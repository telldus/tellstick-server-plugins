#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='SqueezeBox',
	version='1.0',
	color='#2baaa6',
	icon='squeezebox.png',
	author='Micke Prag',
	author_email='micke.prag@telldus.se',
	category='multimedia',
	description='Plugin to control Logitech Squeezebox from TellStick',
	long_description="""
		Use this plugin to control your Squeezebox fom TellStick.
		You'll need to supply the IP for your Squeezebox server in the settings for the plugin.
	""",
	packages=['squeezebox'],
	package_dir = {'':'src'},
	entry_points={ \
		'telldus.startup': ['c = squeezebox:SqueezeBox [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1'),
)
