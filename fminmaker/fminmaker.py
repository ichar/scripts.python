# -*- coding: utf-8 -*-

import sys
import os
import codecs
import datetime
import re

from types import UnicodeType, ListType, TupleType, StringType, IntType, LongType, FloatType, BooleanType
from string import strip, upper, lower

version_info = { 'version' : '1.01 beta', 'date' : '2013-09-13', 'now' : datetime.datetime.now().strftime('%Y-%m-%d'), 'time' : datetime.datetime.now().strftime('%H:%M'), 'author' : 'ichar' }
version = 'version %(version)s, %(date)s, %(author)s' % version_info
short_version = 'version %(version)s В© Rosan Finance' % version_info
date_version = '%(now)s %(time)s' % version_info

SequenceTypes = (TupleType, ListType,)
StringTypes = (UnicodeType, StringType,)
NumericTypes = (IntType, FloatType, LongType,)
DigitTypes = (IntType, FloatType, LongType, BooleanType,)

default_encoding = 'cp1251'
default_unicode = 'utf-8'

JAVASCRIPT_TEMPLATE = {
    'Body' : u"""
%(header)s
%(brains)s
%(footer)s
""",
}

EOL = '\n'

IsDisableOutput = 0

_globals = {}

##  =====================================================================================================================  ##

class Logger():
    
    def __init__(self, to_file=None, encoding=default_unicode, mode='w+', bom=True):
        self.is_to_file = to_file and 1 or 0
        self.encoding = encoding
        self.fo = None
        if IsDisableOutput and to_file:
            pass
        elif to_file:
            self.fo = codecs.open(to_file, encoding=self.encoding, mode=mode)
            if bom:
                self.fo.write(codecs.BOM_UTF8.decode(self.encoding))
            print '--> %s' % to_file
        else:
            #self.set_default_encoding()
            pass

    def set_default_encoding(self, encoding=default_unicode):
        if sys.getdefaultencoding() == 'ascii':
            reload(sys)
            sys.setdefaultencoding(encoding)
        print '--> %s' % sys.getdefaultencoding()

    def out(self, line):
        if not line:
            return
        elif not (self.fo or self.is_to_file):
            try:
                print '--> %s' % line
            except:
                if type(line) is UnicodeType:
                    v = ''
                    for x in line:
                        try:
                            print x,
                            v += x.encode(default_encoding, 'ignore')
                        except:
                            v += '?'
                    print '' #'%s==> Unicode ERROR %s' % (EOL, type(line))
                else:
                    print '--> %s' % line.decode(default_encoding, 'ignore')
        elif IsDisableOutput:
            return
        else:
            if type(line) in StringTypes:
                try:
                    self.fo.write(line)
                except:
                    try:
                        self.fo.write(unicode(line, self.encoding))
                    except:
                        #print line.decode(default_encoding)
                        #raise
                        try:
                            self.fo.write(line.decode(default_encoding)) #, 'replace'
                            #print line
                        except:
                            #self.fo.write('xxx')
                            raise
                if not line == EOL:
                    self.fo.write(EOL)

    def close(self):
        if IsDisableOutput:
            return
        if not self.fo:
            return
        self.fo.close()

##  =====================================================================================================================  ##

