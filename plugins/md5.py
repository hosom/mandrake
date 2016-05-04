from hashlib import md5

class Plugin:

	__NAME__ = 'md5'

	def __init__(self, args):

		try:
			self.chunk_size = int(args.get('chunk_size'))
		except (TypeError, ValueError) as e:
			self.chunk_size = 4096

	def analyze(self, afile):
		'''Hash the analyzed file. 

		Args:
			afile (FileAnalysis): The file to be analyzed.
		
		Returns:
			None
		'''
		hasher = md5()
		with open(afile.path, 'rb') as f:
			for chunk in iter(lambda: f.read(self.chunk_size), b""):
				hasher.update(chunk)

			afile.md5 = hasher.hexdigest()
			afile.plugin_output[self.__NAME__] = afile.md5