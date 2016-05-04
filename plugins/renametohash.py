import os

class Plugin:

	__NAME__ = 'renametohash'

	def __init__(self, args):
		self.args = args

		# Pull the configured hash
		self.hash = self.args.get('hash')
		# If the configured hash is unsupported or unconfigured, use sha1
		if self.hash is not in ['sha1', 'sha256', 'md5']:
			self.hash = 'sha1'

	def analyze(self, afile):
		'''Rename files that have been analyzed to their hash. This is 
		a convenient lazy way to deduplicate the samples that are stored
		on local disk. 

		Note: this will not prevent future samples matching this hash from 
		being processed.

		Args:
			afile (FileAnalysis): The file to be renamed.

		Returns:
			None
		'''
		if os.path.exists(afile.path):
			# Get the current filename
			dirname, filename = os.path.split(afile.path)
			# Get the current file extension
			ext = filename.split('.')[-1]

			# If the file object has been hashed by a previous analyzer
			# use the hash that was calculated to rename the file to the
			# pattern {HASH}.{ext}
			if hasattr(afile, self.hash):
				filehash = getattr(afile, self.hash)
				new_name = '%s.%s' % (filehash, ext)
				new_full_path = '%s/%s' % (dirname, new_name)
				os.rename(afile.path, new_full_path)