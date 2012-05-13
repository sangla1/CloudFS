#!/usr/bin/env python

from collections import defaultdict
from errno import *
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fusepy.fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from connector import Connector

class CloudFS(LoggingMixIn, Operations):
	
	def __init__(self):
		self.maxFiles = 1024
		self.files = [dict(path=None, dirty=False, data=None)] * self.maxFiles
		self.conn = Connector()
		
	def chmod(self, path, mode):
		raise FuseOSError(EPERM)

	def chown(self, path, uid, gid):
		raise FuseOSError(EPERM)
	
	def create(self, path, mode):
		paths = splitPath(path)
		print path, paths
		if paths[0] == '':
			raise FuseOSError(EPERM)

		fd = None
		fdNum = 0		
		for i in range(0, self.maxFiles):
			fd = self.files[i]
			if fd['path'] == None:
				fdNum = i
				break

		if fd == None:
			raise FuseOSError(ENOENT)

		fd['path'] = path
		fd['dirty'] = False
		fd['data'] = ''

		paths = splitPath(path)
		self.conn.push(paths[0], paths[1], fd['data'])

		return fdNum
	
	def getattr(self, path, fh=None):
		now = time()
		paths = splitPath(path)
		if paths[0] == '':
			return dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2)

		attr = self.conn.getAttr(paths[0], paths[1])
		if attr != None:
			return attr
		else:
			raise FuseOSError(ENOENT)
	
	def getxattr(self, path, name, position=0):
		return {}

	def listxattr(self, path):
		raise FuseOSError(EPERM)
	
	def mkdir(self, path, mode):
		paths = splitPath(path)
		if paths[1] == '':
			raise FuseOSError(EPERM)
		if self.conn.mkdir(paths[0], paths[1]) != True:
			raise FuseOSError(EPERM)
	
	def open(self, path, flags):
		paths = splitPath(path)
		print path, paths
		if paths[0] == '':
			raise FuseOSError(EPERM)

		content = self.conn.pull(paths[0], paths[1])
		if paths[0] == None:
			raise FuseOSError(ENOENT)

		fd = None
		fdNum = 0		
		for i in range(0, self.maxFiles):
			fd = self.files[i]
			if fd['path'] == None:
				fdNum = i
				break

		if fd == None:
			raise FuseOSError(ENOENT)

		fd['path'] = path
		fd['dirty'] = False
		fd['data'] = content

		return fdNum
	
	def read(self, path, size, offset, fh):
		if self.files[fh]['path'] == None:
			raise FuseOSError(ENOENT)
		return self.files[fh]['data'][offset:offset + size]
	
	def readdir(self, path, fh):
		print 'readdir : ', path, fh
		paths = splitPath(path)
		print paths
		if paths[0] == '':
			dents = self.conn.getConns()
		else:
			dents = self.conn.getDents(paths[0], paths[1])

		return ['.', '..'] + dents
	
	def readlink(self, path):
		raise FuseOSError(EPERM)
	
	def removexattr(self, path, name):
		raise FuseOSError(EPERM)
	
	def rename(self, old, new):
		raise FuseOSError(EPERM)
	
	def rmdir(self, path):
		raise FuseOSError(EPERM)
	
	def setxattr(self, path, name, value, options, position=0):
		raise FuseOSError(EPERM)

	def statfs(self, path):
		raise FuseOSError(EPERM)
	
	def symlink(self, target, source):
		raise FuseOSError(EPERM)
	
	def truncate(self, path, length, fh=0):
		fd = self.files[self.open(path, 0)]
		fd['dirty'] = True
		fd['data'] = fd['data'][:length]
	
	def unlink(self, path):
		raise FuseOSError(EPERM)
	
	def utimens(self, path, times=None):
		raise FuseOSError(EPERM)

	def write(self, path, data, offset, fh):
		fd = self.files[fh]
		if fd['path'] == None:
			raise FuseOSError(ENOENT)

		fd['data'] = fd['data'][:offset] + data
		fd['dirty'] = True
		
		return len(data)

	def release(self, path, fh):
		fd = self.files[fh]
		if fd['path'] == None:
			raise FuseOSError(ENOENT)

		if fd['dirty'] == True:
			paths = splitPath(path)
			self.conn.push(paths[0], paths[1], fd['data'])

		fd['path'] = None
		fd['dirty'] = False
		fd['data'] = None

def splitPath(path):
	s = path.split('/')
	return [s[1], '/' + '/'.join(s[2:])]
		

if __name__ == "__main__":
	if len(argv) != 2:
		print 'usage: %s <mountpoint>' % argv[0]
		exit(1)
	fuse = FUSE(CloudFS(), argv[1], foreground=True)
