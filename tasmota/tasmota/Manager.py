# -*- coding: utf-8 -*-

import logging
import urllib.parse

import requests

from base import Application, Plugin, configuration, ConfigurationString
from telldus import DeviceManager, Device

_LOGGER = logging.getLogger(__name__)


class TasmotaDevice(Device):
	def __init__(self, ip, mac, endpoint):
		super().__init__()
		self._ip = ip
		self._mac = mac
		self._endpoint = endpoint
		self._sts = {}

	async def _command(self, action, value, **__kwargs):  # pylint: disable=arguments-differ
		commands = []
		if action == Device.TURNON:
			if Device.DIM & self.methods():
				commands.append(('Dimmer', 100))
			commands.append(('Power', '1'))
		elif action == Device.TURNOFF:
			commands.append(('Power', '0'))
		elif action == Device.DIM:
			level = round(value / 2.55)
			commands.append(('Dimmer', level))
		else:
			return False
		for key, value in commands:
			response = TasmotaDevice.doCommand(
			    self.ip, f'{key}{self._endpoint} {value}'
			)
			if not response:
				return False
		return True

	@property
	def endpoint(self):
		return self._endpoint

	@endpoint.setter
	def endpoint(self, endpoint):
		self._endpoint = endpoint

	@property
	def ip(self):  # pylint: disable=invalid-name
		return self._ip

	@ip.setter
	def ip(self, ip):  # pylint: disable=invalid-name
		self._ip = ip

	@property
	def mac(self):
		return self._mac

	@mac.setter
	def mac(self, mac):
		self._mac = mac

	def deviceType(self):
		methods = self.methods()
		if methods & Device.DIM:
			return Device.TYPE_LIGHT
		if methods & Device.TURNON:
			return Device.TYPE_SWITCH_OUTLET
		return Device.TYPE_UNKNOWN

	def localId(self):
		return f"{self._mac}:{self._endpoint}"

	def methods(self):
		methods = 0
		if f'POWER{self._endpoint}' in self._sts:
			methods |= Device.TURNON | Device.TURNOFF
		if f'Dimmer{self._endpoint}' in self._sts:
			methods |= Device.DIM
		return methods

	def updateStatusSTS(self, stsInfo):
		self._sts = stsInfo

	@staticmethod
	def typeString():
		return 'tasmota'

	@staticmethod
	def doCommand(ipAddress, cmd):
		cmd = urllib.parse.quote_plus(cmd)
		# pylint: disable=too-many-function-args
		password = TasmotaManager(Application.defaultContext()).config('password')

		try:
			return requests.get(
			    f'http://{ipAddress}/cm?user=admin&password={password}&cmnd={cmd}'
			).json()
		except Exception:
			return None


@configuration(
    password=ConfigurationString(
        title='Password',
        defaultValue='',
    )
)
class TasmotaManager(Plugin):
	def __init__(self):
		self._devices = {}

	def tearDown(self):
		# pylint: disable=too-many-function-args
		DeviceManager(self.context).removeDevicesByType('tasmota')

	def zeroconfDeviceFound(self, info):
		ipRaw = info.addresses[0]
		ipAddress = f"{ipRaw[0]}.{ipRaw[1]}.{ipRaw[2]}.{ipRaw[3]}"
		deviceInfo = TasmotaDevice.doCommand(ipAddress, "Status 0")
		if not deviceInfo:
			# Could not connect to device
			_LOGGER.warning("Could not connect to tasmota device")
			return
		mac = deviceInfo.get('StatusNET', {}).get('Mac', None)
		if mac in self._devices:
			# Update ip
			self._devices[mac].ip = ipAddress
			return
		status = deviceInfo.get('Status', {})
		names = status.get('FriendlyName')
		for i, name in enumerate(names):
			if len(names) == 1:  # Only one endpoint
				device = TasmotaDevice(ipAddress, mac, '')
			else:
				device = TasmotaDevice(ipAddress, mac, i + 1)
			device.updateStatusSTS(deviceInfo.get('StatusSTS', {}))
			device.setName(name)
			self._devices[mac] = device
			DeviceManager(self.context).addDevice(device)  # pylint: disable=too-many-function-args
