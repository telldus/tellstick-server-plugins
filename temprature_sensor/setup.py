#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Tempreture sensor',
	version='1.0',
	author='Alice',
	author_email='alice@wonderland.lit',
	color='#2c3e50',
	description='Tempreture template for implementings sensor plugins',
	icon='temprature.png',
	long_description="""
		This plugin is used as a template when creating plugins that support new sensor types.
	""",
	packages=['temprature'],
	package_dir = {'':'src'},
	entry_points={ \
		'telldus.startup': ['c = temprature:Temprature [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
