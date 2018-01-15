# -*- coding: utf-8 -*-

import colorsys
from threading import Timer

from base import Plugin, mainthread
from telldus import DeviceManager, Device
import lifx

class LifxDevice(Device):
	def __init__(self, light):
		super(LifxDevice, self).__init__()
		self.light = light
		self.setName(light.label)

	def _command(self, action, value, success, failure, **__kwargs):
		if action == Device.TURNON:
			self.light.brightness = 1
			self.light.power = True
		elif action == Device.TURNOFF:
			self.light.power = False
		elif action == Device.DIM:
			self.light.brightness = value/255.0
			self.light.power = True
		elif action == Device.RGB:
			red = (value >> 16) & 0xFF
			green = (value >> 8) & 0xFF
			blue = value & 0xFF
			(hue, saturation, __l) = colorsys.rgb_to_hsv(red/255.0, green/255.0, blue/255.0)
			self.light.color = lifx.color.modify_color(
				self.light.color,
				hue=hue*360.0,
				saturation=saturation
			)
		else:
			failure(0)
			return
		success()

	def localId(self):
		return self.light.id

	@staticmethod
	def typeString():
		return 'lifx'

	@staticmethod
	def methods():
		return Device.TURNON | Device.TURNOFF | Device.DIM | Device.RGB

class Lifx(Plugin):  # pylint: disable=R0903
	def __init__(self):
		self.lifxClient = lifx.Client()
		Timer(2.0, self.discover).start()

	@mainthread
	def discover(self):
		deviceManager = DeviceManager(self.context)
		for light in self.lifxClient.get_devices():
			try:
				device = LifxDevice(light)
			except Exception:
				continue
			deviceManager.addDevice(device)
		deviceManager.finishedLoading('lifx')

	def tearDown(self):
		deviceManager = DeviceManager(self.context)
		deviceManager.removeDevicesByType('lifx')
