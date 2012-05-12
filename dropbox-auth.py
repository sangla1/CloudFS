import dropbox
import sys, os, json

APP_KEY = 'vhgangrvc4w2poo'
APP_SECRET = '2xsktxsbhn465mr'
ACCESS_TYPE = 'app_folder'

STATE_FILE = 'cloud_fs.json'

def command_link():
    sess = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
    request_token = sess.obtain_request_token()

    # Make the user log in and authorize this token
    url = sess.build_authorize_url(request_token)
    sys.stdout.write("1. Go to: %s\n" % url)
    sys.stdout.write("2. Authorize this app.\n")
    sys.stdout.write("After you're done, press ENTER.\n")
    raw_input()

    # This will fail if the user didn't visit the above URL and hit 'Allow'
    access_token = sess.obtain_access_token(request_token)
    sys.stdout.write("Link successful.\n")

    save_state({
        'access_token': (access_token.key, access_token.secret),
        'tree': {}
    })

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

def save_state(state):
    f = open(STATE_FILE, 'w')
    state['tree'] = Node.to_json_content(state['tree'])
    json.dump(state, f, indent=4)
    f.close()

if __name__ == '__main__':
    command_link()
