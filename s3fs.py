#!/usr/bin/env python

import cmd
import locale
import sys, os
import amazonkey

from boto.s3.key import Key
from boto.s3.connection import S3Connection
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

class AmazonS3FS(cmd.Cmd):
    def __init__(self, key, secret):
        cmd.Cmd.__init__(self)
        self.conn = S3Connection(key, secret)
        self.bucket = self.conn.create_bucket('cloud_fs')

    def ls(self, path):
        print "DEBUG Amazon S3 Ls => ", path
        fileNameList = []
        pathCount = path.count('/')
        allKeys = self.bucket.get_all_keys()
        print "LS Debug = ", allKeys
        for k in allKeys:
            paddedKey = '/' + k.key
            keyPathCount = k.key.count('/')
            encoding = locale.getdefaultlocale()[1]
            name = ('%s' % k.name).encode(encoding)
            if name[-1:] == '/' and pathCount == keyPathCount:
                if name.startswith(path[1:]):
                    fileNameList.append(os.path.dirname(name))
            if name[-1:] != '/' and pathCount - 1 == keyPathCount:
                if name.startswith(path[1:]):
                    fileNameList.append(os.path.basename(name))

        return fileNameList

    def getFileInfo(self, path):
        print "DEBUG Amazon S3 GetFileInfo => ", path
        now = time()
        pathCount = path.count('/')
        if path[0] == '/':
            path = path[1:]
        if path == '':
            attr = dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2)
            return attr

        allKeys = self.bucket.get_all_keys()
        attr = None
        for k in allKeys:
            if k.name[-1:] == '/':
                if k.name == path + '/':
                    attr = dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2)
                    return attr
            if k.name == path:
                attr = dict(st_mode=(S_IFREG | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2, st_size=k.size)
                return attr
        return None

    def mkdir(self, path):
        return None

    def rm(self, path):
        return None

    def get(self, from_path):
        return None

    def put(self, data, to_path):
        return None

if __name__ == '__main__':
    s3 = AmazonS3FS(amazonkey.key, amazonkey.sec)
    lsResult = s3.ls('/')
    print lsResult
    lsResult = s3.getFileInfo('/TestFolder2')
    print lsResult
