#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Broadlink',
	version='1.0',
	author='Telldus Technologies',
	author_email='info.tech@telldus.se',
	color='#2c3e50',
	description='Broadlink device for On/Off switched',
	long_description="""
		Plugin for controlling broadlink devices
	""",
	packages=['broadlinkdevice'],
	package_dir = {'':'src'},
	entry_points={ \
		'telldus.startup': ['c = broadlinkdevice:Broadlink [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
