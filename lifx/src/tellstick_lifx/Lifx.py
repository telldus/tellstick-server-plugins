# -*- coding: utf-8 -*-

from base import Plugin, mainthread
from telldus import DeviceManager, Device
from threading import Timer
import lifx
import colorsys

class LifxDevice(Device):
	def __init__(self, light):
		super(LifxDevice,self).__init__()
		self.light = light
		self.setName(light.label)

	def _command(self, action, value, success, failure, **kwargs):
		if action == Device.TURNON:
			self.light.brightness = 1
			self.light.power = True
		elif action == Device.TURNOFF:
			self.light.power = False
		elif action == Device.DIM:
			self.light.brightness = value/255.0
			self.light.power = True
		elif action == Device.RGBW:
			r = (value >> 24) & 0xFF
			g = (value >> 16) & 0xFF
			b = (value >> 8) & 0xFF
			(h, s, l) = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
			self.light.color = lifx.color.modify_color(self.light.color, hue=h*360.0, saturation=s)
			self.light.power = True
		else:
			failure(0)
			return
		success()

	def localId(self):
		return self.light.id

	def typeString(self):
		return 'lifx'

	def methods(self):
		return Device.TURNON | Device.TURNOFF | Device.DIM | Device.RGBW

class Lifx(Plugin):
	def __init__(self):
		self.deviceManager = DeviceManager(self.context)
		self.lifxClient = lifx.Client()
		Timer(2.0, self.discover).start()

	@mainthread
	def discover(self):
		for light in self.lifxClient.get_devices():
			try:
				d = LifxDevice(light)
			except Exception:
				continue
			self.deviceManager.addDevice(d)
		self.deviceManager.finishedLoading('lifx')
