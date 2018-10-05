#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

# The python library broadlink depends on pycryptodome which includes c extentions
# It seems the api is equal to PyCrypto so just skipping this dependency seems to work for now

setup(
	name='Broadlink-HA',
	version='1.0',
	author='Telldus Technologies',
	author_email='info.tech@telldus.se',
	category='appliances',
	color='#14b1ee',
	icon='broadlink.png',
	description='Broadlink device support',
	long_description="""Plugin for controlling device from Broadlink devices
These devices are also sold under other brands. Such as ClasOhlson.""",
	packages=['broadlinkdevice'],
	entry_points={ \
		'telldus.startup': ['c = broadlinkdevice:Broadlink [cREQ]']
	},
	extras_require=dict(cREQ='Base>=0.1\nTelldus>=0.1'),
)
