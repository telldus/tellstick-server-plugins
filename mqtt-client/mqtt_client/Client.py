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
		self.client = mqtt.Client()
		self.client.on_connect = self.onConnect
		self.client.on_message = self.onMessage
		self.client.on_publish = self.onPublish
		self.client.on_subscribe = self.onSubscribe
		if self.config('hostname') != '':
			self.connect()

	def configWasUpdated(self, key, __value):
		if key == 'hostname':
			self.connect()

	def connect(self):
		if self.config('username') != '':
			self.client.username_pw_set(self.config('username'), self.config('password'))
		self.client.connect_async(self.config('hostname'), self.config('port'))
		self.client.loop_start()

	@slot('deviceStateChanged')
	def onDeviceStateChanged(self, device, state, stateValue, origin=None):
		del origin
		self.client.publish('%s/device/%s/state' % (self.config('topic'), device.id()), json.dumps({
			'state': state,
			'stateValue': stateValue,
			#'origin': origin,
		}))

	def onConnect(self, client, userdata, flags, result):
		pass

	def onMessage(self, client, userdata, msg):
		pass

	def onPublish(self, client, obj, mid):
		pass

	@slot('sensorValueUpdated')
	def onSensorValueUpdated(self, device, valueType, value, scale):
		self.client.publish('%s/sensor/%s/value' % (self.config('topic'), device.id()), json.dumps({
			'value': FloatWrapper(value),
			'valueType': valueType,
			'scale': scale,
		}))

	def onSubscribe(self, client, obj, mid, granted_qos):
		pass
