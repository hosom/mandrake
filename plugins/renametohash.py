import os

class Plugin:

	def __init__(self, args):
		self.args = args
		self.hash = 'sha1'

	def analyze(self, afile):

		if os.path.exists(afile.path):
			dirname, filename = os.path.split(afile.path)
			ext = filename.split('.')[-1]

			if hasattr(afile, self.hash):
				filehash = getattr(afile, self.hash)

				new_name = '%s.%s' % (filehash, ext)

				new_full_path = '%s/%s' % (dirname, new_name)
				os.rename(afile.path, new_full_path)