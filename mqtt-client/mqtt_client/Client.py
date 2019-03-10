# -*- coding: utf-8 -*-

import json

from base import \
	Plugin, \
	configuration, \
	ConfigurationNumber, \
	ConfigurationString, \
	implements, \
	ISignalObserver, \
	slot
from telldus import DeviceManager, Device
import paho.mqtt.client as mqtt


__name__ = 'MQTT'  # pylint: disable=W0622


# On mips 0.1 might be represented as 0.10000000000000001. This is a workaround.
class FloatWrapper(float):
	def __repr__(self):
		return '%.15g' % self


@configuration(
	username=ConfigurationString(
		defaultValue='',
		title='Username',
	),
	password=ConfigurationString(
		defaultValue='',
		title='Password',
	),
	hostname=ConfigurationString(
		defaultValue='',
		title='Hostname',
	),
	port=ConfigurationNumber(
		defaultValue=1883,
		title='Port',
	),
	topic=ConfigurationString(
		defaultValue='telldus',
		title='Base topic'
	)
)
class Client(Plugin):
	implements(ISignalObserver)

	def __init__(self):
		self.deviceManager = DeviceManager(self.context)

		self.client = mqtt.Client('telldus')
		self.client.on_connect = self.onConnect
		self.client.on_message = self.onMessage
		self.client.on_publish = self.onPublish
		self.client.on_subscribe = self.onSubscribe
		if self.config('hostname') != '':
			self.connect()

	def configWasUpdated(self, key, __value):
		# TODO: handle other changes
		if key == 'hostname':
			self.connect()

	def connect(self):
		if self.config('username') != '':
			self.client.username_pw_set(self.config('username'), self.config('password'))
		self.client.will_set('%s/status' % self.config('topic'), payload='Offline', qos=0, retain=True)
		self.client.connect_async(self.config('hostname'), self.config('port'))
		self.client.loop_start()

	def subscribeDevice(self, deviceId):
		self.client.subscribe('%s/device/%s/cmd' % (self.config('topic'), deviceId))

	def unsubscribeDevice(self, deviceId):
		self.client.unsubscribe('%s/device/%s/cmd' % (self.config('topic'), deviceId))

	@slot('deviceAdded')
	def onDeviceAdded(self, device):
		self.subscribeDevice(device.id())

	@slot('deviceRemoved')
	def onDeviceRemoved(self, deviceId):
		self.unsubscribeDevice(deviceId)

	@slot('deviceStateChanged')
	def onDeviceStateChanged(self, device, state, stateValue, origin=None):
		del origin
		self.client.publish('%s/device/%s/state' % (self.config('topic'), device.id()), json.dumps({
			'name': device.name(),
			'state': state,
			'stateValue': stateValue,
		}))

	@slot('sensorValueUpdated')
	def onSensorValueUpdated(self, device, valueType, value, scale):
		self.client.publish('%s/sensor/%s/value' % (self.config('topic'), device.id()), json.dumps({
			'name': device.name(),
			'value': FloatWrapper(value),
			'valueType': valueType,
			'scale': scale,
		}))

	def onConnect(self, client, userdata, flags, result):
		for device in self.deviceManager.devices:
			self.subscribeDevice(device.id())
		self.subscribeDevice(4)
		self.client.publish('%s/status' % self.config('topic'), payload='Online', qos=0, retain=True)

	def onMessage(self, client, userdata, msg):
		try:
			data = json.loads(str(msg.payload.decode('utf-8')))
			deviceId = msg.topic.split('/')[3]
			device = self.deviceManager.device(deviceId)
			if device and data.get('action'):
				device.command(data.get('action'), data.get('value'))
		except Exception as e:
			# TODO: log?
			print('Couldn\'t decode JSON payload')

	def onPublish(self, client, obj, mid):
		pass

	def onSubscribe(self, client, obj, mid, granted_qos):
		pass
