#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='WorkDay Sensor',
	version='1.0',
	author='Telldus Technologies',
	author_email='info.tech@telldus.se',
	color='#2c3e50',
	description='According to workday on/off the device',
	long_description="""
		Plugin that controll on/off of device based on working day.
	""",
	packages=['workdaysensor'],
	package_dir = {'':'src'},
	entry_points={ \
		'telldus.startup': ['c = workdaysensor:WorkDaySensor [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
