import sys, os.path, re
import StringIO
import xml.etree.ElementTree as ET
from lxml import etree
from pdfminer.psparser import PSKeyword, PSLiteral
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import PDFObjectNotFound
from pdfminer.pdftypes import PDFStream, PDFObjRef
from pdfminer.utils import isnumber
from pdfid import PDFiD2String, PDFiD #Source code for pdfid put in public domain by Didier Stevens, no Copyright



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


        '''The following functions adapted and modified from pdfminer utility dumppdf.py, they are responsible for building XML structure from PDF objects

            e
            dumpxml
            dumptrailers
            dumpallobjs
        '''
        ESC_PAT = re.compile(r'[\000-\037&<>()"\042\047\134\177-\377]')
        def e(s):
            return ESC_PAT.sub(lambda m:'&#%d;' % ord(m.group(0)), s)


        # dumpxml
        def dumpxml(out, obj, codec=None):
            if obj is None:
                out.write('<null />')
                return

            if isinstance(obj, dict):
                out.write('<dict size="%d">\n' % len(obj))
                for (k,v) in obj.iteritems():
                    out.write('<key>%s</key>\n' % k)
                    out.write('<value>')
                    dumpxml(out, v)
                    out.write('</value>\n')
                out.write('</dict>')
                return

            if isinstance(obj, list):
                out.write('<list size="%d">\n' % len(obj))
                for v in obj:
                    dumpxml(out, v)
                    out.write('\n')
                out.write('</list>')
                return

            if isinstance(obj, str):
                out.write('<string size="%d">%s</string>' % (len(obj), e(obj)))
                return

            if isinstance(obj, PDFStream):
                if codec == 'raw':
                    out.write(obj.get_rawdata())
                elif codec == 'binary':
                    out.write(obj.get_data())
                else:
                    out.write('<stream>\n<props>\n')
                    dumpxml(out, obj.attrs)
                    out.write('\n</props>\n')
                    if codec == 'text':
                        data = obj.get_data()
                        out.write('<data size="%d">%s</data>\n' % (len(data), e(data)))
                    out.write('</stream>')
                return

            if isinstance(obj, PDFObjRef):
                out.write('<ref id="%d" />' % obj.objid)
                return

            if isinstance(obj, PSKeyword):
                out.write('<keyword>%s</keyword>' % obj.name)
                return

            if isinstance(obj, PSLiteral):
                out.write('<literal>%s</literal>' % obj.name)
                return

            if isnumber(obj):
                out.write('<number>%s</number>' % obj)
                return

            raise TypeError(obj)

        # dumptrailers
        def dumptrailers(out, doc):
            for xref in doc.xrefs:
                out.write('<trailer>\n')
                dumpxml(out, xref.trailer)
                out.write('\n</trailer>\n\n')
            return

        # dumpallobjs
        def dumpallobjs(out, doc, codec=None):
            visited = set()
            out.write('<pdf>')
            for xref in doc.xrefs:
                for objid in xref.get_objids():
                    if objid in visited: continue
                    visited.add(objid)
                    try:
                        obj = doc.getobj(objid)
                        if obj is None: continue
                        out.write('<object id="%d">\n' % objid)
                        dumpxml(out, obj, codec=codec)
                        out.write('\n</object>\n\n')
                    except PDFObjectNotFound as e:
                        print >>sys.stderr, 'not found: %r' % e
            dumptrailers(out, doc)
            out.write('</pdf>')
            return out.getvalue()

        #leverages pdfid to print out a counted summary of discovered tags in PDF file
        def pdf_id(afile):
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

        if afile.mime_type in self.analyzed_mimes:

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

            # Parse the metadata for the pdf file and add all pdf metadata
            # attributes to the FileAnalysis object.
            if process_metadata:

                # count out PDF tags using pdfid and set attributes
                try:
                    pdf_id(afile)
                except:
                    aile.errors = afile.errors + ['pdf plugin: pdfid failed to parse PDF document']

                #get metadata information and update analysis object
                try:
                    parser = PDFParser(fp)
                    doc = PDFDocument(parser,'')
                    if doc.info:
                        info = doc.info[0]
                        for k,v in info.iteritems():
                            setattr(afile,k,v)


                    #Get XML representation of PDF document
                    xml_io = StringIO.StringIO()
                    xml_str = dumpallobjs(xml_io,doc,None)
                    xml_io.close()

                except:
                    afile.errors = afile.errors + ['pdf plugin: pdfminer failed to parse PDF document']


                #Go through XML and grab all string tags. This will contain embedded links, javascript, titles useful to enrich meaning behind pdfid findings
                try:
                    #pass recover=True so element tree can parse unfriendly xml characters from PDF extract
                    parser = etree.XMLParser(recover=True)
                    xml = etree.fromstring(xml_str,parser=parser)
                    strings = list()
                    for child in xml.iter('string'):
                        if child.text not in strings:
                            text = re.sub(r'\n|\r|\\r|\\n','',child.text)
                            strings.append(text)
                    setattr(afile,'strings',strings)
                except ET.ParseError as e:
                    afile.errors = afile.errors + ['pdf plugin: %s' % str(e)]

