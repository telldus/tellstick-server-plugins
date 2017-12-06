#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
	from setuptools.command.bdist_egg import bdist_egg
except ImportError:
	from distutils.core import setup
	from distutils.command.bdist_egg import bdist_egg
import os

class buildweb(bdist_egg):
	def run(self):
		print("generate web application")
		if os.system('npm install') != 0:
			raise Exception("Could not install npm packages")
		if os.system('npm run build') != 0:
			raise Exception("Could not build web application")
		bdist_egg.run(self)

setup(
	name='Philips Hue',
	version='1.1',
	author='Telldus Technologies AB',
	author_email='info.tech@telldus.se',
	category='appliances',
	description='Control Philips Hue lights',
	packages=['hue'],
	package_dir = {'':'src'},
	color='#000000',
	icon='philipshue.png',
	cmdclass={'bdist_egg': buildweb},
	entry_points={ \
		'telldus.startup': ['c = hue:Hue [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldusWeb>=0.1'),
	package_data={'hue' : [
		'htdocs/img/*.jpg',
		'htdocs/*.js',
	]}
)
