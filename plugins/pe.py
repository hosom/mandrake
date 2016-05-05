import pefile
import peutils

from datetime import datetime

class Plugin:
	
	__NAME__ = 'pe'

	def __init__(self, args):

		self.args = args

	def analyze(self, afile):
		'''Analyze the Windows portable executable format.

		ref: https://en.wikipedia.org/wiki/Portable_Executable

		Args: 
			afile (FileAnalysis): Mandrake file analysis object.

		Returns:
			None
		'''
		if afile.mime_type == 'application/x-dosexec':
			try:
				pe = pefile.PE(afile.path)
			except:
				afile.errors = afile.errors + ['pe plugin: unsupported filetype']
				output = 'None'
				afile.plugin_output[self.__NAME__] = output
				return

			# Collect interesting flags from the binary
			# Allows >32 bit values for ASLR
			afile.high_entropy_aslr = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA
			afile.uses_aslr = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE
			afile.force_integrity = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY
			# DEP
			afile.uses_dep = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_NX_COMPAT
			afile.force_no_isolation = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_NO_ISOLATION
			afile.uses_seh = not pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_NO_SEH
			afile.no_bind = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_NO_BIND
			afile.app_container = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_APPCONTAINER
			afile.wdm_driver = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_WDM_DRIVER
			afile.uses_cfg = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_GUARD_CF
			afile.terminal_server_aware = pe.OPTIONAL_HEADER.IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE

			# Determine whether the pe file is likely to be packed
			afile.is_probably_packed = peutils.is_probably_packed(pe)

			# Attach pe parser warnings
			afile.warnings = pe.get_warnings()

			# This method determines whether or not the binary is a dll
			afile.is_dll = pe.is_dll()
			afile.is_exe = pe.is_exe()
			afile.is_driver = pe.is_driver()

			# Does the checksum check out?
			afile.verify_checksum = pe.verify_checksum()

			# Determine the compile date of a binary
			compile_date = datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp)
			afile.compile_date = compile_date

			# Compute / retrieve the imphash
			afile.imphash = pe.get_imphash()

			# Parse out the import table from within the pe file
			imports = {}
			if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
				afile.has_import_table = True
				for entry in pe.DIRECTORY_ENTRY_IMPORT:
					imports[entry.dll] = []
					for imp in entry.imports:
						imports[entry.dll].append(imp.name)

				afile.imports = imports

			# Parse out the export table listed within the pe file
			exports = []
			if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
				afile.has_export_table = True
				for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols:
					exports.append(entry.name)

				afile.exports = exports

			pe.close()