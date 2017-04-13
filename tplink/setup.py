#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='TP-Link',
	version='1.0',
	author='Fredrik Gullberg',
	author_email='fredrik.gullberg@telldus.se',
	color='#2ecfda',
	description='Plugin that allows you to control TP-Link HS100/HS110',
	long_description="""
		Use this plugin to control your TP-Link HS100/HS110 devices.
		All devices will be imported at startup.
	""",
	icon='tplink.png',
	long_description="",
	packages=['tplink'],
	entry_points={ \
		'telldus.startup': ['c = tplink:TPLink [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
