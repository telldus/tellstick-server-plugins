#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Mail sender',
	version='1.0',
	icon='email.png',
	author='Telldus Technologies',
	author_email='info.tech@telldus.se',
	color='#000000',
	description='Send emails from lua scripts',
	long_description="""
		Use this plugin to add support for sending emails through Lua scripts.
		You need to supply your own smtp-server.
		Example to send an email from Lua:
		local smtp = require "mailsender.SMTP"
		smtp:send{
			receiver='email@example.com',
			msg='Hello from lua',
			subject='Lua mailer'
		}
	""",
	packages=['mailsender'],
	entry_points={ \
		'telldus.plugins': ['c = mailsender:SMTP [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
