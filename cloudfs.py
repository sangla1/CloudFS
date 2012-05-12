#!/usr/bin/env python

from collections import defaultdict
from errno import *
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fusepy.fuse import FUSE, FuseOSError, Operations, LoggingMixIn

class CloudFS(LoggingMixIn, Operations):
    
    def __init__(self):
        self.maxFiles = 1024
        self.files = [None] * self.maxFiles
        
    def chmod(self, path, mode):
        raise FuseOSError(EPERM)

    def chown(self, path, uid, gid):
        raise FuseOSError(EPERM)
    
    def create(self, path, mode):
        raise FuseOSError(EPERM)
    
    def getattr(self, path, fh=None):
        now = time()
        if path == '/':            
            return dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2)
        else:
            raise FuseOSError(ENOENT)
    
    def getxattr(self, path, name, position=0):
        raise FuseOSError(EPERM)

    def listxattr(self, path):
        raise FuseOSError(EPERM)
    
    def mkdir(self, path, mode):
        raise FuseOSError(EPERM)
    
    def open(self, path, flags):
        raise FuseOSError(EPERM)
    
    def read(self, path, size, offset, fh):
        raise FuseOSError(EPERM)
    
    def readdir(self, path, fh):
        print 'readdir : ', path, fh
        dents = []
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
    
    def truncate(self, path, length, fh=None):
        raise FuseOSError(EPERM)
    
    def unlink(self, path):
        raise FuseOSError(EPERM)
    
    def utimens(self, path, times=None):
        raise FuseOSError(EPERM)

    def write(self, path, data, offset, fh):
        raise FuseOSError(EPERM)

if __name__ == "__main__":
    if len(argv) != 2:
        print 'usage: %s <mountpoint>' % argv[0]
        exit(1)
    fuse = FUSE(CloudFS(), argv[1], foreground=True)
