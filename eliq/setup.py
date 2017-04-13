#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Eliq',
	description='Import Eliq energy data into Telldus Live!',
	long_description="""
		Use this plugin to import your power consumption from Eliq.
		You will need to provice an access token in the settings.
		You can find this token at [my.eliq](https://my.eliq.io),
		activate Plus and then go to API.
	""",
	version='1.0',
	icon='eliq_logo.png',
	color='#51b607',
	author='Micke Prag',
	author_email='micke.prag@telldus.se',
	packages=['eliq'],
	package_dir = {'':'src'},
	entry_points={ \
		'telldus.startup': ['c = eliq:Eliq [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
