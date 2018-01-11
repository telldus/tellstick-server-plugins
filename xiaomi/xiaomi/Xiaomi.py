# -*- coding: utf-8 -*-

import binascii
import json
import logging
import struct
from threading import Thread

from PyXiaomiGateway import PyXiaomiGateway
from base import \
	configuration, \
	ConfigurationNumber, \
	ConfigurationString, \
	Application, \
	Plugin, \
	mainthread
from telldus import DeviceManager, Device

__name__ = 'Xiaomi'  # pylint: disable=W0622

class XiaomiDevice(Device):
	def __init__(self, data, gateway):
		super(XiaomiDevice, self).__init__()
		self.lastChanged = None
		self._sid = data.get('sid')
		self.__model = data.get('model', 'unknown')
		self.__features = data.get('features', [])
		self._gateway = gateway
		self.__argb = (0, 0, 0, 0)
		self.__battery = 254
		self.setName(self.__model)

	def _command(self, action, value, success, failure, **__kwargs):
		kwargs = None
		if action == Device.TURNON:
			if 'switch' in self.__features:
				kwargs = {'status': 'on'}
			elif 'light' in self.__features:
				argb = list(self.__argb)
				argb[0] = 100
				kwargs = {'rgb': XiaomiDevice.argbToInt(argb)}
		elif action == Device.TURNOFF:
			if 'switch' in self.__features:
				kwargs = {'status': 'off'}
			elif 'light' in self.__features:
				argb = list(self.__argb)
				argb[0] = 0
				kwargs = {'rgb': XiaomiDevice.argbToInt(argb)}
		elif action == Device.DIM:
			argb = list(self.__argb)
			argb[0] = int(value/255.0*100)
			kwargs = {'rgb': XiaomiDevice.argbToInt(argb)}
		elif action == Device.RGB:
			argb = list(self.__argb)
			argb[1] = (value >> 16) & 0xFF
			argb[2] = (value >> 8) & 0xFF
			argb[3] = value & 0xFF
			kwargs = {'rgb': XiaomiDevice.argbToInt(argb)}
		else:
			failure(Device.FAILED_STATUS_UNKNOWN)
			return
		if kwargs is None:
			failure(Device.FAILED_STATUS_UNKNOWN)
			return
		if self._gateway.write_to_hub(self._sid, **kwargs):
			success()
			return
		failure(Device.FAILED_STATUS_UNKNOWN)

	def battery(self):
		return self.__battery

	def localId(self):
		return self._sid

	def methods(self):
		methods = 0
		if 'switch' in self.__features:
			methods = methods | Device.TURNON | Device.TURNOFF
		if 'light' in self.__features:
			methods = methods | Device.TURNON | Device.TURNOFF | Device.DIM | Device.RGB
		return methods

	def model(self):
		return self.__model

	def isDevice(self):
		types = ['binary_sensor', 'switch', 'light', 'cover']
		for deviceType in types:
			if deviceType in self.__features:
				return True
		return False

	def isSensor(self):
		if self.__model == 'plug':
			# Should we check for the feature "switch" here?
			# Does all switches support energy metering?
			return True
		return 'sensor' in self.__features

	@staticmethod
	def typeString():
		return 'xiaomi_aqara'

	def __parseStatus(self, data, heartbeat):
		if 'load_power' in data:
			self.setSensorValue(Device.WATT, float(data['load_power']),
				Device.SCALE_POWER_WATT
			)
		if 'power_consumed' in data:
			self.setSensorValue(Device.WATT, float(data['power_consumed']),
				Device.SCALE_POWER_KWH
			)
		newState = data['status']
		states = {
			'click': Device.TURNON,
			'double_click': Device.TURNOFF,
			'motion': Device.TURNON,
			'on': Device.TURNON,
			'off': Device.TURNOFF,
			'open': Device.TURNON,
			'close': Device.TURNOFF,
		}
		if newState not in states:
			logging.warning('Unknown Xiaomi state: %s', newState)
			return
		if heartbeat:
			# If this is a heartbeat we check the current state to not trigger events by mistake
			state, __stateValue = self.state()
			if state == states[newState]:
				return
		self.setState(states[newState])

	def update(self, data, heartbeat):
		if 'status' in data:
			self.__parseStatus(data, heartbeat)
		if 'rgb' in data:
			# Convert int to argb
			hexstr = "%x" % data['rgb']
			hexstr = '0' * (8-len(hexstr)) + hexstr # Pad to 8 characters
			self.__argb = struct.unpack('BBBB', bytearray.fromhex(hexstr))
		if 'no_close' in data:
			# This is reported regularly while a magnet is open.
			# We use this as an extra failsafe to ensure the correct status is set.
			# But we cannot just simply call Device::setState() every time since this would trigger
			# events. so first compare to see if the recorded state has changed
			state, __stateValue = self.state()
			if state != Device.TURNON:
				self.setState(Device.TURNON)
		if 'no_motion' in data:
			state, __stateValue = self.state()
			if state != Device.TURNOFF:
				self.setState(Device.TURNOFF)
		if 'temperature' in data:
			self.setSensorValue(Device.TEMPERATURE, float(data['temperature'])/100.0,
				Device.SCALE_TEMPERATURE_CELCIUS
			)
		if 'humidity' in data:
			self.setSensorValue(Device.HUMIDITY, float(data['humidity'])/100.0,
				Device.SCALE_HUMIDITY_PERCENT
			)
		if 'illumination' in data:
			# Home Assistnat substracts 300 from the value. Not sure why?
			# We do not support LM yet...
			#self.setSensorValue(Device.LUMINANCE, max(int(data['illumination'])-300, 0),
			#	Device.SCALE_LUMINANCE_LM
			#)
			pass
		if 'voltage' in data:
			# Are these correct? Same for all products?
			maxVoltage = 3000
			minVoltage = 2000
			voltage = max(min(data['voltage'], maxVoltage), minVoltage)
			percent = (((float(voltage) - minVoltage) / (maxVoltage - minVoltage)) * 100)
			self.__battery = int(round(percent, 0))

	@staticmethod
	def argbToInt(argb):
		return int(binascii.hexlify(struct.pack('BBBB', *argb)).decode("ASCII"), 16)

