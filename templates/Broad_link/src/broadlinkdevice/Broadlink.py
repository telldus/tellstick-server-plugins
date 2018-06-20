# -*- coding: utf-8 -*-

from base import Plugin
from telldus import DeviceManager, Device
import logging
import broadlink
import codecs

class BroadDevice(Device):
	'''All devices exported must subclass Device

	Minimal function to reimplement is:
	_command
	localId
	typeString
	methods
	'''
	def __init__(self):
		super(BroadDevice,self).__init__()
		self.devices = broadlink.discover(timeout=5)
		self.device=None
		for d in self.devices:
			bytearray.reverse(d.mac)
			macAddr = codecs.encode(d.mac, 'hex_codec')
			if(macAddr=="34ea349133ea"):
				d.auth()
				self.device = d

	def _command(self, action, value, success, failure, **kwargs):
		'''This method is called when someone want to control this device

		action is the method id to execute. This could be for instance:
		Device.TURNON or Device.TURNOFF

		value us only used for some actions, for example dim

		This method _must_ call either success or failure
		'''
		logging.debug('Sending command %s to Broadlink device', action)
		if action == 1:
			self.device.set_power(1)
		else:
			self.device.set_power(0)
		success()

	def localId(self):
		'''Return a unique id number for this device. The id should not be
		globally unique but only unique for this device type.
		'''
		return 8

	def typeString(self):
		'''Return the device type. Only one plugin at a time may export devices using
		the same typestring'''
		return 'broad'

	def methods(self):
		'''Return a bitset of methods this device supports'''
		return Device.TURNON | Device.TURNOFF

class Broadlink(Plugin):
	'''This is the plugins main entry point and is a singleton
	Manage and load the plugins here
	'''
	def __init__(self):
		# The devicemanager is a globally manager handling all device types
		self.deviceManager = DeviceManager(self.context)

		# Load all devices this plugin handles here. Individual settings for the devices
		# are handled by the devicemanager
		self.deviceManager.addDevice(BroadDevice())

		# When all devices has been loaded we need to call finishedLoading() to tell
		# the manager we are finished. This clears old devices and caches
		self.deviceManager.finishedLoading('broad')
