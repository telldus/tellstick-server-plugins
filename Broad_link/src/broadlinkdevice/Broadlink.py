# -*- coding: utf-8 -*-

from threading import Thread
import logging
import codecs
import broadlink
from base import Plugin, Application
from telldus import DeviceManager, Device

class BroadDevice(Device):
	def __init__(self, device):
		super(BroadDevice, self).__init__()
		self.device = device
		self.device.auth()
		self._uniqueId = codecs.encode(device.mac, "hex_codec")

	def _command(self, action, value, success, failure, **kwargs):
		logging.debug('Sending command %s to Broadlink device', action)
		if action == Device.TURNON:
			self.device.set_power(1)
		elif action == Device.TURNOFF:
			self.device.set_power(0)
		else:
			failure(0)
			return
		success()

	def localId(self):
		return self._uniqueId

	def typeString(self):
		return 'broadlink'

	def methods(self):
		return Device.TURNON | Device.TURNOFF

	def isSensor(self):
		return True

	def updateValue(self):
		self.setSensorValue(Device.WATT, float(self.device.get_energy()),
			Device.SCALE_POWER_WATT
		)

class Broadlink(Plugin):
	def __init__(self):
		self.deviceManager = DeviceManager(self.context)
		self.devices = None
		t = Thread(target=self.detectBroadlink, name="Detect Broadlink Devices")
		t.start()

	def updateValues(self):
		for device in self.deviceManager.retrieveDevices("broadlink"):
			if(device.isDevice()):
    				device.updateValue()

	def detectBroadlink(self):
		self.devices = broadlink.discover(timeout=5)
		print(self.devices)
		for device in self.devices:
			self.deviceManager.addDevice(BroadDevice(device))
		self.deviceManager.finishedLoading('broadlink')
		Application().registerScheduledTask(self.updateValues, seconds=300, runAtOnce=True)
