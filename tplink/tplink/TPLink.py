# -*- coding: utf-8 -*-

from base import Plugin
from telldus import DeviceManager, Device
from pyHS100 import TPLinkSmartHomeProtocol, SmartPlug
from threading import Thread
import logging

class TPLinkDevice(Device):

	def __init__(self, plug):
		super(TPLinkDevice,self).__init__()
		self.plug = plug
		self.sysinfo = plug.get_sysinfo()
		self.setName(self.sysinfo['alias'])

	def _command(self, action, value, success, failure, **kwargs):
		if action == Device.TURNON:
			try:
				self.plug.turn_on()
			except:
				failure(Device.FAILED_STATUS_TIMEDOUT)
		elif action == Device.TURNOFF:
			try:
				self.plug.turn_off()
			except:
				failure(Device.FAILED_STATUS_TIMEDOUT)
		else:
			failure(0)
			return
		success()

	def localId(self):
		return self.sysinfo['deviceId']

	def typeString(self):
		return 'tplink'

	def methods(self):
		return Device.TURNON | Device.TURNOFF

class TPLink(Plugin):
	def __init__(self):
		t = Thread(target=self.loadDevices, name='TP-Link device discovery')
		t.start()

	def loadDevices(self):
		deviceManager = DeviceManager(self.context)
		for dev in TPLinkSmartHomeProtocol.discover():
			plug = SmartPlug(dev['ip'])
			deviceManager.addDevice(TPLinkDevice(plug))
		deviceManager.finishedLoading('tplink')
	
