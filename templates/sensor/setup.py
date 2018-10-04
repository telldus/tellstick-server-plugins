#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Temperature sensor',
	version='1.0',
	author='Alice',
	author_email='alice@wonderland.lit',
	color='#2c3e50',
	description='Temperature template for implementings sensor plugins',
	icon='temperature.png',
	long_description="""
		This plugin is used as a template when creating plugins that support new sensor types.
	""",
	packages=['temperature'],
	package_dir = {'':'src'},
	entry_points={ \
		'telldus.startup': ['c = temperature:Temperature [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
