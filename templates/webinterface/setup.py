#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from setuptools import setup
	from setuptools.command.install import install
except ImportError:
	from distutils.core import setup
	from distutils.command.install import install
import os

class buildweb(install):
	def run(self):
		print("generate web application")
		os.system('npm install')
		os.system('npm run build')
		install.run(self)

setup(
	name='Webinterface',
	version='0.1',
	packages=['webinterface'],
	package_dir = {'':'src'},
	cmdclass={'install': buildweb},
	entry_points={ \
		'telldus.plugins': ['c = webinterface:Webinterface [cREQ]']
	},
	extras_require = dict(cREQ = 'Base>=0.1\nTelldus>=0.1\nTelldusWeb>=0.1')
)
