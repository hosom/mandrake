import sys, os.path, re
from pdfminer.psparser import PSKeyword, PSLiteral, LIT
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdftypes import PDFObjectNotFound, PDFValueError
from pdfminer.pdftypes import PDFStream, PDFObjRef, resolve1, stream_value
from pdfminer.pdfpage import PDFPage
from pdfminer.utils import isnumber
from pdfid import PDFiD2String, PDFiD



class Plugin:

    __NAME__ = 'pdf'

    def __init__(self, args):
        self.args = args
        self.analyzed_mimes = ['application/pdf']



    SC_PAT = re.compile(r'[\000-\037&<>()"\042\047\134\177-\377]')
    def e(self,s):
        return ESC_PAT.sub(lambda m:'&#%d;' % ord(m.group(0)), s)


    # dumpxml
    def dumpxml(self,out, obj, codec=None):
        if obj is None:
            out.write('<null />')
            return

            if isinstance(obj, dict):
                out.write('<dict size="%d">\n' % len(obj))
                for (k,v) in obj.iteritems():
                    out.write('<key>%s</key>\n' % k)
                    out.write('<value>')
                    self.dumpxml(out, v)
                    out.write('</value>\n')
                out.write('</dict>')
                return

            if isinstance(obj, list):
                out.write('<list size="%d">\n' % len(obj))
                for v in obj:
                    self.dumpxml(out, v)
                    out.write('\n')
                out.write('</list>')
                return

            if isinstance(obj, str):
                out.write('<string size="%d">%s</string>' % (len(obj), self.e(obj)))
                return

            if isinstance(obj, PDFStream):
                if codec == 'raw':
                    out.write(obj.get_rawdata())
                elif codec == 'binary':
                    out.write(obj.get_data())
                else:
                    out.write('<stream>\n<props>\n')
                    self.dumpxml(out, obj.attrs)
                    out.write('\n</props>\n')
                    if codec == 'text':
                        data = obj.get_data()
                        out.write('<data size="%d">%s</data>\n' % (len(data), self.e(data)))
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
    def dumptrailers(self,out, doc):
        for xref in doc.xrefs:
            out.write('<trailer>\n')
            self.dumpxml(out, xref.trailer)
            out.write('\n</trailer>\n\n')
        return

    # dumpallobjs
    def dumpallobjs(self,out, doc, codec=None):
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
                    self.dumpxml(out, obj, codec=codec)
                    out.write('\n</object>\n\n')
                except PDFObjectNotFound as e:
                    print >>sys.stderr, 'not found: %r' % e
        self.dumptrailers(out, doc)
        out.write('</pdf>')
        return


    def pdf_id(self,afile):
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
                # count out PDF tags
                self.pdf_id(afile)

                parser = PDFParser(fp)
                doc = PDFDocument(parser,'')

                self.dumpallobjs(sys.stdout,doc,None)


