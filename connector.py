#!/usr/bin/env python

from dropboxfs import DropboxFS
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

class Connector:

	def __init__(self):
		self.conns = []
		self.conns.append(dict(name='dropbox', app=DropboxFS('vhgangrvc4w2poo', '2xsktxsbhn465mr')))

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
		if connAttr == None:
			return None

		now = time()
		if connAttr['is_dir']:
			attr = dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2)
		else:
			attr = dict(st_mode=(S_IFREG | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2, st_size=connAttr['bytes'])
		
		return attr
	
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
	
	def remove(self):
		nop
