from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

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
				parser = PDFParser(fp)
				doc = PDFDocument(parser)
				#Get metadata from document parser
				meta = doc.info

				for i in meta:
					for k,v in i.iteritems():
						setattr(afile,k,v)	
			
				parser.close()
