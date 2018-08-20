# -*- coding: utf-8 -*-

import logging
import codecs
import broadlink

from base import Plugin
from telldus import DeviceManager, Device
from threading import Thread

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

class Broadlink(Plugin):
	def __init__(self):
		self.deviceManager = DeviceManager(self.context)
		self.devices = None
		t = Thread(target=self.detectBroadlink, name="Detect Broadlink Devices")
		t.start()

	def detectBroadlink(self):
		self.devices = broadlink.discover(timeout=5)
		print(self.devices)
		for device in self.devices:
			self.deviceManager.addDevice(BroadDevice(device))
		self.deviceManager.finishedLoading('broadlink')
