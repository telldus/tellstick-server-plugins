#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='Eliq',
	version='0.1',
	packages=['eliq'],
	package_dir = {'':'src'},
	entry_points={ \
		'telldus.startup': ['c = eliq:Eliq [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1\nTelldusWeb>=0.1'),
	package_data={'eliq' : [
		'templates/*.html',
	]}
)
