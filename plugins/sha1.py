from hashlib import sha1

class Plugin:

	__NAME__ = 'sha1'

	def __init__(self, args):

		self.chunk_size = args.get('chunk_size')
		if self.chunk_size == None:
			self.chunk_size = 4096

	def analyze(self, afile):

		hasher = sha1()
		with open(afile.path, 'rb') as f:
			for chunk in iter(lambda: f.read(self.chunk_size), b""):
				hasher.update(chunk)

		afile.sha1 = hasher.hexdigest()
		afile.plugin_output[self.__NAME__] = afile.sha1