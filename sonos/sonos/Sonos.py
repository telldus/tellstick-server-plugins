# -*- coding: utf-8 -*-

from base import Plugin, mainthread
from telldus import DeviceManager, Device
from threading import Thread, Timer
import soco
from requests.exceptions import ConnectionError

class SonosDevice(Device):
	def __init__(self, soco):
		super(SonosDevice,self).__init__()
		self.__soco = soco
		self.setName(soco.player_name)

	def _command(self, action, value, success, failure, **kwargs):
		if action == Device.TURNOFF:
			self.__soco.pause()
		elif action == Device.TURNON:
			self.__soco.play()
		elif action == Device.STOP:
			self.__soco.stop()
		elif action == Device.UP:
			self.__soco.volume += 1
		elif action == Device.DOWN:
			self.__soco.volume -= 1
		else:
			failure(Device.FAILED_STATUS_NO_REPLY)
		success()

	def localId(self):
		return self.__soco.uid

	def methods(self):
		return Device.TURNON | Device.TURNOFF | Device.UP | Device.DOWN | Device.STOP

	def params(self):
		return {
			'ip_address': self.__soco.ip_address
		}

	def soco(self):
		return self.__soco

	def typeString(self):
		return 'sonos'

class Sonos(Plugin):
	def __init__(self):
		Thread(target=self.__scanDevices, name='SonosFinder').start()

	@mainthread
	def __loadCached(self):
		deviceManager = DeviceManager(self.context)
		l = deviceManager.retrieveDevices('sonos')
		if len(l) == 0:
			# No cached, retry search in 10 minutes
			timer = Timer(600, self.__scanDevices)
			timer.daemon = True
			timer.start()
			return
		for dev in l:
			ip = dev.params().get('ip_address', None)
			if ip is None:
				continue
			try:
				s = soco.SoCo(ip)
				s.uid  # Will throw exception if not available
				deviceManager.addDevice(SonosDevice(s))
			except ConnectionError:
				continue

	def __scanDevices(self):
		l = soco.discover()
		if l is None:
			# No found, this could be an error. Don't remove all old. Try to check them manually
			self.__loadCached()
			return
		deviceManager = DeviceManager(self.context)
		for s in l:
			deviceManager.addDevice(SonosDevice(s))
		deviceManager.finishedLoading('sonos')
