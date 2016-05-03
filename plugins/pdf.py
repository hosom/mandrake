import re
from pdfid import PDFiD2String, PDFiD
class Plugin:

	__NAME__ = 'pdf'

	def __init__(self, args):
		self.args = args
		self.analyzed_mimes = ['application/pdf']


	def analyze(self, afile):
		'''Analyze PDF files and extract metadata about the file into the 
		FileAnalysis object.

		Args:
			afile (FileAnalysis): The file to be analyzed.
		
		Returns:
			None
		'''
		if afile.mime_type in self.analyzed_mimes:

			# Parse the metadata for the pdf file and add all pdf metadata
			# attributes to the FileAnalysis object.
			try:
				fp = open(afile.path)
				output = 'None'
				afile.plugin_output[self.__NAME__] = output
				process_metadata = True
			except IOError:
				afile.errors = afile.errors + ['pdf plugin: unsupported filetype']
				output = 'None'
				afile.plugin_output[self.__NAME__] = output
				process_metadata = False

			if process_metadata:
				# Get string representation of discovered PDF tags
				result = PDFiD2String(PDFiD(afile.path),True)
				# Split off of new lines
				lines = result.split('\n')[1:]
				for line in lines:
					#strip white spaces
					line = line.strip()
					#parse out line into key,value by sequential white spaces
					kv_pair = re.split('\s+',line)
					if len(kv_pair) > 1:
						#remove forward slash
						key = re.sub('/','',kv_pair[0])
						value = kv_pair[1]
						# if we have more than 2 entries then the value was parsed incorrectly, join the other entries in list into one value
						if len(kv_pair) > 2:
							value = ' '.join(kv_pair[1:])
						# set the attribute with our key,value
						setattr(afile,key,value)

