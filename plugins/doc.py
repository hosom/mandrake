from oletools import olevba

class Plugin:

	__NAME__ = 'doc'

	def __init__(self, args):
		self.args = args
		self.analyzed_mimes = ['application/msword',
								'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
								'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
								'application/vnd.openxmlformats-officedocument.presentationml.presentation',
								'application/vnd.ms-excel',
								'application/vnd.ms-powerpoint',
								'application/vnd.openxmlformats-officedocument.presentationml.presentation',
								'application/vnd.ms-office']
		self.alert_on_macro = True
		self.suspicious_on_macro = True

	def analyze(self, afile):
		
		if afile.mime_type in self.analyzed_mimes:
			try:
				parser = olevba.VBA_Parser(afile.path)
			except TypeError:
				afile.errors = afile.errors + ['doc plugin: unsupported filetype']
				#afile.errors = afile.errors + ['TypeError']
				output = 'None'
				afile.plugin_output[self.__NAME__] = output
				return

			results = parser.analyze_macros()

			contains_macro = parser.detect_vba_macros()
			if contains_macro and self.alert_on_macro:
				afile.alert = True
			if contains_macro and self.suspicious_on_macro:
				afile.suspicious = True

			output = '' 

			if results is not None:
				for result in results:
					output = output + '[%s] keyword: %s description: %s' % result
			else:
				output = 'None'

			if contains_macro:
				afile.vba = parser.reveal()

			afile.plugin_output[self.__NAME__] = output

			# The parser requires an explicit close
			parser.close()