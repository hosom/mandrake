import zipfile
import os

class Plugin:

	__NAME__ = 'zipextract'

	def __init__(self, args):
		self.args = args

		try:
			self.max_extracted_files = int(args.get('max_extracted_files'))
		except (TypeError, ValueError) as e:
			# Default max extracted files is 30
			self.max_extracted_files = 30

		try:
			self.max_extracted_size = int(args.get('max_extracted_size'))
		except (TypeError, ValueError) as e:
			# Default max extracted size is 50 MB
			self.max_extracted_size = 50000000
		
		self.pwd = args.get('pwd')
		if self.pwd == None:
			self.pwd = 'infected'


	def analyze(self, afile):
		'''Analyze and extract zip files.

		Because zip files are HARD, some limitations will exist.

		Args:
			afile (FileAnalysis): The file to be analyzed.
		
		Returns:
			None
		'''
		abort = False
		if afile.mime_type == 'application/zip':
			with zipfile.ZipFile(afile.path) as z:
				# The filenames included in this zip file
				afile.contained_files = z.namelist()
				# Check for too many files. Extracting too many files could
				# result in a huge number of issues.
				afile.contained_file_count = len(afile.contained_files)
				if afile.contained_file_count > self.max_extracted_files:
					afile.errors = afile.errors + ['zipextract: too many contained files']
					abort = True
				# Check for maximum extracted file size. Extracting files 
				# to the disk is also a problem.
				afile.extracted_size = 0
				for info in z.infolist():
					afile.extracted_size = afile.extracted_size + info.file_size
					if afile.extracted_size > self.max_extracted_size:
						afile.errors = afile.errors + ['zipextract: extracted size too big']
						abort = True
				# If the file does not hit any of the filters for problematic
				# zip files, then continue on and extract the contained files.
				if not abort:
					dirname, filename = os.path.split(afile.path)
					for fname in afile.contained_files:
						# It turns out, the ZipFile module is smart enough to
						# know whether or not a password is needed, so always
						# passing a password is the easiest way to handle this
						try:
							z.extract(fname, dirname, pwd=self.pwd)
						except RuntimeError as e:
							afile.errors = afile.errors + ['zipextract: %s' % (e[0])]
