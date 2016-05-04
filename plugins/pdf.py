<<<<<<< HEAD
import sys, os.path, re
from pdfminer.psparser import PSKeyword, PSLiteral, LIT
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdftypes import PDFObjectNotFound, PDFValueError
from pdfminer.pdftypes import PDFStream, PDFObjRef, resolve1, stream_value
from pdfminer.pdfpage import PDFPage
from pdfminer.utils import isnumber
from pdfid import PDFiD2String, PDFiD

#Sourced from the dumppdf.py utilitiy that is installed with pdfminer. 
#Modified to be usable as an object
class DumpPDF:

    SC_PAT = re.compile(r'[\000-\037&<>()"\042\047\134\177-\377]')
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
            return

    # dumpoutline
    def dumpoutline(outfp, fname, objids, pagenos, password='',
                                    dumpall=False, codec=None, extractdir=None):
            fp = file(fname, 'rb')
            parser = PDFParser(fp)
            doc = PDFDocument(parser, password)
            pages = dict( (page.pageid, pageno) for (pageno,page)
                                        in enumerate(PDFPage.create_pages(doc)) )
            def resolve_dest(dest):
                    if isinstance(dest, str):
                            dest = resolve1(doc.get_dest(dest))
                    elif isinstance(dest, PSLiteral):
                            dest = resolve1(doc.get_dest(dest.name))
                    if isinstance(dest, dict):
                            dest = dest['D']
                    return dest
            try:
                    outlines = doc.get_outlines()
                    outfp.write('<outlines>\n')
                    for (level,title,dest,a,se) in outlines:
                            pageno = None
                            if dest:
                                    dest = resolve_dest(dest)
                                    pageno = pages[dest[0].objid]
                            elif a:
                                    action = a.resolve()
                                    if isinstance(action, dict):
                                            subtype = action.get('S')
                                            if subtype and repr(subtype) == '/GoTo' and action.get('D'):
                                                    dest = resolve_dest(action['D'])
                                                    pageno = pages[dest[0].objid]
                            s = e(title).encode('utf-8', 'xmlcharrefreplace')
                            outfp.write('<outline level="%r" title="%s">\n' % (level, s))
                            if dest is not None:
                                    outfp.write('<dest>')
                                    dumpxml(outfp, dest)
                                    outfp.write('</dest>\n')
                            if pageno is not None:
                                    outfp.write('<pageno>%r</pageno>\n' % pageno)
                            outfp.write('</outline>\n')
                    outfp.write('</outlines>\n')
            except PDFNoOutlines:
                    pass
            parser.close()
            fp.close()
            return

    # extractembedded
    LITERAL_FILESPEC = LIT('Filespec')
    LITERAL_EMBEDDEDFILE = LIT('EmbeddedFile')
    def extractembedded(outfp, fname, objids, pagenos, password='',
                                            dumpall=False, codec=None, extractdir=None):
            def extract1(obj):
                    filename = os.path.basename(obj['UF'] or obj['F'])
                    fileref = obj['EF']['F']
                    fileobj = doc.getobj(fileref.objid)
                    if not isinstance(fileobj, PDFStream):
                            raise PDFValueError(
                                    'unable to process PDF: reference for %r is not a PDFStream' %
                                    (filename))
                    if fileobj.get('Type') is not LITERAL_EMBEDDEDFILE:
                            raise PDFValueError(
                                    'unable to process PDF: reference for %r is not an EmbeddedFile' %
                                    (filename))
                    path = os.path.join(extractdir, filename)
                    if os.path.exists(path):
                            raise IOError('file exists: %r' % path)
                    print >>sys.stderr, 'extracting: %r' % path
                    out = file(path, 'wb')
                    out.write(fileobj.get_data())
                    out.close()
                    return

            fp = file(fname, 'rb')
            parser = PDFParser(fp)
            doc = PDFDocument(parser, password)
            for xref in doc.xrefs:
                    for objid in xref.get_objids():
                            obj = doc.getobj(objid)
                            if isinstance(obj, dict) and obj.get('Type') is LITERAL_FILESPEC:
                                    extract1(obj)
            return

    # dumppdf
    def dumppdf(outfp, fname, objids, pagenos, password='',
                            dumpall=True, codec=None, extractdir=None):
            fp = file(fname, 'rb')
            parser = PDFParser(fp)
            doc = PDFDocument(parser, password)
            if objids:
                    for objid in objids:
                            obj = doc.getobj(objid)
                            dumpxml(outfp, obj, codec=codec)
            if pagenos:
                    for (pageno,page) in enumerate(PDFPage.create_pages(doc)):
                            if pageno in pagenos:
                                    if codec:
                                            for obj in page.contents:
                                                    obj = stream_value(obj)
                                                    dumpxml(outfp, obj, codec=codec)
                                    else:
                                            dumpxml(outfp, page.attrs)
            if dumpall:
                    dumpallobjs(outfp, doc, codec=codec)
            if (not objids) and (not pagenos) and (not dumpall):
                    dumptrailers(outfp, doc)
            fp.close()
            if codec not in ('raw','binary'):
                    outfp.write('\n')
            return




class Plugin:

    __NAME__ = 'pdf'

    def __init__(self, args):
        self.args = args
        self.analyzed_mimes = ['application/pdf']


    def pdf_id(afile_path):
        result = PDFiD2String(PDFiD(afile_path),True)
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
                pdf_id(afile.path)

                pdf_xml = DumpPDF()
                pdf_xml.dumppdf()


