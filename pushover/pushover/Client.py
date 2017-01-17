# -*- coding: utf-8 -*-

from base import configuration, ConfigurationString, Plugin
import httplib, urllib, json

__name__ = 'pushover'

@configuration(
	apiToken = ConfigurationString(
		defaultValue='',
		title='API Token/Key',
		description='Genererate an token in Pushover portal',
		minLength=30,
		maxLength=30
	),
	userKey = ConfigurationString(
		defaultValue='',
		title='User key',
		description='Get the user key from the Pushover portal',
		minLength=30,
		maxLength=30
	),
)
class Client(Plugin):
	def send(self, msg, device='', title='', url='', url_title='', priority=0, sound=''):
		if self.config('apiToken') == '' or self.config('userKey') == '':
			raise Exception('Pushover is not configured. Please setup apiToken and userKey first')
		conn = httplib.HTTPSConnection('api.pushover.net:443')
		conn.request('POST', '/1/messages.json',
			urllib.urlencode({
				'token': self.config('apiToken'),
				'user': self.config('userKey'),
				'message': msg,
				'device': device,
				'title': title,
				'url': url,
				'url_title': url_title,
				'priority': priority,
				'sound': sound
			}), { 'Content-type': 'application/x-www-form-urlencoded' })
		resp = conn.getresponse()
		return json.loads(resp.read())
