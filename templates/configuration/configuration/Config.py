# -*- coding: utf-8 -*-

from base import configuration, ConfigurationString, Plugin, ConfigurationList

__name__ = 'configuration'

@configuration(
	companyName = ConfigurationString(
		defaultValue='Telldus Technologies',
		title='Company Name',
		description='Name of the Company'
	),
	contacts = ConfigurationList(
		defaultValue=['9879879879', '8529513579', '2619859867'],
		title='company contacts',
		description='Contacts of the company',
		minLength=2
	),
	username = ConfigurationString(
		defaultValue='admin@gmail.com',
		title='Username',
		description='Username of the company Administrator'
	),
	password = ConfigurationString(
		defaultValue='admin1234',
		title='Password',
		description='Password of the company Administrator',
		minLength=8,
		maxLength=12
	)
)
class Config(Plugin):
	def companyInfo(self):
		return {
			'companyName' : self.config('companyName'),
			'contacts' : self.config('contacts'),
			'username' : self.config('username'),
			'password' : self.config('password'),
		}
