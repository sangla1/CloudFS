#!/usr/bin/env python

import account

from s3fs import AmazonS3FS
from dropboxfs import DropboxFS

from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

class Connector:

	def __init__(self):
		self.conns = []
		self.conns.append(dict(name='dropbox', app=DropboxFS('vhgangrvc4w2poo', '2xsktxsbhn465mr')))
		self.conns.append(dict(name='amazons3', app=AmazonS3FS('AKIAIKYAQ2OX6ZHAGDMA', 'K2GJ6y0BkDxi8/NmKXK0vLqhoqd8DcQLA+EJyHBN')))

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
		connList = conn['app'].ls(path)
		print connList
		return connList
	
	def getAttr(self, name, path):
		conn = self.findConn(name)
		if conn == None:
			return None
		connAttr = conn['app'].getFileInfo(path)

		return connAttr
	
	def push(self, name, path, content):
		conn = self.findConn(name)
		if conn == None:
			return False

		print 'PUSH'
		print path
		print content

		conn['app'].put(content, path)

		return True
	
	def pull(self, name, path):
		conn = self.findConn(name)
		if conn == None:
			print 1
			return None
		print path
		content = conn['app'].get(path)
		print 2, content
		return content
	
	def rm(self, name, path):
		conn = self.findConn(name)
		if conn == None:
			return False

		return conn['app'].rm(path)
	
	def mkdir(self, name, path):
		conn = self.findConn(name)
		if conn == None:
			return False

		return conn['app'].mkdir(path)
