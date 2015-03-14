#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Generated Wed Aug 29 10:36:02 2012 by generateDS.py version 2.7c.
#
## IMPORTANT!!!

# This file was created by generateDS.  It has been modified
# in a few places as denoted by the NOT_GENERATED comments

import getopt
import re as re_
import sys

etree_ = None
Verbose_import_ = False
(XMLParser_import_none, XMLParser_import_lxml,
    XMLParser_import_elementtree
    ) = range(3)
XMLParser_import_library = None
try:
    # lxml
    from lxml import etree as etree_
    XMLParser_import_library = XMLParser_import_lxml
    if Verbose_import_:
        print("running with lxml.etree")
except ImportError:
    try:
        # cElementTree from Python 2.5+
        import xml.etree.cElementTree as etree_
        XMLParser_import_library = XMLParser_import_elementtree
        if Verbose_import_:
            print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # ElementTree from Python 2.5+
            import xml.etree.ElementTree as etree_
            XMLParser_import_library = XMLParser_import_elementtree
            if Verbose_import_:
                print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree_
                XMLParser_import_library = XMLParser_import_elementtree
                if Verbose_import_:
                    print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree_
                    XMLParser_import_library = XMLParser_import_elementtree
                    if Verbose_import_:
                        print("running with ElementTree")
                except ImportError:
                    raise ImportError("Failed to import ElementTree from any known place")

def parsexml_(*args, **kwargs):
    if (XMLParser_import_library == XMLParser_import_lxml and
        'parser' not in kwargs):
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        kwargs['parser'] = etree_.ETCompatXMLParser()
    doc = etree_.parse(*args, **kwargs)
    return doc

#
# User methods
#
# Calls to the methods in these classes are generated by generateDS.py.
# You can replace these methods by re-implementing the following class
#   in a module named generatedssuper.py.

try:
    from generatedssuper import GeneratedsSuper
