# -*- coding: utf-8 -*-

from base import configuration, ConfigurationString, Plugin, ConfigurationList, ConfigurationManager

__name__ = 'configuration'

@configuration(
	companyName = ConfigurationString(
		defaultValue='',
		title='Company Name',
		description='Name of the Company'
	),
	contacts = ConfigurationList(
		defaultValue=[],
		title='company contacts',
		description='Contacts of the company'
	),
	username = ConfigurationString(
		defaultValue='',
		title='Username',
		description='Username of the company Administrator'
	),
	password = ConfigurationString(
		defaultValue='',
		title='Password',
		description='Password of the company Administrator'
	)
)
class Config(Plugin):

	def getCompanyInfo(self):
		return {
			'companyName' : self.config('companyName'),
			'contacts' : self.config('contacts'),
			'username' : self.config('username'),
			'password' : self.config('password'),
		}