class XiaomiGateway(XiaomiDevice):
	def __init__(self, data, gateway, doorbell):
		super(XiaomiGateway, self).__init__(data, gateway)
		self.doorbell = doorbell

	def _command(self, action, value, success, failure, **kwargs):
		if action != Device.BELL:
			return super(XiaomiGateway, self)._command(action, value, success, failure, **kwargs)
		kwargs = {'mid': int(self.doorbell)}
		if self._gateway.write_to_hub(self._sid, **kwargs):
			success()
			return
		failure(Device.FAILED_STATUS_UNKNOWN)

	def methods(self):
		return super(XiaomiGateway, self).methods() | Device.BELL

@configuration(
	host=ConfigurationString(
		defaultValue='',
		title='IP address',
	),
	port=ConfigurationNumber(
		defaultValue='9898 ',
		title='Port',
	),
	sid=ConfigurationString(
		defaultValue='',
		title='Sid',
	),
	key=ConfigurationString(
		defaultValue='',
		title='Key',
	),
	doorbell=ConfigurationNumber(
		defaultValue='10',
		title='Doorbell sound number',
	),
)
class Gateway(Plugin):
	def __init__(self):
		gatewaycfg = {}
		if self.config('host') != '':
			gatewaycfg['host'] = self.config('host')
			gatewaycfg['port'] = self.config('port')
			gatewaycfg['sid'] = self.config('sid')
			gatewaycfg['key'] = self.config('key')
		self.xiaomi = PyXiaomiGateway(self.__pyXiaomiGatewayCallback, {}, 'any')
		self.gateway = None
		self.devices = {}
		Application().registerShutdown(self.shutdown)
		Thread(name='Xiaomi Discovery', target=self.__discovery).start()

	def __addUpdateDevice(self, device):
		sid = device.get('sid', None)
		if sid is None:
			return
		if sid not in self.devices:
			if device.get('model') == 'gateway':
				self.devices[sid] = XiaomiGateway(device, self.gateway, self.config('doorbell'))
			else:
				self.devices[sid] = XiaomiDevice(device, self.gateway)
			deviceManager = DeviceManager(self.context)
			deviceManager.addDevice(self.devices[sid])
		self.devices[sid].update(device.get('data', {}), True)

	def __discovery(self):
		self.xiaomi.discover_gateways()
		for ipAddr in self.xiaomi.gateways:
			self.gateway = self.xiaomi.gateways[ipAddr]
			self.gateway.key = self.config('key')
			break  # Only support one gw
		else:
			return
		# We need to flatten the devices since the library sorts this by function and one device
		# may be in the list more than once
		devices = {}
		for deviceType in self.gateway.devices:
			for device in self.gateway.devices[deviceType]:
				sid = device['sid']
				if sid not in devices:
					devices[sid] = device
				devices[sid].setdefault('features', []).append(deviceType)
		for sid in devices:
			self.__addUpdateDevice(devices[sid])
		deviceManager = DeviceManager(self.context)
		deviceManager.finishedLoading('xiaomi_aqara')
		self.xiaomi.listen()  # Start listen for events

	@mainthread
	def __pyXiaomiGatewayCallback(self, __pushData, data):
		cmd = data.get('cmd', '')
		if cmd not in ['report', 'heartbeat']:
			logging.info('Received unknown cmd from Xiaomi GW: %s', data.get('cmd'))
			return
		sid = data.get('sid', None)
		if sid not in self.devices:
			return
		params = json.loads(data.get('data', '{}'))
		self.devices[sid].update(params, cmd == 'heartbeat')

	def configWasUpdated(self, key, value):
		if key == 'doorbell':
			for sid in self.devices:
				if self.devices[sid].model() == 'gateway':
					self.devices[sid].doorbell = value
		if key == 'key' and self.gateway:
			self.gateway.key = value

	def shutdown(self):
		self.xiaomi.stop_listen()

	def tearDown(self):
		deviceManager = DeviceManager(self.context)
		deviceManager.removeDevicesByType('xiaomi_aqara')
