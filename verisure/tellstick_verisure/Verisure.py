# -*- coding: utf-8 -*-

from base import Application, Plugin, mainthread, configuration, ConfigurationString, signal
from telldus import DeviceManager, Device
from threading import Thread, Timer
import verisure
from requests.exceptions import ConnectionError
import logging

__name__ = 'Verisure'

class VerisureDevice(Device):
	def __init__(self):
		super(VerisureDevice,self).__init__()
		self.lastChanged = None

	def _command(self, action, value, failure, **kwargs):
		failure(Device.FAILED_STATUS_NOT_CONFIRMED)

	def methods(self):
		return 0

	def params(self):
		return {
			'lastChanged': self.lastChanged
		}

	def setParams(self, params):
		self.lastChanged = params.get('lastChanged', None)

	def typeString(self):
		return 'verisure'

class AlarmDevice(VerisureDevice):
	def __init__(self):
		super(AlarmDevice,self).__init__()
		self.setName('Verisure Alarm')

	def localId(self):
		return 0

	def updateStatus(self, armstate):
		if armstate['date'] == self.lastChanged:
			return False
		newStatus = armstate['statusType']
		states = {
			'ARMED_AWAY': (Device.TURNON, None),
			'ARMED_HOME': (Device.DIM, 127),
			'DISARMED': (Device.TURNOFF, None),
		}
		if newStatus not in states:
			logging.warning("Unknown state %s", newStatus)
			return False
		state, stateValue = self.state()
		newState, newStateValue = states[newStatus]
		self.lastChanged = armstate['date']
		self.setState(newState, newStateValue, origin='%s by %s' % (armstate['name'], armstate['changedVia'].lower()))
		return True

class DoorWindowDevice(VerisureDevice):
	def __init__(self, info):
		super(DoorWindowDevice,self).__init__()
		self.info = info
		self.setName(info['area'])

	def localId(self):
		return self.info['deviceLabel']

	def updateStatus(self, info):
		if info['reportTime'] == self.lastChanged:
			return
		newStatus = info['state']
		states = {
			'OPEN': Device.TURNON,
			'CLOSE': Device.TURNOFF,
		}
		if newStatus not in states:
			logging.warning("Unknown state %s", newStatus)
			return
		state, stateValue = self.state()
		self.lastChanged = info['reportTime']
		self.setState(states[newStatus])

class ClimateDevice(VerisureDevice):
	def __init__(self, info):
		super(ClimateDevice,self).__init__()
		self.info = info
		self.setName(info['deviceArea'])

	def localId(self):
		return self.info['deviceLabel']

	def isDevice(self):
		return False

	def isSensor(self):
		return True

	def model(self):
		return self.info['deviceType'].lower()

	def updateValues(self, newValues):
		if newValues['time'] == self.lastChanged:
			return
		self.lastChanged = newValues['time']
		if 'temperature' in newValues:
			self.setSensorValue(Device.TEMPERATURE, newValues['temperature'], Device.SCALE_TEMPERATURE_CELCIUS)
		if 'humidity' in newValues:
			self.setSensorValue(Device.HUMIDITY, newValues['humidity'], Device.SCALE_HUMIDITY_PERCENT)

class SmartPlugDevice(VerisureDevice):
	def __init__(self, info, manager):
		super(SmartPlugDevice,self).__init__()
		self.info = info
		self.manager = manager
		self.setName(info['area'])

	def _command(self, action, value, success, failure, **kwargs):
		if action == Device.TURNON:
			self.manager.setSmartplugState(self.info['deviceLabel'], True)
			success()
			return
		if action == Device.TURNOFF:
			self.manager.setSmartplugState(self.info['deviceLabel'], False)
			success()
			return
		failure(Device.FAILED_STATUS_NOT_CONFIRMED)

	def localId(self):
		return self.info['deviceLabel']

	def methods(self):
		return Device.TURNON | Device.TURNOFF

	def updateValues(self, info):
		newStatus = info['currentState']
		states = {
			'ON': Device.TURNON,
			'OFF': Device.TURNOFF,
			'UNKNOWN': Device.TURNOFF,
		}
		if newStatus not in states:
			logging.warning("Unknown state %s", newStatus)
			return
		state, stateValue = self.state()
		if state == states[newStatus]:
			return
		self.setState(states[newStatus])

