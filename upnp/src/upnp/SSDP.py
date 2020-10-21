# -*- coding: utf-8 -*-

import socket
from threading import Thread
import logging

from six.moves import http_client
from six import BytesIO

from base import ObserverCollection, IInterface, Application, Plugin, mainthread

from .Device import Device


class ISSDPNotifier(IInterface):
	def ssdpRootDeviceFound(rootDevice):  # pylint: disable=no-self-argument
		"""This method is called when a root device is found on the network"""

	def ssdpDeviceFound(device):  # pylint: disable=no-self-argument
		"""This method is called when a device is found on the network"""

	def ssdpServiceFound(service):  # pylint: disable=no-self-argument
		"""This method is called when a service is found on the network"""


class SSDPResponse(object):
	ST_ROOT_DEVICE, ST_DEVICE, ST_SERVICE, ST_UNKNOWN = range(4)

	class _FakeSocket(BytesIO):
		def makefile(self, *_args, **_kwargs):
			return self

	def __init__(self, response):
		httpResponse = http_client.HTTPResponse(self._FakeSocket(response))
		httpResponse.begin()
		self.location = httpResponse.getheader("location", '')
		self.usn = httpResponse.getheader("usn", '')
		self.st = httpResponse.getheader("st", '')  # pylint: disable=invalid-name
		try:
			self.cache = httpResponse.getheader("cache-control").split("=")[1]
		except:
			logging.warning("Could not extract cache-control header.")
			logging.warning("Headers are: %s", httpResponse.getheaders())
		index = self.usn.find('::')
		if index >= 0:
			self.uuid = self.usn[5:index]
		else:
			self.uuid = self.usn[5:]
		self.type = SSDPResponse.ST_UNKNOWN
		if self.st == 'upnp:rootdevice':
			self.type = SSDPResponse.ST_ROOT_DEVICE
		elif self.st.startswith('urn:schemas-upnp-org:device'):
			self.type = SSDPResponse.ST_DEVICE
			self.deviceType = self.st[28:]


class SSDP(Plugin):
	observers = ObserverCollection(ISSDPNotifier)

	def __init__(self):
		self.rootDevices = {}
		self.devices = {}
		Application().registerScheduledTask(
		    self.startDiscover, minutes=10, runAtOnce=True
		)

	def startDiscover(self):
		thread = Thread(target=self.discover, name='SSDP discoverer')
		thread.daemon = True
		thread.start()

	def discover(self):
		service = "ssdp:all"
		group = ("239.255.255.250", 1900)
		message = "\r\n".join(
		    [
		        'M-SEARCH * HTTP/1.1', 'HOST: {0}:{1}', 'MAN: "ssdp:discover"',
		        'ST: {st}', 'MX: 3', '', ''
		    ]
		)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.settimeout(5)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(message.format(*group, st=service).encode('utf-8'), group)
		while True:
			try:
				response = SSDPResponse(sock.recv(1024))
				if response.type == SSDPResponse.ST_ROOT_DEVICE:
					pass
				elif response.type == SSDPResponse.ST_DEVICE:
					device = Device.fromSSDPResponse(response)
					self.devices[response.uuid] = device
			except socket.timeout:
				break
		self.__discoveryDone()

	@mainthread
	def __discoveryDone(self):
		for i in self.devices:
			self.observers.ssdpDeviceFound(self.devices[i])
