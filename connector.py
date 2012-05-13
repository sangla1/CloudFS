#!/usr/bin/env python

import dropbox

class Connector:

	def __init__(self):
		self.conns = []
		self.conns.append(dict(name='test', app=Dropbox('vhgangrvc4w2poo', '2xsktxsbhn465mr')))

	def getConns(self):
		conns = []
		for conn in self.conns:
			conns.append(conn['name'])

		return conns
	
	def hasConn(self, name):
		if self.findConn(name) != None:
			return True
		return False
	
	def findConn(self, name):
		for conn in self.conns:
			if name == conn['name']:
				return conn
		return None

	def getDents(self, name, path):
		conn = self.findConn(name)
		if conn == None:
			return None
		return conn['app'].ls(path)
	
	def getAttr(self):
		nop
	
	def push(self):
		nop
	
	def pull(self):
		nop
	
	def remove(self):
		nop