class DoorLockDevice(VerisureDevice):
	def __init__(self, info):
		super(DoorLockDevice,self).__init__()
		self.info = info
		self.setName(info['area'])

	def localId(self):
		return self.info['deviceLabel']

	def updateStatus(self, info):
		if info['eventTime'] == self.lastChanged:
			return
		newStatus = info['currentLockState']
		states = {
			'LOCKED': Device.TURNON,
			'UNLOCKED': Device.TURNOFF,
		}
		if newStatus not in states:
			logging.warning("Unknown state %s", newStatus)
			return
		state, stateValue = self.state()
		self.lastChanged = info['eventTime']
		self.setState(states[newStatus], origin='%s by %s' % (info.get('userString', 'unknown'), info['method'].lower()))
		return True

@configuration(
	username = ConfigurationString(
		defaultValue='',
		title='Username',
	),
	password = ConfigurationString(
		defaultValue='',
		title='Password',
	),
)
class Alarm(Plugin):
	def __init__(self):
		self.loaded = False
		self.armState = None
		self.alarmDevice = AlarmDevice()
		deviceManager = DeviceManager(self.context)
		deviceManager.addDevice(self.alarmDevice)
		self.devices = {}
		Application().registerScheduledTask(fn=self.__fetch, minutes=10, runAtOnce=True)

	def isArmed(self):
		return self.armState == 'ARMED_AWAY'

	def isArmedHome(self):
		return self.armState == 'ARMED_HOME'

	def isDisarmed(self):
		return self.armState == 'DISARMED'

	@signal
	def verisureArmStateChanged(self, date, statusType, name, changedVia):
		"""This signal is fired every time the arm state in the alarm is changed"""

	def setSmartplugState(self, device_label, state):
		try:
			session = verisure.Session(self.config('username'), self.config('password'))
			session.login()
			session.set_smartplug_state(device_label, state)
			session.logout()
		except Exception as e:
			logging.warning('Could not communicate with Verisur')
			return

	def __fetch(self):
		if self.config('username') == '':
			return
		def parseValues(overview):
			# Running in the main thread
			deviceManager = DeviceManager(self.context)

			self.armState = overview.get('armState', {}).get('statusType', '')
			# Main box
			if self.alarmDevice.updateStatus(overview['armState']):
				# Send signal
				self.verisureArmStateChanged(overview['armState']['date'], overview['armState']['statusType'], overview['armState']['name'], overview['armState']['changedVia'])

			# Door/Window sensors
			for door in overview.get('doorWindow', {}).get('doorWindowDevice', []):
				deviceLabel = door['deviceLabel']
				if deviceLabel not in self.devices:
					device = DoorWindowDevice(door)
					self.devices[deviceLabel] = device
					deviceManager.addDevice(device)
				else:
					device = self.devices[deviceLabel]
				device.updateStatus(door)

			# Climate values
			for climate in overview.get('climateValues', []):
				deviceLabel = climate['deviceLabel']
				if deviceLabel not in self.devices:
					device = ClimateDevice(climate)
					self.devices[deviceLabel] = device
					deviceManager.addDevice(device)
				else:
					device = self.devices[deviceLabel]
				device.updateValues(climate)

			# Smart plugs
			for plug in overview.get('smartPlugs', []):
				deviceLabel = plug['deviceLabel']
				if deviceLabel not in self.devices:
					device = SmartPlugDevice(plug, self)
					self.devices[deviceLabel] = device
					deviceManager.addDevice(device)
				else:
					device = self.devices[deviceLabel]
				device.updateValues(plug)

			# Door locks
			for lock in overview.get('doorLockStatusList', []):
				deviceLabel = lock['deviceLabel']
				if deviceLabel not in self.devices:
					device = DoorLockDevice(lock)
					self.devices[deviceLabel] = device
					deviceManager.addDevice(device)
				else:
					device = self.devices[deviceLabel]
				device.updateStatus(lock)

			if self.loaded == False:
				deviceManager.finishedLoading('verisure')
				self.loaded = True
		def asyncFetch():
			# This is run in a separate thread and can block
			try:
				session = verisure.Session(self.config('username'), self.config('password'))
				session.login()
				overview = session.get_overview()
				session.logout()
			except Exception as e:
				logging.warning("Could not fetch Verisure data")
				return
			Application().queue(parseValues, overview)
		t = Thread(name='Verisure fetcher', target=asyncFetch)
		t.daemon = True
		t.start()
