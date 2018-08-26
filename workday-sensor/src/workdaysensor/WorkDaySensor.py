# -*- coding: utf-8 -*-

from datetime import date, datetime
import time
import pytz
from base import Plugin, Settings, Application
import holidays
from telldus import DeviceManager, Device
from iso3166 import countries
import logging

# pylint: disable=E0211,E0213,W0622,W0312

class DummyDevice(Device):
    	'''All devices exported must subclass Device

	Minimal function to reimplement is:
	_command
	localId
	typeString
	methods
	'''
	def __init__(self):
		super(DummyDevice,self).__init__()

	def _command(self, action, value, success, failure, **kwargs):
		'''This method is called when someone want to control this device

		action is the method id to execute. This could be for instance:
		Device.TURNON or Device.TURNOFF

		value us only used for some actions, for example dim

		This method _must_ call either success or failure
		'''
		logging.debug('Sending command %s to dummy device', action)
		success()

	def localId(self):
		'''Return a unique id number for this device. The id should not be
		globally unique but only unique for this device type.
		'''
		return 1

	def typeString(self):
		'''Return the device type. Only one plugin at a time may export devices using
		the same typestring'''
		return 'dummy'

	def methods(self):
		'''Return a bitset of methods this device supports'''
		return Device.TURNON | Device.TURNOFF

class WorkDaySensor(Plugin):

    def __init__(self):
		self.s = Settings('telldus.scheduler')
		self.timezone = self.s.get('tz', 'UTC')
		self.deviceManager = DeviceManager(self.context)
		self.deviceManager.addDevice(DummyDevice())
		self.deviceManager.finishedLoading('dummy')
		Application().registerScheduledTask(self.checkDay, seconds=30, runAtOnce=True)

    def checkDay(self):
        date_time = datetime.now(pytz.timezone(self.timezone))
        try:
            country_holidays = holidays.CountryHoliday(self.countryCode())
        except self.countryCode() == "":
            pass
        except:
            country_holidays = holidays.CountryHoliday(countries.get(self.countryCode()).alpha3)
        if date(date_time.year, date_time.month, date_time.day) in country_holidays and date_time.hour==00 and date_time.minute==01 and self.countryCode()!="":
    	    self.deviceAction(2)
        elif date_time.hour==00 and date_time.minute==01:
            self.deviceAction(1)

    def deviceAction(self,action):
        device = DeviceManager(self.context)
        print(dir(device))
        DummyDevice().command(action=action)
        time.sleep(60)

    def countryCode(self):
        countr_code=""
        for countrycode in pytz.country_timezones:
            timezones = pytz.country_timezones[countrycode]
            for timezone in timezones:
                if timezone == self.timezone:
                    countr_code = countrycode
        return countr_code
