#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='WeMo',
	description='Control WEMO Insight',
	version='1.0',
	icon='icon.png',
	color='#94e05c',
	author='Micke Prag',
	author_email='micke.prag@telldus.se',
	packages=['wemo'],
	package_dir = {'':'src'},
	entry_points={ \
		'telldus.startup': ['c = wemo:WeMo [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
