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

class Dropbox(cmd.Cmd):
    def __init__(self, app_key, app_secret):
        cmd.Cmd.__init__(self)
        state = load_state()
        access_token = state['access_token']

        self.sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        self.sess.set_token(*access_token)
        self.api_client = client.DropboxClient(self.sess)
        self.current_path = ''

    def do_ls(self, path):
        """list files in current remote directory"""
        print "Current Path = " + self.current_path + path
        resp = self.api_client.metadata(self.current_path + path)

        if 'contents' in resp:
            for f in resp['contents']:
                name = os.path.basename(f['path'])
                encoding = locale.getdefaultlocale()[1]
                self.stdout.write(('%s\n' % name).encode(encoding))

if __name__ == '__main__':
    dropbox = Dropbox(APP_KEY, APP_SECRET)
    dropbox.do_ls("");
