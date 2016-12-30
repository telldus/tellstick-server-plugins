# -*- coding: utf-8 -*-

from base import Application, Plugin, ConfigurationString, configuration
from telldus import DeviceManager, Sensor
from urllib2 import HTTPError
import eliqonline
import logging

class EliqSensor(Sensor):
	def __init__(self, channelId):
		super(EliqSensor,self).__init__()
		self.channelId = channelId
		self.setName('Eliq')

	def localId(self):
		return self.channelId

	def model(self):
		return 'eliq'

	def typeString(self):
		return 'eliq'

@configuration(
	accessToken = ConfigurationString(
		defaultValue='',
		title='Access token',
		description='Genererate an access token in the Eliq online portal',
		minLength=32,
		maxLength=32
	)
)
class Eliq(Plugin):
	def __init__(self):
		self.deviceManager = DeviceManager(self.context)
		self.sensor = None
		Application().registerScheduledTask(self.__requestNewValue, minutes=1, runAtOnce=True)

	def __requestNewValue(self):
		accessToken = self.config('accessToken')
		if accessToken == '':
			return
		try:
			eliq = eliqonline.API(accessToken)
			data_now = eliq.get_data_now()
		except HTTPError as e:
			# Something wrong with our request apparantly
			logging.error('Could not request Eliq value %s', e)
			return
		if self.sensor is None:
			self.sensor = EliqSensor(data_now.channelid)
			self.sensor.setSensorValue(Sensor.WATT, data_now.power, Sensor.SCALE_POWER_WATT)
			self.deviceManager.addDevice(self.sensor)
			self.deviceManager.finishedLoading('eliq')
		else:
			self.sensor.setSensorValue(Sensor.WATT, data_now.power, Sensor.SCALE_POWER_WATT)
