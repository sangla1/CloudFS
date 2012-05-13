#!/usr/bin/env python

import cmd
import locale
import sys, os

from boto.s3.connection import S3Connection

class AmazonS3FS(cmd.Cmd):
    def __init__(self, key, secret):
        cmd.Cmd.__init__(self)
        self.conn = S3Connection(key, secret)
        self.bucket = self.conn.create_bucket('cloud_fs')

    def ls(self, path):
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
        pathCount = path.count('/')
        allKeys = self.bucket.get_all_keys()
        print "LS Debug = ", allKeys
        for k in allKeys:
            paddedKey = '/' + k.key
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
    s3 = AmazonS3FS('', '')
    lsResult = s3.ls('/')
    print lsResult
    lsResult = s3.ls('/TestFolder2/')
    print lsResult
