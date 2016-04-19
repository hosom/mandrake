from oletools import olevba

class Plugin:

	__NAME__ = 'doc'

	def __init__(self, args):
		self.args = args

	def analyze(self, afile):
		
		if afile.mime_type == 'application/msword':
			parser = olevba.VBA_Parser(afile.path)
			results = parser.analyze_macros()

			for kw_type, keyword, description in results:
				output = 'type: %s keyword: %s description: %s\n' % (kw_type, keyword, description)

			afile.plugin_output[self.__NAME__] = output

			# The parser requires an explicit close
			parser.close()