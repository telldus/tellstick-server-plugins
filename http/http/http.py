# -*- coding: utf-8 -*-

from base import Plugin
import requests, threading

__name__ = 'http'

class Request(Plugin):
	public = True

	def get(self, success=None, **kwargs):
		r = PendingRequest(requests.get, success, kwargs)
		r.start()
		return r

	def post(self, success=None, **kwargs):
		r = PendingRequest(requests.post, success, kwargs)
		r.start()
		return r

class PendingRequest(threading.Thread):
	def __init__(self, fn, callback, kwargs):
		super(PendingRequest,self).__init__(name='HTTP request')
		self.daemon = True
		self.fn = fn
		if hasattr(callback, 'registerDestructionHandler'):
			callback.registerDestructionHandler(self.__callbackDestroyed)
		self.callback = callback
		self.kwargs = kwargs

	def __callbackDestroyed(self):
		self.callback = None

	def run(self):
		r = self.fn(**self.kwargs)
		if self.callback is not None:
			self.callback(r)
