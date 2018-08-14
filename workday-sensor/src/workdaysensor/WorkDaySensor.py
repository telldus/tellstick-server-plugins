# -*- coding: utf-8 -*-

from datetime import date, datetime
import time
import pytz
from base import Plugin, Settings, Application
import holidays
from telldus import DeviceManager
from iso3166 import countries

# pylint: disable=E0211,E0213,W0622,W0312
class WorkDaySensor(Plugin):

    def __init__(self):
		self.s = Settings('telldus.scheduler')
		self.timezone = self.s.get('tz', 'UTC')
		Application().registerScheduledTask(self.checkDay, seconds=30, runAtOnce=True)

    def checkDay(self):
        date_time = datetime.now(pytz.timezone(self.timezone))
        try:
            country_holidays = holidays.CountryHoliday(self.countryCode())
        except:
            country_holidays = holidays.CountryHoliday(countries.get(self.countryCode()).alpha3)
        if date(date_time.year, date_time.month, date_time.day) in country_holidays and date_time.hour==00 and date_time.minute==01:
    	    self.deviceAction(2)
        elif date_time.hour==00 and date_time.minute==01:
            self.deviceAction(1)

    def deviceAction(self,action):
        devices = DeviceManager(self.context).retrieveDevices()
        for device in devices:
            if device.protocol() == "dummy":
                device.command(action=action)
        time.sleep(60)

    def countryCode(self):
        for countrycode in pytz.country_timezones:
            timezones = pytz.country_timezones[countrycode]
            for timezone in timezones:
                if timezone == self.timezone:
                    return countrycode
        