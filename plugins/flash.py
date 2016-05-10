from swf.movie import SWF
import re

class Plugin:

        __NAME__ = 'flash'

        def __init__(self, args):
                self.args = args
                self.analyzed_mimes = ['application/x-shockwave-flash']


        def analyze(self, afile):
                '''Analyze SWF files and extract metadata about the file into the 
                FileAnalysis object.

                Args:
                        afile (FileAnalysis): The file to be analyzed.
                
                Returns:
                        None
                '''
		
		if afile.mime_type in self.analyzed_mimes:
			# Parse the metadata for the swf file and add all swf metadata
                        # attributes to the FileAnalysis object.
			try:
                        	fp = open(afile.path,'rb')
				swf = SWF(fp)
                                process_metadata = True
                        except IOError:
                                afile.errors = afile.errors + ['swf plugin: unsupported filetype']
                                afile.plugin_output[self.__NAME__] = 'None'
                                process_metadata = False

                       	if process_metadata:
				tag_list = list()
				for tag in swf.tags:
					if tag.name == 'FileAttributes':
						setattr(afile,'useDirectBlit',tag.useDirectBlit)
						setattr(afile,'useGPU',tag.useGPU)
						setattr(afile,'hasMetadata',tag.hasMetadata)
						setattr(afile,'actionscript3',tag.actionscript3)
						setattr(afile,'useNetwork',tag.useNetwork)

					elif tag.name == 'Metadata':
						# Iterate through xml tags and pass to regex search to easily pull out value. 
						xml_tags = ['format','title','description','publisher','creator','language','date']
						for xt in xml_tags:
							search = re.search(r'<dc:'+xt+'>(.*)</dc:'+xt+'>',tag.xmlString,re.M|re.I)
							if search:
								setattr(afile,xt,search.group(1))
								if xt == 'title':
									afile.plugin_output[self.__NAME__] = search.group(1)

					elif tag.name == 'TagScriptLimits':
						setattr(afile,'MaxRecursionDepth',tag.maxRecursionDepth)
						setattr(afile,'ScriptTimeout',tag.scriptTimeoutSeconds)

					elif tag.name == 'TagExportAssets':
						setattr(afile,'Exports',tag.exports)
 
