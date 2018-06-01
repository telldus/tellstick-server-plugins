# -*- coding: utf-8 -*-

import math
import logging
from threading import Thread
import time

from base import Plugin
from telldus import DeviceManager, Sensor

class TemperatureSensor(Sensor):
	'''All sensors exported must subclass Sensor

	Minimal function to reimplement is:
	_command
	localId
	typeString
	methods
	'''
	def __init__(self):
		super(TemperatureSensor, self).__init__()
		temperature_thread = Thread(target=TemperatureSensor.setTemperature, args=(self,))
		temperature_thread.start()

	@staticmethod
	def _command(action, value, success, failure, **__kwargs):
		'''This method is called when someone want to control this sensor

		action is the method id to execute. This could be for instance:
		Sensor.TURNON or Sensor.TURNOFF

		value us only used for some actions, for example dim

		This method _must_ call either success or failure
		'''
		del value
		del failure
		logging.debug('Sending command %s to temperature sensor', action)
		success()

	@staticmethod
	def localId():
		'''Return a unique id number for this sensor. The id should not be
		globally unique but only unique for this sensor type.
		'''
		return 2

	@staticmethod
	def typeString():
		'''Return the sensor type. Only one plugin at a time may export sensors using
		the same typestring'''
		return 'temperature'

	@staticmethod
	def methods():
		'''Return a bitset of methods this sensor supports'''
		return Sensor.TURNON | Sensor.TURNOFF

	@staticmethod
	def setTemperature(device):
		"""setTemperatureSensor value constantly."""
		while True:
			#This is dummy data for testing sine wave
			for temperature in range(0, 101):
				tamprature_in_sine = (((math.sin((temperature * 0.1) + (1/30)) * 100) / 2) + 100) / 2
					#converting temperature value according to Temperature Birmingham algorithm
				device.setSensorValue(device.TEMPERATURE, tamprature_in_sine, device.SCALE_TEMPERATURE_CELCIUS)
				time.sleep(15)

			for temperature in range(100, 0, -1):
				tamprature_in_sine = (((math.sin((temperature * 0.1) + (1/30)) * 100) / 2) + 100) / 2
					#converting temperature value according to Temperature Birmingham algorithm
				device.setSensorValue(device.TEMPERATURE, tamprature_in_sine, device.SCALE_TEMPERATURE_CELCIUS)
				time.sleep(15)

# pylint: disable=R0903
class Temperature(Plugin):
	'''This is the plugins main entry point and is a singleton
	Manage and load the plugins here
	'''
	def __init__(self):
		# The devicemanager is a globally manager handling all device types
		self.deviceManager = DeviceManager(self.context)

		# Load all devices this plugin handles here. Individual settings for the devices
		# are handled by the devicemanager
		self.deviceManager.addDevice(TemperatureSensor())

		# When all devices has been loaded we need to call finishedLoading() to tell
		# the manager we are finished. This clears old devices and caches
		self.deviceManager.finishedLoading('temperature')
