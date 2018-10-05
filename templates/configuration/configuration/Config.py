# -*- coding: utf-8 -*-

from base import configuration, ConfigurationString, Plugin, ConfigurationNumber

__name__ = 'configuration'  # pylint: disable=W0622

@configuration(
	companyName=ConfigurationString(
		defaultValue='',
		title='Company Name',
		description='Name of the Company'
	),
	founded=ConfigurationNumber(
		defaultValue=[],
		title='Founded year',
		description='The year the company was founded',
		minimum=1900,
		maximum=2050
	),
	username=ConfigurationString(
		defaultValue='',
		title='Username',
		description='Username of the company Administrator'
	),
	password=ConfigurationString(
		defaultValue='',
		title='Password',
		description='Password of the company Administrator',
		minLength=8,
		maxLength=15
	)
)
class Config(Plugin):

	def getCompanyInfo(self):
		return {
			'companyName' : self.config('companyName'),
			'founded' : self.config('founded'),
			'username' : self.config('username'),
			'password' : self.config('password'),
		}
