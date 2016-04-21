import pefile
import peutils

from datetime import datetime

class Plugin:
	
	__NAME__ = 'pe'

	def __init__(self, args):

		self.args = args

	def analyze(self, afile):

		if afile.mime_type == 'application/x-dosexec':
			try:
				pe = pefile.PE(afile.path)
			except:
				afile.errors = afile.errors + ['pe plugin: unsupported filetype']
				output = 'None'
				afile.plugin_output[self.__NAME__] = output
				return

			is_dll = pe.is_dll()
			afile.is_dll = is_dll

			compile_date = datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp)
			afile.compile_date = compile_date

			imports = {}
			if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
				for entry in pe.DIRECTORY_ENTRY_IMPORT:
					imports[entry.dll] = []
					for imp in entry.imports:
						imports[entry.dll].append(imp.name)

				afile.imports = imports

			exports = []
			if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
				for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols:
					exports.append(entry.name)

				afile.exports = exports

			pe.close()