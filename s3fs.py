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
    def __init__(self, bucket_name, key, secret):
        cmd.Cmd.__init__(self)
        self.conn = S3Connection(key, secret)
        self.bucket = self.conn.create_bucket(bucket_name)

    def ls(self, path):
        print "DEBUG Amazon S3 Ls => ", path
        fileNameList = []
        pathCount = path.count('/')
        allKeys = self.bucket.get_all_keys()
        print "LS Debug = ", allKeys
        if len(path) == 1:
            for k in allKeys:
                keyPathCount = k.key.count('/')
                encoding = locale.getdefaultlocale()[1]
                name = ('%s' % k.name).encode(encoding)
                if name[-1:] == '/' and pathCount == keyPathCount:
                    if name.startswith(path[1:]):
                        fileNameList.append(os.path.dirname(name))
                if name[-1:] != '/' and pathCount - 1 == keyPathCount:
                    if name.startswith(path[1:]):
                        fileNameList.append(os.path.basename(name))
        else:
            path = path + '/'
            for k in allKeys:
                encoding = locale.getdefaultlocale()[1]
                name = ('%s' % k.name).encode(encoding)
                name = '/' + name
                if name.startswith(path) and len(name) > len(path):
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
        path = path[1:] # remove first '/'
        path = path + '/'
        k = Key(self.bucket)
        k.key = path
        k.set_contents_from_string('')
        return True

    def rm(self, path):
        attr = self.getFileInfo(path)
        if attr['st_mode'] == (S_IFDIR|0755):
            path = path[1:] # remove first '/'
            path = path + '/'
            print "DEBUG rm => now remove dir key - ", path
            self.bucket.delete_key(path)
        else:
            path = path[1:] # remove first '/'
            self.bucket.delete_key(path)
        return True

    def get(self, from_path):
        attr = self.getFileInfo(from_path)
        data = None
        if attr['st_mode'] != (S_IFDIR|0755):
            k = Key(self.bucket)
            k.key = from_path[1:]
            data = k.get_contents_as_string()
        return data

    def put(self, data, to_path):
        dataStr = ''
        f = open('/tmp/workfile', 'w')
        f.write(data)
        f.close()
        k = Key(self.bucket)
        k.key = to_path[1:]
        k.set_contents_from_filename('/tmp/workfile')

if __name__ == '__main__':
    s3 = AmazonS3FS(amazonkey.key, amazonkey.sec)
    lsResult = s3.ls('/')
    print lsResult
    lsResult = s3.getFileInfo('/TestFolder2')
    print lsResult
