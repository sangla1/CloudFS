#!/usr/bin/env python

from account import *

from s3fs import AmazonS3FS
from dropboxfs import DropboxFS

class Connector:

	def __init__(self):
		self.conns = []
		for item in account:
			if item[0] == 'dropbox':
				self.conns.append(dict(name=item[1], app=DropboxFS(item[2], item[3])))
			elif item[0] == 's3':
				self.conns.append(dict(name=item[1], app=AmazonS3FS(item[2], item[3], item[4])))

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
