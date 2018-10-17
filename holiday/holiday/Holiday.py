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
	),
	monday=ConfigurationBool(
		defaultValue=False,
		sortOrder=1,
		title='Is monday a holiday?'
	),
	tuesday=ConfigurationBool(
		defaultValue=False,
		sortOrder=2,
		title='Is tuesday a holiday?'
	),
	wednesday=ConfigurationBool(
		defaultValue=False,
		sortOrder=3,
		title='Is wednesday a holiday?'
	),
	thursday=ConfigurationBool(
		defaultValue=False,
		sortOrder=4,
		title='Is thursday a holiday?'
	),
	friday=ConfigurationBool(
		defaultValue=False,
		sortOrder=5,
		title='Is friday a holiday?'
	),
	saturday=ConfigurationBool(
		defaultValue=True,
		sortOrder=6,
		title='Is saturday a holiday?'
	),
	sunday=ConfigurationBool(
		defaultValue=True,
		sortOrder=7,
		title='Is sunday a holiday?'
	),
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

	def configWasUpdated(self, __key, __value):
		# Retrigger new check
		self.lastCheckedDate = None

	def runCheck(self, now):
		# Check configurations for weekdays first.
		weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
		try:
			localHoliday = self.config(weekdays[now.weekday()])
			if localHoliday:
				return True, weekdays[now.weekday()]
		except Exception as error:
			# This should not happen. Just extra precaution
			Application.printException(error)

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
