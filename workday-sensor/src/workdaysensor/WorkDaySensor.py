# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import pytz

from base import Plugin, Settings, Application, configuration
from scheduler.base import Scheduler
import holidays
from telldus import DeviceManager, Device
from iso3166 import countries
from pluginloader import ConfigurationDropDown

class WorkDay(Device):
	def __init__(self):
		super(WorkDay, self).__init__()
		self.setName("Workday")

	@staticmethod
	def deviceType():
		return Device.TYPE_VIRTUAL

	@staticmethod
	def localId():
		return 1

	@staticmethod
	def typeString():
		return 'workday'

class Country(object):
	def __init__(self):
		settings = Settings('telldus.scheduler')
		self.timezone = settings.get('tz', 'UTC')
		self.country_code = self.countryCode()

	def countryCode(self):
		countr_code = ''
		for countrycode in pytz.country_timezones:
			timezones = pytz.country_timezones[countrycode]
			for timezone in timezones:
				if timezone == self.timezone:
					countr_code = countrycode
		return countr_code

	def getCountry(self):
		return countries.get(self.country_code).name

@configuration(
	country=ConfigurationDropDown(
		title='Country',
		defaultValue='auto',
		options={
			'auto': '- Use country from timezone -',
			'AR': 'Argentina',
			'AU': 'Australia',
			'AT': 'Austria',
			'BY': 'Belarus',
			'BE': 'Belgium',
			'BA': 'Canada',
			'CO': 'Colombia',
			'CZ': 'Czech',
			'DK': 'Denmark',
			'FI': 'Finland',
			'FRA': 'France',
			'DE': 'Germany',
			'HU': 'Hungary',
			'IND': 'India',
			'IE': 'Ireland',
			'IT': 'Italy',
			'JP': 'Japan',
			'MX': 'Mexico',
			'NL': 'Netherlands',
			'NZ': 'New Zealand',
			'NO': 'Norway',
			'PL': 'Poland',
			'PT': 'Portugal',
			'PTE': 'Portugal plus extended days most people have off',
			'SI': 'Slovenia',
			'SK': 'Slovakia',
			'ZA': 'South Africa',
			'ES': 'Spain',
			'SE': 'Sweden',
			'CH': 'Switzerland',
			'UK': 'United Kingdom',
			'US': 'United States',
		},
	)
)
class WorkDaySensor(Plugin):
	def __init__(self):
		self.lastCheckedDate = None
		self.device = WorkDay()
		deviceManager = DeviceManager(self.context)
		deviceManager.addDevice(self.device)
		deviceManager.finishedLoading('workday')
		Application().registerScheduledTask(self.checkDay, minutes=1, runAtOnce=False)

	def checkDay(self):
		scheduler = Scheduler(self.context)
		today = datetime.now(pytz.timezone(scheduler.timezone)).date()
		if self.lastCheckedDate == today:
			# Check today has already been performed
			return
		self.lastCheckedDate = today

		country = self.config('country')
		try:
			countryHolidays = holidays.CountryHoliday(country)
		except Exception as __error:
			return

		if today in countryHolidays:
			self.device.setState(
				Device.TURNOFF,
				origin=countryHolidays[today],
				onlyUpdateIfChanged=True
			)
		else:
			self.device.setState(Device.TURNON, onlyUpdateIfChanged=True)