def make_min(name='functions', encoding=default_unicode):
    script_file = '%s.min.js' % name
    so = Logger(script_file, encoding, bom=True)
    so.out('// %s' % _globals['version']['name'])
    so.out('// %s' % _globals['version']['description'])
    so.out('// %s' % _globals['version']['date'])

    source = file('%s.js' % name, 'rb')
    b = source.read()
    source.close()

    #b = re.sub(r'%s*' % codecs.BOM_UTF8, '', b)

    b = re.sub(r'\/\*(.*?)\*\/(?ims)', '', b)
    b = re.sub(r'^\s*?\/\/(.*?)$(?ims)', '', b)
    b = re.sub(r'\/\/(.*?)\n', '\n', b)
    b = re.sub(r'^\s+$', '', b)

    #b = re.sub(r'(continue|break)\s+(\w)', r'\1;\2', b)
    b = re.sub(r'[\r]+', '', b)
    b = re.sub(r'\t', ' ', b)
    b = re.sub(r'\s+({)\s+', r'\1', b)
    b = re.sub(r'\s+(})\s+', r'\1', b)
    #b = re.sub(r'if\s+(\()', r'if\1', b)
    b = re.sub(r'\s+(=|\?|:|>=|<=|>|<|\+|\-|\:|\*|\|\||&&|==|\!=|\+=)\s+', r'\1', b)
    b = re.sub(r'\;\s+(\(|\)|\{|\}|\[|\]|\w|\$)', r';\1', b)

    # !!! Исключены кавычки {'|"} в соединении с символами слева и справа ...
    # -----------------------------------------------------------------------
    #b = re.sub(r'(\w)\s+(\(|\)|\{|\}|\[|\]|\'|\"|\=|\:|\,|\;)', r'\1\2', b)
    b = re.sub(r'(\w)\s+(\(|\)|\{|\}|\[|\]|\=|\:|\,|\;)', r'\1\2', b)

    #b = re.sub(r'(\(|\)|\{|\}|\[|\]|\'|\"|\=|\:|\,|\;)\s+(\w)', r'\1\2', b)
    b = re.sub(r'(\(|\)|\{|\}|\[|\]|\=|\:|\,|\;)\s+(\w)', r'\1\2', b)
    # -----------------------------------------------------------------------

    #b = re.sub(r'(\w)\s+(\'|\"|\=)', r'\1\2', b)
    b = re.sub(r'\,\s+(\'|\")', r',\1', b)
    b = re.sub(r'[\n]+', '', b)
    b = re.sub(r'\s+', ' ', b)
    #b = re.sub(r'(\;|\})(function)', r'\1 \2', b)

    so.out(b)

    so.close()
    del so

def run(name='functions', encoding=default_unicode):
    """
        Convert 'function.txt' to javascript
    """
    script_file = '%s.js' % name
    so = Logger(script_file, encoding)

    level1 = ' '*4

    def clean(s):
        return re.sub(r'%s{2,}' % EOL, EOL*2, re.sub(r'\s*else\s*\{\s*\}%s*(?si)' % EOL, EOL*2, s)) or s

    def sout(s, no_clean=None):
        # РїРµСЂРµРєРѕРґРёСЂРѕРІРєР° (РІС‹РІРѕРґ РїРѕР»РµР№) РІ default_unicode
        if no_clean:
            return s or ''
        return s and clean(s) or ''

    source = file('%s.txt' % name, 'rb')
    b = source.read()
    source.close()

    b = re.sub(r'\/\*(.*?)\*\/(?ims)', '', b)
    b = re.sub(r'^\s*?\/\/(.*?)$(?ims)', '', b)
    b = re.sub(r'\/\/(.*?)\n', '\n', b)
    b = re.sub(r'^\s+$', '', b)
    b = re.sub(r'(var)\s+([\w]+)(:[\w]+)\s*=\s*', r'\1 \2 = ', b)
    b = re.sub(r'(var)\s+([\w]+)(:[\w]+);', r'\1 \2;', b)
    b = re.sub(r'{\n{2,}', r'{\n', b)
    b = re.sub(r'\n{3,}', r'\n\n', b)

    r = re.compile(r'(function\s+.*)\((.*)\)([\:\w\s\n]*?)\{')
    m = r.search(b)
    while m:
        if m.group(2):
            x = re.sub(r'(\w*)\:(\w*)(,?)', r'\1\3', m.group(2))
            b = b[:m.start()] + m.group(1) + '(' + x + ') {' + b[m.end():]
        m = r.search(b, m.end())

    b = re.sub(r'(for)\s+(each)\s*(\()', r'\1 \3', b)
    b = re.sub(r'(new)\s+(Boolean)\s*\(([\w]+)\)(?ims)', r'\3', b)

    b = b.replace('self.hasOwnProperty(item)', 'item in self')

    if b:
        header = ''
        brains = []
        footer = ''

        for n, line in enumerate(b.split(EOL)[1:]):
            brains.append('%s%s' % ('', line))

        template = JAVASCRIPT_TEMPLATE['Body']
        x = { \
            'header'   : header, 
            'brains'   : EOL.join(brains).decode(default_unicode, 'ignore'), 
            'footer'   : footer
        }
        so.out(sout(template % x))

    so.close()
    del so


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) < 2 or argv[1].lower() in ('/h', '/help', '-h', 'help', '--help'):
        print '--> Rosan Inc.'
        print '--> *JS-Functions Maker* script.'
        print '--> '
        print '--> Arguments:'
        print '-->   <file> - js-filename without extention'
    else:
        name = argv[1]

        _globals['version'] = {
            'name' : '%s.js' % name.capitalize(),
            'description' : 'Generated by Fminmaker.py, %s' % short_version,
            'date' : 'Date: %s' % date_version
        }

        make_min(name)
