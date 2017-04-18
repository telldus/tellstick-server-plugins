#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='HTTP lib',
	version='1.0',
	icon='icon_96x96_http_request.png',
	author='Telldus Technologies',
	author_email='info.tech@telldus.se',
	category='notifications',
	color='#26a69a',
	description='Lua library for making http calls',
	long_description=open('long_description.md', 'r').read(),
	packages=['http'],
	entry_points={ \
		'telldus.plugins': ['c = http:Request [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
