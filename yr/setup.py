#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='YR Weather',
	version='1.2',
	color='#00b9f1',
	icon='yr-logo.png',
	author='Micke Prag',
	author_email='micke.prag@telldus.se',
	category='weather',
	description='Import weatherdata from the current location from yr.no',
	long_description="""
		Use this plugin to collect weatherdata from the current location from yr.no.
		Data is imported once per hour.
		Make sure that you have set the coordinates for your TellStick.
	""",
	packages=['yrno'],
	entry_points={ \
		'telldus.startup': ['c = yrno:Weather [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
