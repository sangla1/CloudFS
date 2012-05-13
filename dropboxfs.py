#!/usr/bin/env python

import cmd
import locale
import pprint
import shlex
import sys, os, json

from dropbox import client, rest, session

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
                #self.stdout.write(('%s\n' % name).encode(encoding))

        return fileNameList

    def getFileInfo(self, path):
	print "=========== getFileInfo"
	print path
	print "==========================="
        try:
            resp = self.api_client.metadata(path)
        except rest.ErrorResponse:
            return None
        return resp

    def mkdir(self, path):
        """create a new directory"""
        self.api_client.file_create_folder(path)

    def rm(self, path):
        """delete a file or directory"""
        self.api_client.file_delete(path)

    def get(self, from_path, to_path):
        to_file = open(os.path.expanduser(to_path), "wb")

        f, metadata = self.api_client.get_file_and_metadata(from_path)
        #print 'Metadata:', metadata
        to_file.write(f.read())

    def put(self, from_path, to_path):
        from_file = open(os.path.expanduser(from_path), "rb")

        self.api_client.put_file(to_path, from_file)

if __name__ == '__main__':
    dropbox = DropboxFS(APP_KEY, APP_SECRET)
    #dropbox.mkdir("test_mkdir");
    #dropbox.rmdir("test_mkdir");
    #dropbox.put("dropbox.pyc", "put_dropbox.pyc");
    #dropbox.get("put_dropbox.pyc", "get_from_dropbox.pyc");
    #dropbox.rm("put_dropbox.pyc");
    fileNameList = dropbox.ls("");
    print "ls result = "
    print fileNameList
    #dropbox.put("test.txt", "test.txt");
    #fileInfo = dropbox.getFileInfo("test.txt");
    fileInfo = dropbox.getFileInfo("/test.txt");
    if fileInfo != None:
        print "Created Data = " + fileInfo['modified']
        print "File Size = " + str(fileInfo['bytes'])
    print "FileInfo Dictionary = "
    print fileInfo
    dropbox.get("test.txt", "local.txt");
