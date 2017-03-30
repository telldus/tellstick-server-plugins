# -*- coding: utf-8 -*-

from base import Plugin, configuration, ConfigurationString
from telldus import DeviceManager, Device
from pylms.server import Server
import logging

class Player(Device):
	def __init__(self, player):
		super(Player,self).__init__()
		self.p = player
		self.setName(player.get_name())
		if player.get_power_state():
			self.setState(Device.TURNON)
		else:
			self.setState(Device.TURNOFF)

	def _command(self, action, value, success, failure, **kwargs):
		if action == Device.TURNON:
			self.p.set_power_state(True)
			self.p.play()
			success()
		elif action == Device.TURNOFF:
			self.p.set_power_state(False)
			success()
		else:
			failure(0)

	def localId(self):
		return self.p.get_ref()

	def typeString(self):
		return 'squeezebox'

	def methods(self):
		return Device.TURNON | Device.TURNOFF

@configuration(
	hostname = ConfigurationString(
		defaultValue='',
		title='IP address',
		description='The ip address to the Squeezebox server',
	)
)
class SqueezeBox(Plugin):
	def __init__(self):
		self.deviceManager = DeviceManager(self.context)
		self.loaded = False
		if self.config('hostname') != '':
			self.setHostname(self.config('hostname'))

	def configWasUpdated(self, key, value):
		if key == 'hostname':
			self.setHostname(value)

	def setHostname(self, hostname):
		if self.loaded:
			logging.warning('Cannot change hostname, without a restart')
			return
		self.sc = Server(hostname=hostname)
		try:
			self.sc.connect()
		except:
			logging.error("Cannot connect to squeezebox server")
			return
		for player in self.sc.players:
			self.deviceManager.addDevice(Player(player))
		self.deviceManager.finishedLoading('squeezebox')
		self.loaded = True
