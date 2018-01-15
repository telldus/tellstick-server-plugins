#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Lifx',
	description='Plugin that allows you to control Lifx bulbs',
	version='1.1',
	icon='icon.png',
	color='#440099',
	author='Micke Prag',
	author_email='micke.prag@telldus.se',
	category='appliances',
	packages=['tellstick_lifx'],
	package_dir={'':'src'},
	entry_points={ \
		'telldus.startup': ['c = tellstick_lifx:Lifx [cREQ]']
	},
	extras_require=dict(cREQ='Base>=0.1\nTelldus>=0.1'),
)
