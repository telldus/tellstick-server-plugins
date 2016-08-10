# -*- coding: utf-8 -*-

from base import Plugin, mainthread
from telldus import DeviceManager, Device
from threading import Timer
import lifx

class LifxDevice(Device):
	def __init__(self, light):
		super(LifxDevice,self).__init__()
		self.light = light
		self.setName(light.label)

	def _command(self, action, value, success, failure, **kwargs):
		if action == Device.TURNON:
			self.light.power = True
			self.light.brightness = 1
		elif action == Device.TURNOFF:
			self.light.power = False
		elif action == Device.DIM:
			self.light.power = True
			self.light.brightness = value/255.0
		else:
			failure(0)
			return
		success()

	def localId(self):
		return self.light.id

	def typeString(self):
		return 'lifx'

	def methods(self):
		return Device.TURNON | Device.TURNOFF | Device.DIM

class Lifx(Plugin):
	def __init__(self):
		self.deviceManager = DeviceManager(self.context)
		self.lifxClient = lifx.Client()
		Timer(2.0, self.discover).start()

	@mainthread
	def discover(self):
		for light in self.lifxClient.get_devices():
			d = LifxDevice(light)
			self.deviceManager.addDevice(d)
		self.deviceManager.finishedLoading('lifx')
