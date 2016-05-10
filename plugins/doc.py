from oletools import olevba
from oletools.thirdparty import olefile

class Plugin:

	__NAME__ = 'doc'

	def __init__(self, args):
		self.args = args
		self.analyzed_mimes = ['application/msword',
								'application/vnd.ms-excel',
								'application/vnd.ms-powerpoint',
								'application/vnd.ms-office']
		self.alert_on_macro = True
		self.suspicious_on_macro = True

	def analyze(self, afile):
		'''Analyze OLE files and extract metadata about the file into the 
		FileAnalysis object.

		Args:
			afile (FileAnalysis): The file to be analyzed.
		
		Returns:
			None
		'''
		if afile.mime_type in self.analyzed_mimes:

			# Parse the metadata for the ole file and add all ole metadata
			# attributes to the FileAnalysis object. This should add a ton
			# of contectual information to the file.
			try:
				ole = olefile.OleFileIO(afile.path)
				process_metadata = True
			except IOError:
				afile.errors = afile.errors + ['doc plugin: unsupported filetype']
				output = 'None'
				afile.plugin_output[self.__NAME__] = output
				process_metadata = False
			# There are OLE files out there with LOTS of embedded objects.
			# This should prevent plugin crashes for those cases.
			except RuntimeError:
				afile.errors = afile.errors + ['doc plugin: max recursion reached']
				output = 'None'
				process_metadata = False
				afile.suspicious = True
				process_metadata = False

			if process_metadata:
				meta = ole.get_metadata()
				# These loops iterate through the meta for attributes and then 
				# set attributes with the same name in the FileAnalysis object
				for prop in meta.SUMMARY_ATTRIBS:
					value = getattr(meta, prop)
					setattr(afile, prop, value)

				for prop in meta.DOCSUM_ATTRIBS:
					value = getattr(meta, prop)
					setattr(afile, prop, value)

				# Thumbnails are binary streams and muck up the output so they
				# are removed. This is a temporary work-around... the doc 
				# analyzer will be rewritten to accomidate things like this
				if hasattr(afile, 'thumbnail'):
					afile.has_thumbnail = True
					del afile.thumbnail

				# Explicitly call close to ensure that the ole object gets closed
				ole.close()

			# Parse the file again, this time looking for VBA scripts.
			try:
				parser = olevba.VBA_Parser(afile.path)
			except TypeError:
				afile.errors = afile.errors + ['doc plugin: unsupported filetype']
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