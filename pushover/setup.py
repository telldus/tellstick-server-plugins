#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Pushover',
	description='Pushover makes it easy to get real-time notifications on your Android, iPhone, iPad, and Desktop (Pebble, Android Wear, and Apple watches, too!)',
	version='1.0',
	icon='icon-96.png',
	color='#1597f1',
	author='Micke Prag',
	author_email='micke.prag@telldus.se',
	category='notifications',
	packages=['pushover'],
	entry_points={ \
		'telldus.plugins': ['c = pushover:Client [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
