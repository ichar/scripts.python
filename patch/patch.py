# -*- coding: cp1251 -*-

#from __future__ import _pout_function

import datetime
import codecs
import sys
import os
import re
import types

from shutil import copytree, copy2

try:
    from types import UnicodeType, StringType
    StringTypes = (UnicodeType, StringType,)
except:
    StringTypes = (str,)

is_v3 = sys.version_info[0] > 2 and True or False

if is_v3:
    from imp import reload

default_no_ext = ('pyc','log','exe',) #'ico','jpg','png','gif',

default_unicode = 'utf-8'
default_encoding = 'cp1251'
default__pout_encoding = 'cp866'

version = '1.01 with cp1251 (Python3)'

config = {}

EOL = '\n'

IsTrace = 0
IsDisableOutput = 0

DEFAULT_DATE_FORMAT = '%Y%m%d'

_globals = {}
_processed = 0

ansi = not sys.platform.startswith("win")

##  =========================================================================================================  ##

def _imports():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            yield val.__name__

def show_imported_modules():
    return [x for x in _imports()]

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

def normpath(p):
    return re.sub(r'\\', '/', os.path.normpath(p))

def mkdir(name):
    try:
        os.mkdir(name)
    except:
        raise OSError('Error while create a folder')

def mdate(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def getToday():
    return datetime.datetime.now()

def getDate(value, format=DEFAULT_DATE_FORMAT):
    return value and datetime.datetime.strptime(value, format) or None

def checkDate(value, format=DEFAULT_DATE_FORMAT):
    try:
        v = getDate(value, format)
        if not (v and v.year > 2010):
            v = None
    except:
        v = None
    return v and True or False

def copy_patch(filename, p, **kw):
    """
        Copy file into the patch.
        Patch is a destination folder, which should be created before.

        >> Copy `filename` into `destination`.
        
        Arguments:
            filename    -- absolute path to the source file
            p           -- source folder path

        Keywords arguments (**kw):
            source      -- root of source folder
            destination -- root of destination folder (patch root)
            root        -- root folder name ('YYYYMMDD')

        Returns:
            Boolean
    """
    source = kw['source']
    destination = kw['destination']

    # ----------------------------------------------
    # Check $ Create the `destination` folders chain 
    # ----------------------------------------------

    folders = re.sub(r'%s(.*)' % source, r'\1', filename).split('/')
    folder = destination

    folders.insert(0, source.split('/')[-1])

    is_not_exists = False

    if IsTrace:
        logger.out('filename %s' % filename)
        logger.out('folders %s' % repr(folders))
        logger.out('destination %s' % destination)

    for name in folders:
        if not name or filename.endswith('/'+name):
            continue

        folder = normpath(os.path.join(folder, name))

        if not is_not_exists and _check_folder(folder):
            continue

        is_not_exists = True

        mkdir(folder)

    # -----------------------------
    # Copy file inside the `folder`
    # -----------------------------

    try:
        copy2(filename, folder)
        return True
    except:
        pass

    return False

def _check_folder(p):
    """
        Check folder existance.
        Returns True if folder exists, otherwise False.

        >> Check a folder `p`.
        
        Arguments:
            p           -- source folder path

        Returns:
            Boolean
    """
    return os.path.exists(p) and os.path.isdir(p)

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

def run(name, p, **kw):
    """
        Run the action.
        Returns True if action finished successfull, otherwise False.

        >> Check $ Copy `name` from `p` into `destination`.

        Arguments:
            name        -- name of the file in the source folder
            p           -- source folder path
    """
    global _processed

    filename = normpath(os.path.join(p, name))
    fdate = mdate(filename)
    
    date_from = kw['date_from']

    date_to = config.get('date_to')
    if date_to:
        date_to = checkDate(date_to) and getDate(date_to) or None
    
    if not (fdate >= date_from and (not date_to or fdate <= date_to) and copy_patch(filename, p, **kw)):
        return

    _pout('--> %s' % filename)

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
    """
        Walk the source folder.
        Checks the filesystem objects, folder should be checked recursively.
        
        Arguments:
            p           -- source folder absolute path

        Local:
            name        -- name of the source object (folder or file)
            source_path -- absolute path to the source object
    """
    if IsTrace:
        logger.out('>>> DIR:%s' % p)
        
    for name in os.listdir(p):
        source_path = normpath(os.path.join(p, name))

        if config.get('suppressed') and name in config['suppressed']:
            continue
        elif _check_folder(source_path):
            walk(source_path, **kw)
        else:
            if _check_file(name, p, **kw):
                run(name, p, **kw)


if __name__ == "__main__":
    #
    # Test: python patch.py patch.config 20170729
    #
    
    argv = sys.argv

    setup_console(default_encoding)

    if IsTrace:
        logger.out('Encoding %s' % sys.getdefaultencoding())

    if len(argv) == 1 or argv[1].lower() in ('/h', '/help', '-h', 'help', '--help', '/?'):
        _pout('--> Rosan Finance Inc.')
        _pout('--> Application project source code patch creater.')
        _pout('--> ')
        _pout('--> Format: patch.py [<config>] YYYYMMDD [<source> [<destination>]]')
        _pout('--> ')
        _pout('--> Parameters:')
        _pout('--> ')
        _pout('-->   <config>      : path to the script config-file, by default: `patch.config`')
        _pout('-->   YYYYMMDD      : patch name as `date_from`')
        _pout('-->   <source>      : source folder, may present in `config`')
        _pout('-->   <destination> : destination folder, may present in `config`')
        _pout('--> ')
        _pout('--> Version:%s' % version)

    elif len(argv) > 1 and argv[1]:

        # -----------
        # Config path
        # -----------
        
        is_default_config = argv[1].isdigit()
        config_path = is_default_config and 'patch.config' or argv[1]
        
        assert config_path, "Config file name is not present!"

        if is_default_config:
            date_from = argv[1] or None
            source = len(argv) > 2 and argv[2] or ''
            destination = len(argv) > 3 and argv[3] or ''
        else:
            date_from = len(argv) > 2 and argv[2] or None
            source = len(argv) > 3 and argv[3] or ''
            destination = len(argv) > 4 and argv[4] or ''

        # -------------------------------------
        # DateFrom as a destination root folder
        # -------------------------------------

        if not date_from:
            date_from = getToday()
            root = date_from.strftime(DEFAULT_DATE_FORMAT)
        else:
            root = date_from
            date_from = checkDate(date_from) and getDate(date_from) or None

        assert date_from, "Date YYYYMMDD is invalid!"

        # --------------
        # Make `_config`
        # --------------

        make_config(config_path)

        # -------------
        # Source folder
        # -------------
        
        if not source:
            source = config.get('source') or './'
        source = normpath(source)

        # ------------------
        # Destination folder
        # ------------------

        if not destination:
            destination = config.get('destination') or './'
    
        assert source != destination, "Destination cannot be equal to source!"

        # -----------------------------------
        # Create a root of destination folder
        # -----------------------------------

        destination = normpath(os.path.join(destination, root))
        if not os.path.exists(destination):
            mkdir(destination)

        # =====
        # Start
        # =====

        if IsTrace:
            logger.out('config: %s, date_from: %s, source: %s, destination: %s, root: %s' % ( \
                config_path,
                str(date_from),
                source,
                destination,
                root,
            ))

        walk(source, source=source, destination=destination, date_from=date_from, root=root, encoding=default_unicode)

        _pout('>>> Total processed: %d' % _processed)

        logger.close()
   