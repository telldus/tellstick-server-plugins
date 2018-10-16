#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Holiday',
	version='1.0',
	author='ajajul',
	author_email='ajajul9998555036@gmail.com',
	color='#2c3e50',
	description='According to workday on/off the device',
	long_description="""
		Plugin that controll on/off of device based on working day.
	""",
	packages=['holiday'],
	entry_points={ \
		'telldus.startup': ['c = holiday:Holiday [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
