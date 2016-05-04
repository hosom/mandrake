import zipfile
import os

class Plugin:

	__NAME__ = 'zipextract'

	def __init__(self, args):
		self.args = args
		self.max_extracted_files = 100
		self.max_extracted_size = 200
		self.pwd = 'infected'


	def analyze(self, afile):

		if afile.mime_type == 'application/zip':
			#dirname, filename = os.path.split(afile.path)
			total_size = 0
			with zipfile.ZipFile(afile.path) as f:
				container_files = f.namelist()
				if len(container_files) > self.max_extracted_files:
					print('Error! Too many files!')
				for fname in container_files:
					total_size = total_size + f.getinfo(fname).file_size