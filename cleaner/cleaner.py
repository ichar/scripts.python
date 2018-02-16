# -*- coding: cp1251 -*-

#from __future__ import _pout_function

import codecs
import sys
import os
import re

try:
    from types import UnicodeType, StringType
    StringTypes = (UnicodeType, StringType,)
except:
    StringTypes = (str,)

is_v3 = sys.version_info[0] > 2 and True or False

if is_v3:
    from imp import reload

default_no_ext = ('mo','swf','pyc','ico','jpg','png','gif',)

default_unicode = 'utf-8'
default_encoding = 'cp1251'
default__pout_encoding = 'cp866'

version = '1.0 with cp1251 (Python3)'

config = {}

EOL = '\n'

IsTrace = 1
IsCheckOnly = 0
IsDisableOutput = 0

_globals = {}
_processed = 0

ansi = not sys.platform.startswith("win")

##  =========================================================================================================  ##

def _pout(s, **kw):
    if not is_v3:
        print(s, end='end' in kw and kw.get('end') or None)
        if 'flush' in kw and kw['flush'] == True:
            sys.stdout.flush()
    else:
        print(s, **kw)

class Logger():
    
    def __init__(self, to_file=None, encoding=default_unicode, mode='w+', bom=True, end_of_line=EOL):
        self.is_to_file = to_file and 1 or 0
        self.encoding = encoding
        self.fo = None
        self.end_of_line = end_of_line

        if IsDisableOutput and to_file:
            pass
        elif to_file:
            self.fo = codecs.open(to_file, encoding=self.encoding, mode=mode)
            if bom:
                self.fo.write(codecs.BOM_UTF8.decode(self.encoding))
            self.out(to_file, console_forced=True) #_pout('--> %s' % to_file)
        else:
            pass

    def get_to_file(self):
        return self.fo

    def set_default_encoding(self, encoding=default_unicode):
        if sys.getdefaultencoding() == 'ascii':
            reload(sys)
            sys.setdefaultencoding(encoding)
        _pout('--> %s' % sys.getdefaultencoding())

    def out(self, line, console_forced=False, without_decoration=False):
        if not line:
            return
        elif console_forced or not (self.fo or self.is_to_file):
            mask = '%s' % (not without_decoration and '--> ' or '')
            try:
                _pout('%s%s' % (mask, line))
            except:
                if is_v3:
                    pass
                elif type(line) is UnicodeType:
                    v = ''
                    for x in line:
                        try:
                            _pout(x, end='')
                            v += x.encode(default_encoding, 'ignore')
                        except:
                            v += '?'
                    _pout('')
                else:
                    _pout('%s%s' % (mask, line.decode(default_encoding, 'ignore')))
        elif IsDisableOutput:
            return
        else:
            if type(line) in StringTypes:
                try:
                    self.fo.write(line)
                except:
                    if is_v3:
                        return
                    try:
                        self.fo.write(unicode(line, self.encoding))
                    except:
                        try:
                            self.fo.write(line.decode(default_encoding)) #, 'replace'
                        except:
                            raise
                if not line == self.end_of_line:
                    self.fo.write(self.end_of_line)

    def progress(self, line=None, mode='continue'):
        if mode == 'start':
            _pout('--> %s:' % (line or ''), end=' ')
        elif mode == 'end':
            _pout('', end='\n')
        else:
            _pout('#', end='', flush=True)

    def close(self):
        if IsDisableOutput:
            return
        if not self.fo:
            return
        self.fo.close()

def setup_console(sys_enc=default_unicode):
    """
    Set sys.defaultencoding to `sys_enc` and update stdout/stderr writers to corresponding encoding
    .. note:: For Win32 the OEM console encoding will be used istead of `sys_enc`
    http://habrahabr.ru/post/117236/
    http://www.py-my.ru/post/4bfb3c6a1d41c846bc00009b
    """
    global ansi
    reload(sys)
    
    try:
        if sys.platform.startswith("win"):
            import ctypes
            enc = "cp%d" % ctypes.windll.kernel32.GetOEMCP()
        else:
            enc = (sys.stdout.encoding if sys.stdout.isatty() else
                        sys.stderr.encoding if sys.stderr.isatty() else
                            sys.getfilesystemencoding() or sys_enc)

        sys.setdefaultencoding(sys_enc)

        if sys.stdout.isatty() and sys.stdout.encoding != enc:
            sys.stdout = codecs.getwriter(enc)(sys.stdout, 'replace')

        if sys.stderr.isatty() and sys.stderr.encoding != enc:
            sys.stderr = codecs.getwriter(enc)(sys.stderr, 'replace')
    except:
        pass

