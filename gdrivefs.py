import gdata.docs.service
import gdata.docs.client
import gdata.sample_util
import atom.http_core

class Node():
	
	def __init__(self, id, name, isFolder):
		self.id = id
		self.name = name
		self.isFolder = isFolder

	def isFolder(self):
		return isFolder

	def setParent(self, parent):
		self.parent = parent

	def getPath(self):
		if hasattr(self, 'parent') == False:
			return '/' + self.name
		return self.parent.getPath() + '/' + self.name
		#return name


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


	def ls(self, path):
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
				self.nodeDict[id] = nd
			else:
				nd = self.nodeDict[id]

			if self.hasParent(ent):
				prnd = self.getParent(ent)
				if self.nodeDict.has_key(prnd.id) == False:
					self.nodeDict[prnd.id] = prnd
					nd.setParent(prnd)
				else:
					nd.setParent(self.nodeDict[prnd.id])

		if path.startswith('.'):
			path = path[1: ]

		file_list = []

		for node in self.nodeDict:
			col = self.nodeDict[node].getPath()
			if col.startswith(path) and len(col[len(path):]) > 0:
				file_list.append(col[len(path) + 1: ])


		return file_list
				



def main():
	email = 'temptemp678'
	password = 'cloudfs99'
	gdrive = GDriveFS(email, password)
	#gdrive.test()
	print gdrive.ls('./what/haha')


if __name__ == '__main__':
	main()
