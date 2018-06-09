#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Configuration',
	version='1.0',
	author='ajajul',
	icon='Setting-icon.png',
	color='#1597f1',
	author_email='ajajul9998555036@gmail.com',
	description='Company Information',
	packages=['configuration'],
	long_description="""Use this plugin to get company information through Lua scripts.

Example to get company information from Lua:
```lua
local companyObject = require "configuration.Config"
local companyData = companyObject:companyInfo()
```
""",
	entry_points={ \
		'telldus.plugins': ['c = configuration:Config [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
