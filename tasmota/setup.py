#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
    name='Tasmota',
    version='1.0',
    author='Telldus Technologies',
    author_email='info.tech@telldus.se',
    color='#1FA3EC',
    icon='tasmota.png',
    category='appliances',
    description='Controll Tasmota devices',
    zeroconf=[{
        'type':'_http._tcp.local.',
        'properties':{
          'devicetype':'tasmota',
        },
    }],
    long_description="""
		Please note that mDNS must be activated in the devices.
	""",
    packages=['tasmota'],
    entry_points={ \
  'telldus.startup': ['c = tasmota:TasmotaManager [cREQ]']
                  },
    extras_require=dict(cREQ='Base>=0.1\nTelldus>=0.1'),
)
