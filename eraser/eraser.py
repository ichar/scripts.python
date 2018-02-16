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

no_ext = ('mo','swf','pyc','ico','jpg','png','gif',)

default_encoding = 'cp1251'
default_unicode = 'utf-8'

version = '1.0 with cp1251 (Python3)'

config = {}

EOL = '\n'

IsDebug = 0
IsTrace = 1
IsDisableOutput = 0

_globals = {}

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

def rmdir(name):
    if os.name=='posix':
        command = 'rm -rf "'+name+'"'
    else:
        command = 'rmdir /s/q "'+name+'"'
    if os.system(command):
        raise 'Error while remove a file'

def is_mask_matched(mask, value):
    return mask and value and re.match(mask, value)

def check(p, name, **kw):
    filename = os.path.join(p, name)

    if IsDebug:
        _pout('--> %s' % filename)
        return

    rmdir(filename)

    if IsTrace:
        logger.out('removed:%s' % filename)

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

            if key == 'suppressed':
                config[key] = value.split(':')
                continue

            if key not in 'file:folder':
                continue

            if key not in config:
                config[key] = []

            config[key].append(value)

    if IsTrace:
        for key in config.keys():
            logger.out('config: %s -> %s' % (key, config[key]))

def walk(p, **kw):
    for name in os.listdir(p):
        path = os.path.join(p, name)

        if config.get('suppressed') and name in config['suppressed']:
            continue
        elif os.path.isdir(path) and not os.path.islink(path):
            if 'folder' in config and name in config['folder']:
                check(p, name, **kw)
            else:
                walk(path, **kw)
        elif 'file' in config:
            for mask in config['file']:
                if is_mask_matched(mask, name):
                    check(p, name, **kw)
                    continue


if __name__ == "__main__":
    argv = sys.argv

    setup_console(default_encoding)

    if IsTrace:
        logger.out('Encoding %s' % sys.getdefaultencoding())

    if len(argv) == 1 or argv[1].lower() in ('/h', '/help', '-h', 'help', '--help', '/?'):
        _pout('--> Rosan Finance Inc.')
        _pout('--> Eraser of file system objects script.')
        _pout('--> ')
        _pout('--> Format: eraser.py <config> <source>')
        _pout('--> ')
        _pout('--> %s' % version)

    elif len(argv) > 1 and argv[1]:
        config_path = argv[1]
        assert config_path, "Config file name is not present!"

        make_config(config_path)

        source = len(argv) > 2 and argv[2] or ''
        if not source:
            source = './'

        walk(source)

        logger.close()
