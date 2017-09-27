#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Harmony',
	version='1.0',
	author='Telldus Technologies AB',
	author_email='info.tech@telldus.se',
	category='multimedia',
	description='Control Logitech Harmony scenes',
	long_description="""
		Use this plugin to control Logitech Harmony scenes from Telldus Live!
		Only scenes are supported right now. No individual buttons can be used.
		This is a limitation by Logitech.
	""",
	icon='harmony.png',
	color='#00a9e0',
	packages=['harmony'],
	entry_points={ \
		'telldus.startup': ['c = harmony:Harmony [cREQ]']
	},
	extras_require=dict(cREQ='Base>=0.1\nTelldus>=0.1\nTelldusWeb>=0.1'),
)
