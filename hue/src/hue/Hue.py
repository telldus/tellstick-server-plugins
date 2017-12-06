# -*- coding: utf-8 -*-

import colorsys
import httplib
import json
import logging
import threading
import urlparse

from base import implements, Application, Plugin, mainthread, configuration
from web.base import IWebRequestHandler, Server, WebResponseJson
from upnp import SSDP, ISSDPNotifier
from telldus import DeviceManager, Device
from telldus.web import IWebReactHandler, ConfigurationReactComponent

class Light(Device):
	def __init__(self, uniqueId, nodeId, bridge):
		super(Light, self).__init__()
		self._uniqueId = uniqueId
		self._nodeId = nodeId
		self._bridge = bridge
		self._type = 'unknown'

	def _command(self, action, value, success, failure, **__kwargs):
		if action == Device.TURNON:
			msg = '{"on": true, "bri": 254}'
		elif action == Device.TURNOFF:
			msg = '{"on": false}'
		elif action == Device.DIM:
			msg = '{"on": true, "bri": %s}' % value
		elif action == Device.RGBW:
			value = int(value, 16)
			red = (value >> 24) & 0xFF
			green = (value >> 16) & 0xFF
			blue = (value >> 8) & 0xFF
			hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
			msg = '{"on": true, "hue": %i, "sat": %i}' % (hue*65535, saturation*254)
		else:
			failure(0)
			return
		retval = self._bridge.doCall(
			'PUT',
			'/api/%s/lights/%s/state' % (self._bridge.username, self._nodeId),
			msg
		)
		if len(retval) == 0 or 'success' not in retval[0]:
			failure(0)
			return
		state = 0
		value = None
		for value in retval:
			if 'success' not in value:
				continue
			successData = value['success']
			if '/lights/%s/state/on' % self._nodeId in successData:
				isOn = successData['/lights/%s/state/on' % self._nodeId]
				if isOn is False:
					state = Device.TURNOFF
					break
			elif '/lights/%s/state/bri' % self._nodeId in successData:
				bri = successData['/lights/%s/state/bri' % self._nodeId]
				if bri == 254:
					state = Device.TURNON
					break
				else:
					state = Device.DIM
					value = bri
		if state == 0:
			failure(0)
		success()

	def localId(self):
		return self._uniqueId

	def typeString(self):  # pylint: disable=R0201
		return 'hue'

	def isDevice(self):  # pylint: disable=R0201
		return True

	def isSensor(self):  # pylint: disable=R0201
		return False

	def methods(self):
		if self._type in ['Extended color light', 'Color light']:
			return Device.TURNON | Device.TURNOFF | Device.DIM | Device.RGBW
		if self._type in ['Dimmable light', 'Color temperature light']:
			return Device.TURNON | Device.TURNOFF | Device.DIM
		# Unknown type
		return Device.TURNON | Device.TURNOFF | Device.DIM

	def setType(self, newType):
		self._type = newType

