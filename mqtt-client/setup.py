#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='MQTT Client',
	version='1.1',
	description='Plugin to connect to a MQTT broker',
	icon='mqtt.png',
	color='#660066',
	author='Artem Vitiuk',
	author_email='artem@vitiuk.me',
	category='notifications',
	packages=['mqtt_client'],
	entry_points={
		'telldus.startup': ['c = mqtt_client:Client [cREQ]']
	},
	extras_require=dict(cREQ='Base>=0.1\nTelldus>=0.1'),
)
