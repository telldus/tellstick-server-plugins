# -*- coding: utf-8 -*-

from base import Application, Plugin
from telldus import DeviceManager, Device
from threading import Thread
import pywemo
import logging

class WeMoDevice(Device):
	def __init__(self, device):
		super(WeMoDevice,self).__init__()
		self.device = device
		self.setName(device.name)

	def localId(self):
		return self.device.serialnumber

	def typeString(self):
		return 'wemo'

class WeMoSwitch(WeMoDevice):
	def __init__(self, device):
		super(WeMoSwitch,self).__init__(device)

	def _command(self, action, value, success, failure, **kwargs):
		if action == Device.TURNON:
			self.device.on()
			success()
		elif action == Device.TURNOFF:
			self.device.off()
			success()
		else:
			failure(0)

	def methods(self):
		return Device.TURNON | Device.TURNOFF

class WeMoLight(Device):
	def __init__(self, light):
		super(WeMoLight,self).__init__()
		self.light = light
		self.setName(light.name)

	def _command(self, action, value, success, failure, **kwargs):
		if action == Device.TURNON:
			self.light.turn_on()
		elif action == Device.TURNOFF:
			self.light.turn_off()
		elif action == Device.DIM:
			self.light.turn_on(value)
		else:
			failure(0)
			return
		success()

	def localId(self):
		return self.light.uniqueID

	def typeString(self):
		return 'wemo'

	def methods(self):
		return Device.TURNON | Device.TURNOFF | Device.DIM

class WeMo(Plugin):
	def __init__(self):
		self.devices = {}
		self.deviceManager = DeviceManager(self.context)
		Thread(target=self.discover).start()

	def addDevice(self, DeviceType, device):
		if device.serialnumber in self.devices:
			return
		d = DeviceType(device)
		self.deviceManager.addDevice(d)
		self.devices[device.serialnumber] = d

	def bridgeFound(self, bridge):
		if bridge.serialnumber in self.devices:
			return
		self.devices[bridge.serialnumber] = bridge
		for light in bridge.Lights:
			d = WeMoLight(bridge.Lights[light])
			self.deviceManager.addDevice(d)

	def discover(self):
		devices = pywemo.discover_devices()
		for device in devices:
			if isinstance(device, pywemo.Bridge):
				Application().queue(self.bridgeFound, device)
			elif isinstance(device, pywemo.Switch):
				Application().queue(self.switchFound, device)
			elif isinstance(device, pywemo.Motion):
				Application().queue(self.motionFound, device)
		Application().queue(self.deviceManager.finishedLoading, 'wemo')

	def motionFound(self, motion):
		logging.info("WeMo motion found: %s", motion)
		# TODO(micke): Implement this when we have a sample

	def switchFound(self, switch):
		self.addDevice(WeMoSwitch, switch)