@configuration(
	bridge=ConfigurationReactComponent(
		component='hue',
		defaultValue={},
	)
)
class Hue(Plugin):
	implements(IWebRequestHandler)
	implements(IWebReactHandler)
	implements(ISSDPNotifier)
	STATE_NO_BRIDGE, STATE_UNAUTHORIZED, STATE_AUTHORIZED = range(3)

	def __init__(self):
		self.deviceManager = DeviceManager(self.context)
		self.username = None
		self.ssdp = None
		config = self.config('bridge')
		self.activated = config.get('activated', False)
		self.username = config.get('username', '')
		self.bridge = config.get('bridge', '')
		self.state = Hue.STATE_NO_BRIDGE
		self.lights = {}
		if not self.activated:
			self.ssdp = SSDP(self.context)
		else:
			Application().queue(self.selectBridge, config.get('bridge'))
		Application().registerScheduledTask(self.update, minutes=1)

	@mainthread
	def authorize(self):
		if self.username is None or self.username == '':
			data = self.doCall('POST', '/api', '{"devicetype": "Telldus#TellStick"}')
			resp = data[0]
			if resp.get('error', {}).get('type', None) == 101:
				# Unauthorized, the user needs to press the button. Try again in 5 seconds
				thread = threading.Timer(5.0, self.authorize)
				thread.name = 'Philips Hue authorization poll timer'
				thread.daemon = True
				thread.start()
				return
			if 'success' in resp:
				self.username = resp['success']['username']
				self.activated = True
				self.saveConfig()
				self.setState(Hue.STATE_AUTHORIZED)
			else:
				return
		# Check if username is ok
		data = self.doCall('GET', '/api/%s/lights' % self.username)
		if 0 in data and 'error' in data[0]:
			self.setState(Hue.STATE_UNAUTHORIZED)
			return
		self.setState(Hue.STATE_AUTHORIZED)
		self.parseInitData(data)

	def doCall(self, requestType, endpoint, body=''):
		conn = httplib.HTTPConnection(self.bridge)
		try:
			conn.request(requestType, endpoint, body)
		except Exception:
			return [{'error': 'Could not connect'}]
		response = conn.getresponse()
		try:
			rawData = response.read()
			data = json.loads(rawData)
		except Exception:
			logging.warning("Could not parse JSON")
			logging.warning("%s", rawData)
			return [{'error': 'Could not parse JSON'}]
		return data

	def getReactComponents(self):  # pylint: disable=R0201
		return {
			'hue': {
				'title': 'Philips Hue',
				'script': 'hue/hue.js',
			}
		}

	def matchRequest(self, plugin, path):  # pylint: disable=R0201
		if plugin != 'hue':
			return False
		if path in ['reset', 'state']:
			return True
		return False

	def handleRequest(self, plugin, path, __params, **__kwargs):
		if plugin != 'hue':
			return None

		if path == 'state':
			if self.state == Hue.STATE_NO_BRIDGE:
				# If ssdp fails to detect, use the hue remote service
				self.searchNupnp()
			return WebResponseJson({'state': self.state})

		if path == 'reset':
			self.setState(Hue.STATE_NO_BRIDGE)
			return WebResponseJson({'success': True})

	def parseInitData(self, data):
		self.parseLights(data)
		self.deviceManager.finishedLoading('hue')

	def parseLights(self, lights):
		oldDevices = self.lights.keys()
		for i in lights:
			lightData = lights[i]
			if 'uniqueid' not in lightData:
				continue
			lightId = lightData['uniqueid']
			if lightId in oldDevices:
				# Find any removed lights
				oldDevices.remove(lightId)
			name = lightData.get('name', '')
			if lightId in self.lights:
				light = self.lights[lightId]
				if light.name() != name:
					light.setName(name)
			else:
				light = Light(lightId, i, self)
				self.lights[lightId] = light
				if 'type' in lightData:
					light.setType(lightData['type'])
				self.deviceManager.addDevice(light)
				light.setName(name)
			if 'state' in lightData:
				state = lightData['state']
				ourState, ourStateValue = light.state()
				if state['on'] is False:
					hueState = Device.TURNOFF
					hueStateValue = ourStateValue
				elif state['bri'] == 254:
					hueState = Device.TURNON
					hueStateValue = ourStateValue
				else:
					hueState = Device.DIM
					hueStateValue = state['bri']
				if ourState != hueState or ourStateValue != hueStateValue:
					light.setState(hueState, hueStateValue)
		for lightId in oldDevices:
			light = self.lights[lightId]
			self.deviceManager.removeDevice(light.id())
			del self.lights[lightId]

	def saveConfig(self):
		self.setConfig('bridge', {
			'bridge': self.bridge,
			'username': self.username,
			'activated': self.activated,
		})

	def searchNupnp(self):
		conn = httplib.HTTPSConnection('www.meethue.com')
		conn.request('GET', '/api/nupnp')
		response = conn.getresponse()
		try:
			rawData = response.read()
			data = json.loads(rawData)
		except Exception:
			logging.warning("Could not parse JSON")
			logging.warning("%s", rawData)
			return
		for bridge in data:
			if 'internalipaddress' not in bridge:
				continue
			self.selectBridge(bridge['internalipaddress'])
			return

	def setState(self, newState):
		if newState == Hue.STATE_NO_BRIDGE:
			self.bridge = None
			self.username = None
			self.activated = False
			self.saveConfig()
		elif newState == Hue.STATE_UNAUTHORIZED:
			Application().queue(self.authorize)
		elif newState == Hue.STATE_AUTHORIZED:
			pass
		self.state = newState
		# Notify websocket
		Server(self.context).webSocketSend('hue', 'status', {'state': self.state})

	def ssdpDeviceFound(self, device):
		if self.state != Hue.STATE_NO_BRIDGE:
			return
		if device.type == 'basic:1':
			url = urlparse.urlparse(device.location)
			self.selectBridge(url.netloc)

	def selectBridge(self, urlbase):
		if urlbase == '' or urlbase is None:
			self.setState(Hue.STATE_NO_BRIDGE)
			return
		self.bridge = urlbase
		self.saveConfig()
		self.setState(Hue.STATE_UNAUTHORIZED)

	def tearDown(self):
		self.deviceManager.removeDevicesByType('hue')

	def update(self):
		if self.state != Hue.STATE_AUTHORIZED:
			# Skip
			return
		data = self.doCall('GET', '/api/%s/lights' % self.username)
		if 0 in data and 'error' in data[0]:
			return
		self.parseLights(data)
