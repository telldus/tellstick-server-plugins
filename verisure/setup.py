#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Verisure',
	version='1.1',
	description='Plugin to read status from a Verisure Alarm',
	long_description="""This software is not affiliated with Verisure Holding AB and the developers take no legal responsibility for the functionality or security of your Verisure Alarms and devices.

Only reading status is currently supported. Setting the armstate is currently not possible for security reasons.""",
	icon='verisure.png',
	color='#c3c6c8',
	author='Micke Prag',
	author_email='micke.prag@gmail.com',
	category='security',
	packages=['tellstick_verisure'],
	entry_points={ \
		'telldus.startup': ['c = tellstick_verisure:Alarm [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
