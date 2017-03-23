#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Eliq',
	description='Import Eliq energy data into Telldus Live!',
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
