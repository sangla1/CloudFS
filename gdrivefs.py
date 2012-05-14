import gdata.docs.service
import gdata.docs.client
import gdata.sample_util
import atom.http_core
import gdata.docs.data
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time
import re
import mimetypes

class Node():
	
	def __init__(self, id, name, isFolder):
		self.id = id
		self.name = name
		self.isFolder = isFolder

	def isFolder(self):
		return isFolder

	def setParent(self, parent):
		self.parent = parent

	def setResource(self, resource):
		self.resource = resource

	def getPath(self):
		if hasattr(self, 'parent') == False:
			return '/' + self.name
		return self.parent.getPath() + '/' + self.name
		#return name

	def setSize(self, size):
		self.size = size	


class GDriveFS():

	def __init__(self, email, password):
		source = 'Doc List '
		self.client = gdata.docs.client.DocsClient(source=source)
		self.client.client_login(email, password, source=self.client.source, service=self.client.auth_service) 
		source = 'Doc List'
		self.cl = gdata.client.GDClient(source=source)
		self.cl.host = 'docs.google.com'
		self.cl.api_version = '3.0'
		self.cl.auth_service = 'writely'
		self.cl.ssl = True
		self.cl.client_login(email, password, source=source, service='writely') 
		mimetypes.init()
		self.refresh()

	def refresh(self):
		self.nodeDict = {}
		RESOURCE_FEED_URI = '/feeds/default/private/full/'
		uri = RESOURCE_FEED_URI
		uri = atom.http_core.Uri.parse_uri(uri) 
		uri.query['showfolders'] = 'true'
	
		ch = self.cl.get_feed(uri, desired_class=gdata.docs.data.ResourceFeed)

		root = Node('', '/', True)

		for ent in ch.entry:

			id = ent.id.text[ent.id.text.find('id/')+3: ]

			trueorfalse = False
			if self.isFolder(ent):
				trueorfalse = True
			else:
				trueorfalse = False

			if self.nodeDict.has_key(id) == False:
				nd = Node(id, ent.title.text, trueorfalse)
				if int(ent.quota_bytes_used.text) == 0 and trueorfalse == False:
					self.client.download_revision(ent, '/tmp/workfile')
					f = open('/tmp/workfile', 'r')
					data = f.read()
					f.close()
					te = data
					if ent.title.text.endswith('.txt'):
						st = te.find('<span>')	
						ed = te.find('</span></p>')
						nd.setSize(ed - st)

				else:
					nd.setSize(int(ent.quota_bytes_used.text))

				self.nodeDict[id] = nd
			else:
				nd = self.nodeDict[id]

			nd.setResource(ent)

			if self.hasParent(ent):
				prnd = self.getParent(ent)
				if self.nodeDict.has_key(prnd.id) == False:
					self.nodeDict[prnd.id] = prnd
					nd.setParent(prnd)
				else:
					nd.setParent(self.nodeDict[prnd.id])


	def isFolder(self, entry):
		for cat in entry.category:
			if cat.label == 'folder':
				return True

		return False

	def notRoot(self, entry):
		chk = 0
		for link in ent.link:
			if link.rel.endswith('parent'):
				chk = 1
				break
		if chk == 1:
			print e2

	def hasParent(self, entry):
		chk = 0
		for link in entry.link:
			if link.rel.endswith('parent'):
				return True

		return False

	def getParent(self, entry):
		chk = 0
		for link in entry.link:
			if link.rel.endswith('parent'):
				return Node(link.href[link.href.find('/folder') + 1: ], link.title, True)

		return '' 
	
	def getFileInfo(self, path):
		print 'getFileInfo ', path
		self.refresh()
		now = time()
		if path == '/':
			return dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2)
		for node in self.nodeDict:
			if self.nodeDict[node].getPath() == path:
				if self.nodeDict[node].isFolder:
					return dict(st_mode=(S_IFDIR | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2, st_size=4096)
				return dict(st_mode=(S_IFREG | 0755), st_ctime=now, st_mtime=now, st_atime=now, st_nlink=2, st_size=self.nodeDict[node].size)
		return None

	def ls(self, path):
		print 'ls ', path
		self.nodeDict = {}
		RESOURCE_FEED_URI = '/feeds/default/private/full/'
		uri = RESOURCE_FEED_URI
		uri = atom.http_core.Uri.parse_uri(uri) 
		uri.query['showfolders'] = 'true'
	
		ch = self.cl.get_feed(uri, desired_class=gdata.docs.data.ResourceFeed)

		root = Node('', '/', True)

		for ent in ch.entry:

			id = ent.id.text[ent.id.text.find('id/')+3: ]

			trueorfalse = False
			if self.isFolder(ent):
				trueorfalse = True
			else:
				trueorfalse = False

			if self.nodeDict.has_key(id) == False:
				nd = Node(id, ent.title.text, trueorfalse)
				if int(ent.quota_bytes_used.text) == 0 and trueorfalse == False:
					self.client.download_revision(ent, '/tmp/workfile')
					f = open('/tmp/workfile', 'r')
					data = f.read()
					f.close()
					te = data
					if ent.title.text.endswith('.txt'):
						st = te.find('<span>')	
						ed = te.find('</span></p>')
						nd.setSize(ed - st)

				else:
					nd.setSize(int(ent.quota_bytes_used.text))
				self.nodeDict[id] = nd
			else:
				nd = self.nodeDict[id]

			nd.setResource(ent)

			if self.hasParent(ent):
				prnd = self.getParent(ent)
				if self.nodeDict.has_key(prnd.id) == False:
					self.nodeDict[prnd.id] = prnd
					nd.setParent(prnd)
				else:
					nd.setParent(self.nodeDict[prnd.id])

		if path.startswith('.'):
			path = path[1: ]

#		if path == '/':
#			path = path[1: ]

		file_list = []

		for node in self.nodeDict:
			col = self.nodeDict[node].getPath()
#			print path, col
			if col.startswith(path) and len(col[len(path):]) > 0 and col[len(path)+1:].find('/') == -1:
				if path == '/':
					file_list.append(col[len(path): ])
				else:
					file_list.append(col[len(path) + 1: ])

		return file_list
				

	def rm(self, path):
		print 'rm ', path
		self.refresh()
		if path.startswith('.'):
			path = path[1: ]

		for node in self.nodeDict:
			col = self.nodeDict[node].getPath()
			if col == path:
				self.cl.delete(self.nodeDict[node].resource)
				self.refresh()
				return True
		return False

	def mkdir(self, path):
		print 'mkdir ', path
		self.refresh()
		pa = path[: -path[::-1].find('/')-1]
		name = path[len(pa)+1: ]
		col = gdata.docs.data.Resource(type='folder', title=name)

		if '/' + name == path:
			self.client.create_resource(col)
			self.refresh()
			return True
		else:
			for node in self.nodeDict:
				if self.nodeDict[node].isFolder and self.nodeDict[node].getPath() == pa:
					self.client.CreateResource(col, collection=self.nodeDict[node].resource)
					self.refresh()
					return True

		return False
		

	def get(self, path):
		print 'get ', path
		self.refresh()
		for node in self.nodeDict:
			if self.nodeDict[node].isFolder == False and self.nodeDict[node].getPath() == path:
				self.client.download_revision(self.nodeDict[node].resource, '/tmp/workfile')
				f = open('/tmp/workfile', 'r')
				data = f.read()
				f.close()
				if path.endswith('.txt'):
					st = data.find('<span>')	
					ed = data.find('</span></p>')
					#print st, ed
					return data[st+6: ed: ]
				return data
#		return self.client.download_resource_to_memory(self.nodeDict[node].resource)


	def put(self, data, path):
		print 'put ', path
#		print 'data', data
		print len(data)
		if len(data) == 0:
			data = ' '
		else:
			self.rm(path)	
		self.refresh()
		pa = path[: -path[::-1].find('/')-1]
		name = path[len(pa)+1: ]
		res = gdata.docs.data.Resource(type='file', title=name)
		f = open('/tmp/workfile', 'w')
		f.write(data)
		f.close()

		ext = name[name.find('.'): ].lower()

		type = mimetypes.types_map[ext]
		print type

		ms = gdata.MediaSource(file_path='/tmp/workfile', content_type=type) 

		if '/' + name == path:
			self.client.create_resource(res, media=ms)
		else:
			for node in self.nodeDict:
				if self.nodeDict[node].isFolder and self.nodeDict[node].getPath() == pa:
					self.client.create_resource(res, media=ms, collection=self.nodeDict[node].resource)
		self.refresh()
		

def main():
	email = 'temptemp678'
	password = 'cloudfs99'
	gdrive = GDriveFS(email, password)
	gdrive.getFileInfo('/')
	#print gdrive.ls('/')
	f = open('./test.txt', 'r')
	data = f.read()
	f.close()
#	gdrive.put(data, '/test.txt')
#	gdrive.mkdir('/what/haha/new')
#	gdrive.rm('./crane.txt')
#	print gdrive.ls('./what/haha')
	print gdrive.mkdir('/bbb')


if __name__ == '__main__':
	main()
