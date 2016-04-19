import magic

class Plugin:

	__NAME__ = 'filemagic'

	def __init__(self, args):

		self.args = args

	def analyze(self, afile):

		afile.mime_type = magic.from_file(afile.path, mime=True)
		afile.plugin_output[self.__NAME__] = afile.mime_type