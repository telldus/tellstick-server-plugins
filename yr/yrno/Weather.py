#!/usr/bin/env python

from base import Application, Plugin
from scheduler.base import Scheduler
from telldus import DeviceManager, Sensor
from threading import Thread
from yr.libyr import Yr
import  logging

class YRSensor(Sensor):
	def __init__(self):
		super(YRSensor,self).__init__()
		self.forecastFrom = None
		self.setName('YR local weather')

	def localId(self):
		return 0

	def params(self):
		return {
			'forecastFrom': self.forecastFrom
		}

	def setParams(self, params):
		self.forecastFrom = params.get('forecastFrom', None)

	def typeString(self):
		return 'yr'

	def updateValues(self, now):
		sensorTypes = {
			'dewpointTemperature': {
				'unit': 'celsius',
				'value': '@value',
				'type': (Sensor.DEW_POINT, Sensor.SCALE_TEMPERATURE_CELCIUS)
			},
			'humidity': {
				'unit': 'percent',
				'value': '@value',
				'type': (Sensor.HUMIDITY, Sensor.SCALE_HUMIDITY_PERCENT)
			},
			'pressure': {
				'unit': 'hPa',
				'value': '@value',
				'type': (Sensor.BAROMETRIC_PRESSURE, Sensor.SCALE_BAROMETRIC_PRESSURE_KPA)
			},
			'temperature': {
				'unit': 'celsius',
				'value': '@value',
				'type': (Sensor.TEMPERATURE, Sensor.SCALE_TEMPERATURE_CELCIUS)
			},
			'windDirection': {
				'value': '@deg',
				'type': (Sensor.WINDDIRECTION, Sensor.SCALE_WIND_DIRECTION)
			},
			'windGust': {
				'value': '@mps',
				'type': (Sensor.WINDGUST, Sensor.SCALE_WIND_VELOCITY_MS)
			},
			'windSpeed': {
				'value': '@mps',
				'type': (Sensor.WINDAVERAGE, Sensor.SCALE_WIND_VELOCITY_MS)
			},
		}
		if self.forecastFrom == now['@from']:
			# Old data
			return
		location = now.get('location', {})
		self.forecastFrom = now['@from']
		for sensorType in sensorTypes:
			if sensorType not in location:
				continue
			value = location[sensorType]
			info = sensorTypes[sensorType]
			if 'unit' in info and value.get('@unit', '') != info['unit']:
				logging.warning("Unit not correct %s!=%s", value.get('@unit', ''), info['unit'])
				continue
			valueType, scale = info['type']
			if info['value'] not in value:
				continue
			sensorValue = value[info['value']]
			if sensorType == 'pressure':
				# We get the report as hPa but report it as kPa
				sensorValue = float(sensorValue)/10.0
			self.setSensorValue(valueType, sensorValue, scale)

class Weather(Plugin):
	def __init__(self):
		self.sensor = YRSensor()
		deviceManager = DeviceManager(self.context)
		deviceManager.addDevice(self.sensor)
		deviceManager.finishedLoading('yr')
		Application().registerScheduledTask(self.__requestWeather, hours=1, runAtOnce=True)

	def __requestWeather(self):
		scheduler = Scheduler(self.context)
		longitude = scheduler.longitude
		latitude = scheduler.latitude
		def doRequest():
			weather = Yr(location_xyz=(longitude, latitude, 1))
			now = weather.now(as_json=False)
			Application().queue(self.sensor.updateValues, now)
		t = Thread(target=doRequest, name='YR weather requester')
		t.daemon = True
		t.start()
