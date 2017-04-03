#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Sonos',
	version='0.1',
	description='Plugin that allows you to control Sonos speakers',
	icon='icon.png',
	color='#000000',
	author='Micke Prag',
	author_email='micke.prag@telldus.se',
	category='multimedia',
	packages=['sonos'],
	entry_points={ \
		'telldus.startup': ['c = sonos:Sonos [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
