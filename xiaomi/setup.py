#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Xiaomi',
	version='1.0',
	description='Plugin to import devices from Xiaomi Gateway ',
	long_description=open('long_description.md', 'r').read(),
	icon='xiaomi.png',
	color='#69b68a',
	author='Micke Prag',
	author_email='micke.prag@gmail.com',
	category='appliances',
	packages=['xiaomi'],
	entry_points={ \
		'telldus.startup': ['c = xiaomi:Gateway [cREQ]']
	},
	extras_require=dict(cREQ='Base>=0.1\nTelldus>=0.1'),
)
