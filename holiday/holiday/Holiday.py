# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import pytz

from base import Plugin, Application, configuration, ConfigurationBool
from scheduler.base import Scheduler
from telldus import DeviceManager, Device
from pluginloader import ConfigurationDropDown

import holidays

class HolidayDevice(Device):
	def __init__(self):
		super(HolidayDevice, self).__init__()
		self.setName("Holiday")

	@staticmethod
	def deviceType():
		return Device.TYPE_VIRTUAL

	@staticmethod
	def localId():
		return 1

	@staticmethod
	def typeString():
		return 'holiday'

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
class Holiday(Plugin):
	def __init__(self):
		self.lastCheckedDate = None
		self.device = HolidayDevice()
		deviceManager = DeviceManager(self.context)
		deviceManager.addDevice(self.device)
		deviceManager.finishedLoading('holiday')
		Application().registerScheduledTask(self.checkDay, minutes=1, runAtOnce=False)

	def checkDay(self):
		scheduler = Scheduler(self.context)
		now = datetime.now(pytz.timezone(scheduler.timezone))
		today = now.date()
		if self.lastCheckedDate == today:
			# Check today has already been performed
			return
		self.lastCheckedDate = today

		isHoliday, reason = self.runCheck(now)
		if isHoliday:
			self.device.setState(Device.TURNON, origin=reason, onlyUpdateIfChanged=True)
		else:
			self.device.setState(Device.TURNOFF, origin=reason, onlyUpdateIfChanged=True)

	def runCheck(self, now):
		country = self.config('country')
		try:
			countryHolidays = holidays.CountryHoliday(country)
		except Exception as __error:
			return False, 'Unknown country'

		today = now.date()
		if today in countryHolidays:
			return True, countryHolidays[today]
		return False, weekdays[now.weekday()]

	def tearDown(self):
		DeviceManager(self.context).removeDevicesByType('holiday')
