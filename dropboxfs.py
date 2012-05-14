#!/usr/bin/env python

import cmd
import locale
import pprint
import shlex
import sys, os, json

from dropbox import client, rest, session
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

APP_KEY = 'vhgangrvc4w2poo'
APP_SECRET = '2xsktxsbhn465mr'
ACCESS_TYPE = 'app_folder'

STATE_FILE = 'cloud_fs.json'

class Node(object):
    def __init__(self, path, content):
        # The "original" path (i.e. not the lower-case path)
        self.path = path
        # For files, content is a pair (size, modified)
        # For folders, content is a dict of children Nodes, keyed by lower-case file names.
        self.content = content
    def is_folder(self):
        return isinstance(self.content, dict)
    def to_json(self):
        return (self.path, Node.to_json_content(self.content))
    @staticmethod
    def from_json(jnode):
        path, jcontent = jnode
        return Node(path, Node.from_json_content(jcontent))
    @staticmethod
    def to_json_content(content):
        if isinstance(content, dict):
            return dict([(name_lc, node.to_json()) for name_lc, node in content.iteritems()])
        else:
            return content
    @staticmethod
    def from_json_content(jcontent):
        if isinstance(jcontent, dict):
            return dict([(name_lc, Node.from_json(jnode)) for name_lc, jnode in jcontent.iteritems()])
        else:
            return jcontent

def load_state():
    if not os.path.exists(STATE_FILE):
        sys.stderr.write("ERROR: Couldn't find state file %r.  Run the \"link\" subcommand first.\n" % (STATE_FILE))
        sys.exit(1)
    f = open(STATE_FILE, 'r')
    state = json.load(f)
    state['tree'] = Node.from_json_content(state['tree'])
    f.close()
    return state

class DropboxFS(cmd.Cmd):
    def __init__(self, app_key, app_secret):
        cmd.Cmd.__init__(self)
        state = load_state()
        access_token = state['access_token']

        self.sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        self.sess.set_token(*access_token)
        self.api_client = client.DropboxClient(self.sess)

    def ls(self, path):
        """list files in current remote directory"""
        "LS => input path = " + path
        fileNameList = []
        try:
            resp = self.api_client.metadata(path)
        except rest.ErrorResponse:
            return None

        if 'contents' in resp:
            for f in resp['contents']:
                name = os.path.basename(f['path'])
                encoding = locale.getdefaultlocale()[1]
                name = ('%s' % name).encode(encoding)
                fileNameList.append(name)
        return fileNameList

    def getFileInfo(self, path):
        print "getFileInfo Called ====> ", path
        try:
            resp = self.api_client.metadata(path)
        except rest.ErrorResponse:
            return None
        now = time()
        if resp['is_dir']:
            attr = dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2)
        else:
            attr = dict(st_mode=(S_IFREG | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2, st_size=resp['bytes'])
        return attr

    def mkdir(self, path):
        """create a new directory"""
        try:
            self.api_client.file_create_folder(path)
            return True
        except rest.ErrorResponse:
            return False

    def rm(self, path):
        """delete a file or directory"""
        try:
            self.api_client.file_delete(path)
            return True
        except rest.ErrorResponse:
            return False

    def get(self, from_path):
        f, metadata = self.api_client.get_file_and_metadata(from_path)
        byte = metadata['bytes']
        data = f.read(byte)
        return data

    def put(self, data, to_path):
        if self.getFileInfo(to_path) != None:
            self.rm(to_path)
        dataStr = ''
        f = open('/tmp/workfile', 'w')
        f.write(data)
        f.close()
        from_file = open(os.path.expanduser('/tmp/workfile'), "rb")
        self.api_client.put_file(to_path, from_file)

if __name__ == '__main__':
    dropbox = DropboxFS(APP_KEY, APP_SECRET)
    #dropbox.mkdir("test_mkdir");
    #dropbox.rmdir("test_mkdir");
    #dropbox.put("dropbox.pyc", "put_dropbox.pyc");
    #dropbox.get("put_dropbox.pyc", "get_from_dropbox.pyc");
    #dropbox.rm("put_dropbox.pyc");
    #fileNameList = dropbox.ls("");
    #print "ls result = "
    #print fileNameList
    #dropbox.put("test.txt", "test.txt");
    #fileInfo = dropbox.getFileInfo("test.txt");
    #fileInfo = dropbox.getFileInfo("/test.txt");
    #if fileInfo != None:
    #    print "Created Data = " + fileInfo['modified']
    #    print "File Size = " + str(fileInfo['bytes'])
    #print "FileInfo Dictionary = "
    #print fileInfo
    #dropbox.get("/test.txt");
    #dropbox.put("Hello World!\n", "/helloworld.txt")
    result = dropbox.mkdir("/test")
    print "mkdir /test result = " + str(result)
    #result = dropbox.rm("/test")
    #print "rmdir /test result = " + str(result)