##  =========================================================================================================  ##

logger = Logger(False, encoding=default_encoding)

def mkdir(name):
    command = 'mkdir "'+name+'"'
    if os.system(command):
        raise 'Error while create a folder'

def clean(name, destination, encoding):
    source = open(name, 'r', encoding=encoding)
    b = source.read()
    source.close()

    for key in config.keys():
        if key in ('suppressed', 'no_ext',):
            continue

        value = config[key]
        b = re.sub(r'%s(?si)' % key, value or '', b)

    p = os.path.join(destination, name)
    
    #_pout('>>> %s' % p)

    so = Logger(p, encoding=encoding, bom=False)

    so.out(b)
    so.close()

    del so

def _check_file(name, p, **kw):
    """
        Check file existance.
        Returns True if file is valid, otherwise False.

        >> Check a file `name` inside `p`.
        
        Arguments:
            name        -- name of a file in the folder (source)

        Returns:
            Boolean
    """
    no_ext = config.get('no_ext') or default_no_ext
    return name.split('.')[-1] not in no_ext

def _is_suppressed(name):
    for mask in config['suppressed']:
        if re.search(r'%s' % mask, name, re.I+re.DOTALL):
            return True
    return False

def check_key_exists(b, key):
    return key and key in b

def run(p, name, **kw):
    global _processed

    encoding = kw.get('encoding', default_unicode)
    file_name = os.path.join(p, name)
    IsFound = False

    #_pout('--> %s' % file_name)

    try:
        source = open(file_name, 'r', encoding=encoding)
        b = source.read()
        source.close()
    except:
        b = None

    for key in config.keys():
        value = config[key]
        
        #_pout('%s' % len(b))
        
        IsFound = b and check_key_exists(b, key) and True or False
        if IsFound:
            break

    destination = kw.get('destination', '') #os.path.join(, p.startswith('.') and p[2:] or p)

    if IsFound:
        #if IsTrace:
        #    _pout '> clean: %s to %s' % (file_name, destination)

        if not IsCheckOnly:
            clean(file_name, destination, encoding)

        elif IsTrace:
            _pout('>>> %s' % os.path.join(destination, name))

        _processed += 1

def make_config(source, encoding=default_encoding):
    with open(source, 'r', encoding=encoding) as fin:
        for line in fin:
            s = line
            if line.startswith(';') or line.startswith('#'):
                continue
            x = line.split('::')
            if len(x) < 2:
                continue

            key = x[0].strip()
            value = x[1].strip()

            if key in ('suppressed', 'no_ext'):
                value = value.split(':')

            config[key] = value

            logger.out('config: %s -> %s' % (key, value))

def walk(p, **kw):
    for name in os.listdir(p):
        path = os.path.join(p, name)

        if config.get('suppressed') and _is_suppressed(name):
            continue
        elif os.path.isdir(path):
            walk(path, **kw)
        else:
            if _check_file(name, p, **kw):
                run(p, name, **kw)


if __name__ == "__main__":
    argv = sys.argv

    setup_console(default_encoding)

    logger.out('Encoding %s' % sys.getdefaultencoding())

    if len(argv) < 3 or argv[1].lower() in ('/h', '/help', '-h', 'help', '--help', '/?'):
        _pout('--> Rosan Finance Inc.')
        _pout('--> Clean or modify files with the given context.')
        _pout('--> ')
        _pout('--> Format: cleaner.py [options] <config> <source> [<destination>]')
        _pout('--> ')
        _pout('--> Options:')
        _pout('--> ')
        _pout('-->   --check: check key presence only')
        _pout('--> ')
        _pout('--> Implemented for Python3')
        _pout('--> %s' % version)

    elif len(argv) > 2:
        has_options = False
        for x in argv[1:2]:
            if x.startswith('--'):
                has_options = True
                if x[2:] == '':
                    pass
                elif x[2:] == 'check':
                    IsCheckOnly = 1
                    logger.out('config: IsCheckOnly=%s' % IsCheckOnly)
                else:
                    pass
                continue

        n = has_options and 2 or 1

        config_path = argv[n]
        assert config_path, "Config file name is not present!"

        source = argv[n+1]
        if not source:
            source = './'

        destination = len(argv) > n+2 and argv[n+2] or ''
        if not destination:
            destination = './'

        assert source != destination, "Destination cannot be equal to source!"

        make_config(config_path)

        walk(source, destination=destination, encoding=default_unicode)

        _pout('>>> Total processed: %d' % _processed)

        logger.close()
