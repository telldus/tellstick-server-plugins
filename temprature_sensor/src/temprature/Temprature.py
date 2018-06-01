# -*- coding: utf-8 -*-

from base import Plugin
from telldus import DeviceManager, Sensor
import logging
from threading import Thread
import math
import time

class TempratureSensor(Sensor):
	'''All sensors exported must subclass Sensor

	Minimal function to reimplement is:
	_command
	localId
	typeString
	methods
	'''
	def __init__(self):
		super(TempratureSensor,self).__init__()
		temprature_thread = Thread(target = self.setTemprature, args = (self,))
		temprature_thread.start()

	def _command(self, action, value, success, failure, **kwargs):
		'''This method is called when someone want to control this sensor

		action is the method id to execute. This could be for instance:
		Sensor.TURNON or Sensor.TURNOFF

		value us only used for some actions, for example dim

		This method _must_ call either success or failure
		'''
		logging.debug('Sending command %s to temprature sensor', action)
		success()

	def localId(self):
		'''Return a unique id number for this sensor. The id should not be
		globally unique but only unique for this sensor type.
		'''
		return 2

	def typeString(self):
		'''Return the sensor type. Only one plugin at a time may export sensors using
		the same typestring'''
		return 'temprature'

	def methods(self):
		'''Return a bitset of methods this sensor supports'''
		return Sensor.TURNON | Sensor.TURNOFF

	def setTemprature(self,device):
		"""setTempratureSensor value constantly."""
		while True:
			#This is dummy data for testing sine wave
			for temprature in range(0,101):
				tamprature_in_sine = (((math.sin((temprature * 0.1) + (1/30)) * 100 ) / 2 )+ 100 ) / 2;
					#converting temprature value according to Temprature Birmingham algorithm
				device.setSensorValue(device.TEMPERATURE, tamprature_in_sine, device.SCALE_TEMPERATURE_CELCIUS)
				time.sleep(15)

			for temprature in range(100,0,-1):
				tamprature_in_sine = (((math.sin((temprature * 0.1) + (1/30)) * 100 ) / 2 )+ 100 ) / 2;
					#converting temprature value according to Temprature Birmingham algorithm
				device.setSensorValue(device.TEMPERATURE, tamprature_in_sine, device.SCALE_TEMPERATURE_CELCIUS)
				time.sleep(15)


class Temprature(Plugin):
	'''This is the plugins main entry point and is a singleton
	Manage and load the plugins here
	'''
	def __init__(self):
		# The devicemanager is a globally manager handling all device types
		self.deviceManager = DeviceManager(self.context)

		# Load all devices this plugin handles here. Individual settings for the devices
		# are handled by the devicemanager
		self.deviceManager.addDevice(TempratureSensor())

		# When all devices has been loaded we need to call finishedLoading() to tell
		# the manager we are finished. This clears old devices and caches
		self.deviceManager.finishedLoading('temprature')
