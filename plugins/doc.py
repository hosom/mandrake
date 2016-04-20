from oletools import olevba

class Plugin:

	__NAME__ = 'doc'

	def __init__(self, args):
		self.args = args
		self.analyzed_mimes = ['application/msword',
								'application/vnd.ms-office']
		self.alert_on_macro = True
		self.suspicious_on_macro = True

	def analyze(self, afile):
		
		if afile.mime_type in self.analyzed_mimes:
			parser = olevba.VBA_Parser(afile.path)
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

			afile.vba = parser.reveal()

			afile.plugin_output[self.__NAME__] = output

			# The parser requires an explicit close
			parser.close()