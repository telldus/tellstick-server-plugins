# -*- coding: utf-8 -*-

from base import ConfigurationManager, Plugin, configuration, implements
from web.base import IWebRequestHandler, WebResponseJson
from pluginloader import ConfigurationOAuth2
from threading import Thread
import logging

@configuration(
	oauth=ConfigurationOAuth2(
		clientId='',
		clientSecret='',
		accessTokenUrl='https://home.myharmony.com/oauth2/token',
		authorizeUrl='https://api.telldus.com/logitech/authorize',
		baseUrl='https://home.myharmony.com/cloudapi/',
		params={
			'scope': 'remote',
			'response_type': 'code',
		},
	)
)
class Harmony(Plugin):
	implements(IWebRequestHandler)
	ACTIVITY_TYPES = {
		1: 'Watch TV',
		2: 'Watch DVD',
		3: 'Play Game',
		4: 'Listen To Music',
		5: 'Custom',
		6: 'Surf Web',
		7: 'Watch Netflix',
		8: 'Make Video Call',
		9: 'Watch Apple TV',
		10: 'Watch Roku',
		11: 'PCTV',
		12: 'Smart TV',
		13: 'Watch Fire TV',
		14: 'Listen To Sonos',
	}

	def __init__(self):
		self.activities = {}
		config = self.config('oauth')
		if config.get('access_token', '') is not '':
			self.configuration['oauth'].activated = True
			self.__refresh()

	def configWasUpdated(self, key, value):
		if key == 'oauth':
			self.__refresh()

	def __refresh(self):
		if not self.configuration['oauth'].activated:
			return
		def backgroundTask():
			config = self.config('oauth')
			session = self.configuration['oauth'].session(config.get('access_token'))
			response = session.get('activity/all')
			data = response.json()
			for id, hub in data.get('hubs', {}).items():
				if hub['status'] is not 200:
					# Error, skip (for now)
					logging.warning('Hub is not available %s', hub)
					continue
				response = hub.get('response', {'code': None})
				if hub['response']['code'] is not 200:
					# Error
					continue
				for activityId, activity in response.get('data', {}).items():
					logging.warning("Activity: %s", activity['name'])
		Thread(target=backgroundTask).start()
