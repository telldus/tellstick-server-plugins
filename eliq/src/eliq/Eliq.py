# -*- coding: utf-8 -*-

from base import Application, Plugin, Settings, implements
from web.base import IWebRequestHandler
from telldus import DeviceManager, Sensor
from pkg_resources import resource_filename
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

class Eliq(Plugin):
	implements(IWebRequestHandler)

	def __init__(self):
		self.deviceManager = DeviceManager(self.context)
		self.sensor = None
		s = Settings('eliq')
		self.accessToken = s.get('accessToken', '')
		Application().registerScheduledTask(self.__requestNewValue, minutes=1, runAtOnce=True)

	def __requestNewValue(self):
		if self.accessToken == '':
			return
		try:
			eliq = eliqonline.API(self.accessToken)
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

	def getTemplatesDirs(self):
		return [resource_filename('eliq', 'templates')]

	def matchRequest(self, plugin, path):
		if plugin != 'eliq':
			return False
		if path in ['']:
			return True
		return False

	def handleRequest(self, plugin, path, params, request, **kwargs):
		if request.method() == 'POST':
			self.accessToken = request.post('accessToken', '')
			s = Settings('eliq')
			s['accessToken'] = self.accessToken
			Application().queue(self.__requestNewValue)
		return 'eliq.html', {'accessToken': self.accessToken}
