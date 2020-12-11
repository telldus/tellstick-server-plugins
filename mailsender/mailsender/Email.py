# -*- coding: utf-8 -*-

from base import configuration, ConfigurationNumber, ConfigurationString, Plugin, implements
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

__name__ = 'mailsender'

@configuration(
	smtpServer = ConfigurationString(
		defaultValue='',
		title='SMTP server name',
		description='Address to the smtpserver',
		minLength=4
	),
	port = ConfigurationNumber(
		defaultValue=25,
		title='SMTP server port',
	),
	username = ConfigurationString(
		defaultValue='',
		title='Username',
		description='Leave blank if not needed'
	),
	password = ConfigurationString(
		defaultValue='',
		title='Password',
		description='Leave blank if not needed'
	),
	fromAddress = ConfigurationString(
		defaultValue='',
		title='From address',
		description='The address the email is sent from'
	)
)
class SMTP(Plugin):
	def create(self):
		return Email(
			self.config('smtpServer'),
			self.config('port'),
			self.config('username'),
			self.config('password'),
			self.config('fromAddress')
		)

	def send(self, **kwargs):
		email = self.create()
		email.send(**kwargs)

class Email(object):
	def __init__(self, server, port, username, password, fromAddress):
		self.server = server
		self.port = port
		self.username = username
		self.password = password
		self.fromAddress = fromAddress

	def send(self, receiver, msg, subject = 'Empty', fromAddress = None):
		mimeMsg = MIMEMultipart('alternative')
		mimeMsg['Subject'] = subject
		mimeMsg['From'] = self.fromAddress if fromAddress is None else fromAddress
		mimeMsg['To'] = receiver

		mimeMsg.attach(MIMEText(msg, 'plain', 'utf8'))

		server = smtplib.SMTP(self.server, self.port)
		server.login(self.username, self.password)
		server.sendmail(mimeMsg['From'], receiver, mimeMsg.as_string())
		server.quit()