except ImportError, exp:

    class GeneratedsSuper(object):
        def gds_format_string(self, input_data, input_name=''):
            return input_data
        def gds_validate_string(self, input_data, node, input_name=''):
            return input_data
        def gds_format_integer(self, input_data, input_name=''):
            return '%d' % input_data
        def gds_validate_integer(self, input_data, node, input_name=''):
            return input_data
        def gds_format_integer_list(self, input_data, input_name=''):
            return '%s' % input_data
        def gds_validate_integer_list(self, input_data, node, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    fvalue = float(value)
                except (TypeError, ValueError), exp:
                    raise_parse_error(node, 'Requires sequence of integers')
            return input_data
        def gds_format_float(self, input_data, input_name=''):
            return '%f' % input_data
        def gds_validate_float(self, input_data, node, input_name=''):
            return input_data
        def gds_format_float_list(self, input_data, input_name=''):
            return '%s' % input_data
        def gds_validate_float_list(self, input_data, node, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    fvalue = float(value)
                except (TypeError, ValueError), exp:
                    raise_parse_error(node, 'Requires sequence of floats')
            return input_data
        def gds_format_double(self, input_data, input_name=''):
            return '%e' % input_data
        def gds_validate_double(self, input_data, node, input_name=''):
            return input_data
        def gds_format_double_list(self, input_data, input_name=''):
            return '%s' % input_data
        def gds_validate_double_list(self, input_data, node, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    fvalue = float(value)
                except (TypeError, ValueError), exp:
                    raise_parse_error(node, 'Requires sequence of doubles')
            return input_data
        def gds_format_boolean(self, input_data, input_name=''):
            return '%s' % input_data
        def gds_validate_boolean(self, input_data, node, input_name=''):
            return input_data
        def gds_format_boolean_list(self, input_data, input_name=''):
            return '%s' % input_data
        def gds_validate_boolean_list(self, input_data, node, input_name=''):
            values = input_data.split()
            for value in values:
                if value not in ('true', '1', 'false', '0',):
                    raise_parse_error(node, 'Requires sequence of booleans ("true", "1", "false", "0")')
            return input_data
        def gds_str_lower(self, instring):
            return instring.lower()
        def get_path_(self, node):
            path_list = []
            self.get_path_list_(node, path_list)
            path_list.reverse()
            path = '/'.join(path_list)
            return path
        Tag_strip_pattern_ = re_.compile(r'\{.*\}')
        def get_path_list_(self, node, path_list):
            if node is None:
                return
            tag = GeneratedsSuper.Tag_strip_pattern_.sub('', node.tag)
            if tag:
                path_list.append(tag)
            self.get_path_list_(node.getparent(), path_list)
        def get_class_obj_(self, node, default_class=None):
            class_obj1 = default_class
            if 'xsi' in node.nsmap:
                classname = node.get('{%s}type' % node.nsmap['xsi'])
                if classname is not None:
                    names = classname.split(':')
                    if len(names) == 2:
                        classname = names[1]
                    class_obj2 = globals().get(classname)
                    if class_obj2 is not None:
                        class_obj1 = class_obj2
            return class_obj1
        def gds_build_any(self, node, type_name=None):
            return None


#
# If you have installed IPython you can uncomment and use the following.
# IPython is available from http://ipython.scipy.org/.
#

# # from IPython.Shell import IPShellEmbed
# # args = ''
# # ipshell = IPShellEmbed(args,
# #     banner = 'Dropping into IPython',
# #     exit_msg = 'Leaving Interpreter, back to program.')

# Then use the following line where and when you want to drop into the
# IPython shell:
#    ipshell('<some message> -- Entering ipshell.\nHit Ctrl-D to exit')

#
# Globals
#

# Begin NOT_GENERATED
# External encoding must be utf-8 for Stata and not ascii.
ExternalEncoding = 'utf-8'
# End NOT_GENERATED
Tag_pattern_ = re_.compile(r'({.*})?(.*)')
String_cleanup_pat_ = re_.compile(r"[\n\r\s]+")
Namespace_extract_pat_ = re_.compile(r'{(.*)}(.*)')

#
# Support/utility functions.
#

def showIndent(outfile, level, pretty_print=True):
    if pretty_print:
        for idx in range(level):
            outfile.write('    ')

def quote_xml(inStr):
    if not inStr:
        return ''
    s1 = (isinstance(inStr, basestring) and inStr or
          '%s' % inStr)
    s1 = s1.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('>', '&gt;')
    return s1

def quote_attrib(inStr):
    s1 = (isinstance(inStr, basestring) and inStr or
          '%s' % inStr)
    s1 = s1.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('>', '&gt;')
    if '"' in s1:
        if "'" in s1:
            s1 = '"%s"' % s1.replace('"', "&quot;")
        else:
            s1 = "'%s'" % s1
    else:
        s1 = '"%s"' % s1
    return s1

def quote_python(inStr):
    s1 = inStr
    if s1.find("'") == -1:
        if s1.find('\n') == -1:
            return "'%s'" % s1
        else:
            return "'''%s'''" % s1
    else:
        if s1.find('"') != -1:
            s1 = s1.replace('"', '\\"')
        if s1.find('\n') == -1:
            return '"%s"' % s1
        else:
            return '"""%s"""' % s1

def get_all_text_(node):
    if node.text is not None:
        text = node.text
    else:
        text = ''
    for child in node:
        if child.tail is not None:
            text += child.tail
    return text

def find_attr_value_(attr_name, node):
    attrs = node.attrib
    attr_parts = attr_name.split(':')
    value = None
    if len(attr_parts) == 1:
        value = attrs.get(attr_name)
    elif len(attr_parts) == 2:
        prefix, name = attr_parts
        namespace = node.nsmap.get(prefix)
        if namespace is not None:
            value = attrs.get('{%s}%s' % (namespace, name,))
    return value


class GDSParseError(Exception):
    pass

def raise_parse_error(node, msg):
    if XMLParser_import_library == XMLParser_import_lxml:
        msg = '%s (element %s/line %d)' % (msg, node.tag, node.sourceline,)
    else:
        msg = '%s (element %s)' % (msg, node.tag,)
    raise GDSParseError(msg)


class MixedContainer:
    # Constants for category:
    CategoryNone = 0
    CategoryText = 1
    CategorySimple = 2
    CategoryComplex = 3
    # Constants for content_type:
    TypeNone = 0
    TypeText = 1
    TypeString = 2
    TypeInteger = 3
    TypeFloat = 4
    TypeDecimal = 5
    TypeDouble = 6
    TypeBoolean = 7
    def __init__(self, category, content_type, name, value):
        self.category = category
        self.content_type = content_type
        self.name = name
        self.value = value
    def getCategory(self):
        return self.category
    def getContenttype(self, content_type):
        return self.content_type
    def getValue(self):
        return self.value
    def getName(self):
        return self.name
    def export(self, outfile, level, name, namespace, pretty_print=True):
        if self.category == MixedContainer.CategoryText:
            # Prevent exporting empty content as empty lines.
            if self.value.strip():
                outfile.write(self.value)
        elif self.category == MixedContainer.CategorySimple:
            self.exportSimple(outfile, level, name)
        else:  # category == MixedContainer.CategoryComplex
            self.value.export(outfile, level, namespace, name, pretty_print)
    def exportSimple(self, outfile, level, name):
        if self.content_type == MixedContainer.TypeString:
            outfile.write('<%s>%s</%s>' % (self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeInteger or \
                self.content_type == MixedContainer.TypeBoolean:
            outfile.write('<%s>%d</%s>' % (self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeFloat or \
                self.content_type == MixedContainer.TypeDecimal:
            outfile.write('<%s>%f</%s>' % (self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeDouble:
            outfile.write('<%s>%g</%s>' % (self.name, self.value, self.name))
    def exportLiteral(self, outfile, level, name):
        if self.category == MixedContainer.CategoryText:
            showIndent(outfile, level)
            outfile.write('model_.MixedContainer(%d, %d, "%s", "%s"),\n' % \
                (self.category, self.content_type, self.name, self.value))
        elif self.category == MixedContainer.CategorySimple:
            showIndent(outfile, level)
            outfile.write('model_.MixedContainer(%d, %d, "%s", "%s"),\n' % \
                (self.category, self.content_type, self.name, self.value))
        else:  # category == MixedContainer.CategoryComplex
            showIndent(outfile, level)
            outfile.write('model_.MixedContainer(%d, %d, "%s",\n' % \
                (self.category, self.content_type, self.name,))
            self.value.exportLiteral(outfile, level + 1)
            showIndent(outfile, level)
            outfile.write(')\n')


class MemberSpec_(object):
    def __init__(self, name='', data_type='', container=0):
        self.name = name
        self.data_type = data_type
        self.container = container
    def set_name(self, name): self.name = name
    def get_name(self): return self.name
    def set_data_type(self, data_type): self.data_type = data_type
    def get_data_type_chain(self): return self.data_type
    def get_data_type(self):
        if isinstance(self.data_type, list):
            if len(self.data_type) > 0:
                return self.data_type[-1]
            else:
                return 'xs:string'
        else:
            return self.data_type
    def set_container(self, container): self.container = container
    def get_container(self): return self.container

def _cast(typ, value):
    if typ is None or value is None:
        return value
    return typ(value)

#
# Data representation classes.
#

class report(GeneratedsSuper):
    subclass = None
    superclass = None
    def __init__(self, binding=None):
        if binding is None:
            self.binding = []
        else:
            self.binding = binding
    def factory(*args_, **kwargs_):
        if report.subclass:
            return report.subclass(*args_, **kwargs_)
        else:
            return report(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_binding(self): return self.binding
    def set_binding(self, binding): self.binding = binding
    def add_binding(self, value): self.binding.append(value)
    def insert_binding(self, index, value): self.binding[index] = value
    def export(self, outfile, level, namespace_='tns:', name_='report', namespacedef_='', pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',))
        already_processed = []
        self.exportAttributes(outfile, level, already_processed, namespace_, name_='report')
        if self.hasContent_():
            outfile.write('>%s' % (eol_,))
            self.exportChildren(outfile, level + 1, namespace_, name_, pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespace_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_,))
    def exportAttributes(self, outfile, level, already_processed, namespace_='tns:', name_='report'):
        pass
    def exportChildren(self, outfile, level, namespace_='tns:', name_='report', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for binding_ in self.binding:
            binding_.export(outfile, level, namespace_, name_='binding', pretty_print=pretty_print)
    def hasContent_(self):
        if (
            self.binding
            ):
            return True
        else:
            return False
    def exportLiteral(self, outfile, level, name_='report'):
        level += 1
        self.exportLiteralAttributes(outfile, level, [], name_)
        if self.hasContent_():
            self.exportLiteralChildren(outfile, level, name_)
    def exportLiteralAttributes(self, outfile, level, already_processed, name_):
        pass
    def exportLiteralChildren(self, outfile, level, name_):
        showIndent(outfile, level)
        outfile.write('binding=[\n')
        level += 1
        for binding_ in self.binding:
            showIndent(outfile, level)
            outfile.write('model_.binding(\n')
            binding_.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
    def build(self, node):
        self.buildAttributes(node, node.attrib, [])
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)
    def buildAttributes(self, node, attrs, already_processed):
        pass
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        if nodeName_ == 'binding':
            obj_ = binding.factory()
            obj_.build(child_)
            self.binding.append(obj_)
# end class report


class binding(GeneratedsSuper):
    subclass = None
    superclass = None
    def __init__(self, href=None, type_=None, name=None, value=None, fileName=None, valueOf_=None):
        self.href = _cast(None, href)
        self.type_ = _cast(None, type_)
        self.name = _cast(None, name)
        self.value = _cast(None, value)
        self.fileName = _cast(None, fileName)
        self.valueOf_ = valueOf_
    def factory(*args_, **kwargs_):
        if binding.subclass:
            return binding.subclass(*args_, **kwargs_)
        else:
            return binding(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_href(self): return self.href
    def set_href(self, href): self.href = href
    def get_type(self): return self.type_
    def set_type(self, type_): self.type_ = type_
    def get_name(self): return self.name
    def set_name(self, name): self.name = name
    def get_value(self): return self.value
    def set_value(self, value): self.value = value
    def get_fileName(self): return self.fileName
    def set_fileName(self, fileName): self.fileName = fileName
    def get_valueOf_(self): return self.valueOf_
    def set_valueOf_(self, valueOf_): self.valueOf_ = valueOf_
    def export(self, outfile, level, namespace_='tns:', name_='binding', namespacedef_='', pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',))
        already_processed = []
        self.exportAttributes(outfile, level, already_processed, namespace_, name_='binding')
        if self.hasContent_():
            outfile.write('>')
            outfile.write(str(self.valueOf_.encode(ExternalEncoding)))
            self.exportChildren(outfile, level + 1, namespace_, name_, pretty_print=pretty_print)
            outfile.write('</%s%s>%s' % (namespace_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_,))
    def exportAttributes(self, outfile, level, already_processed, namespace_='tns:', name_='binding'):
        if self.href is not None and 'href' not in already_processed:
            already_processed.append('href')
            outfile.write(' href=%s' % (self.gds_format_string(quote_attrib(self.href).encode(ExternalEncoding), input_name='href'),))
        if self.type_ is not None and 'type_' not in already_processed:
            already_processed.append('type_')
            outfile.write(' type=%s' % (self.gds_format_string(quote_attrib(self.type_).encode(ExternalEncoding), input_name='type'),))
        if self.name is not None and 'name' not in already_processed:
            already_processed.append('name')
            outfile.write(' name=%s' % (self.gds_format_string(quote_attrib(self.name).encode(ExternalEncoding), input_name='name'),))
        if self.value is not None and 'value' not in already_processed:
            already_processed.append('value')
            outfile.write(' value=%s' % (self.gds_format_string(quote_attrib(self.value).encode(ExternalEncoding), input_name='value'),))
        if self.fileName is not None and 'fileName' not in already_processed:
            already_processed.append('fileName')
            outfile.write(' fileName=%s' % (self.gds_format_string(quote_attrib(self.fileName).encode(ExternalEncoding), input_name='fileName'),))
    def exportChildren(self, outfile, level, namespace_='tns:', name_='binding', fromsubclass_=False, pretty_print=True):
        pass
    def hasContent_(self):
        if (
            self.valueOf_
            ):
            return True
        else:
            return False
    def exportLiteral(self, outfile, level, name_='binding'):
        level += 1
        self.exportLiteralAttributes(outfile, level, [], name_)
        if self.hasContent_():
            self.exportLiteralChildren(outfile, level, name_)
        showIndent(outfile, level)
        outfile.write('valueOf_ = """%s""",\n' % (self.valueOf_,))
    def exportLiteralAttributes(self, outfile, level, already_processed, name_):
        if self.href is not None and 'href' not in already_processed:
            already_processed.append('href')
            showIndent(outfile, level)
            outfile.write('href = "%s",\n' % (self.href,))
        if self.type_ is not None and 'type_' not in already_processed:
            already_processed.append('type_')
            showIndent(outfile, level)
            outfile.write('type_ = "%s",\n' % (self.type_,))
        if self.name is not None and 'name' not in already_processed:
            already_processed.append('name')
            showIndent(outfile, level)
            outfile.write('name = "%s",\n' % (self.name,))
        if self.value is not None and 'value' not in already_processed:
            already_processed.append('value')
            showIndent(outfile, level)
            outfile.write('value = "%s",\n' % (self.value,))
        if self.fileName is not None and 'fileName' not in already_processed:
            already_processed.append('fileName')
            showIndent(outfile, level)
            outfile.write('fileName = "%s",\n' % (self.fileName,))
    def exportLiteralChildren(self, outfile, level, name_):
        pass
    def build(self, node):
        self.buildAttributes(node, node.attrib, [])
        self.valueOf_ = get_all_text_(node)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)
    def buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('href', node)
        if value is not None and 'href' not in already_processed:
            already_processed.append('href')
            self.href = value
        value = find_attr_value_('type', node)
        if value is not None and 'type' not in already_processed:
            already_processed.append('type')
            self.type_ = value
        value = find_attr_value_('name', node)
        if value is not None and 'name' not in already_processed:
            already_processed.append('name')
            self.name = value
        value = find_attr_value_('value', node)
        if value is not None and 'value' not in already_processed:
            already_processed.append('value')
            self.value = value
        value = find_attr_value_('fileName', node)
        if value is not None and 'fileName' not in already_processed:
            already_processed.append('fileName')
            self.fileName = value
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        pass
# end class binding


USAGE_TEXT = """
Usage: python <Parser>.py [ -s ] <in_xml_file>
"""

def usage():
    print USAGE_TEXT
    sys.exit(1)


def get_root_tag(node):
    tag = Tag_pattern_.match(node.tag).groups()[-1]
    # rootClass = globals().get(tag)
    rootClass = findRootClass(tag)
    # End NOT_GENERATED
    return tag, rootClass


def parse(inFileName, verbose=True):
    doc = parsexml_(inFileName)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'report'
        rootClass = report
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
     # Begin NOT_GENERATED
    if verbose:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(sys.stdout, 0, name_=rootTag,
            namespacedef_='')
     # End NOT_GENERATED
    return rootObj


def parseString(inString):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'report'
        rootClass = report
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    # Begin NOT_GENERATED
    # Let's shut up the echoing of the received XML
    # to stdout.
#    sys.stdout.write('<?xml version="1.0" ?>\n')
#    rootObj.export(sys.stdout, 0, name_="link",
#        namespacedef_='')
    # End NOT_GENERATED
    return rootObj


def parseLiteral(inFileName):
    doc = parsexml_(inFileName)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'report'
        rootClass = report
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('#from report import *\n\n')
    sys.stdout.write('import report as model_\n\n')
    sys.stdout.write('rootObj = model_.rootTag(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
    sys.stdout.write(')\n')
    return rootObj


def main():
    args = sys.argv[1:]
    if len(args) == 1:
        parse(args[0])
    else:
        usage()


if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    main()


__all__ = [
    "binding",
    "report"
    ]

# Begin NOT_GENERATED
_rootClassMap = {
                "binding"  : binding,
                "report"   : report
    }
def findRootClass(rootTag):
    """
    Helper function that enables the generated code to locate the
    root element.  The api does not explicitly list a root
    element; hence, the generated code has a hard time deducing
    which one it actually is.  This function will map the first
    tag in the XML (i.e. the root) to an internal class.
    """
    res = _rootClassMap.get(rootTag)
    return res
# End NOT_GENERATED