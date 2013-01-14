from distutils.core import setup
import glob
import py2exe
import os,sys
import shutil

def myignore(src,name):
    return (['.svn',])

sys.argv.append('py2exe')

setup(windows=[{'script':'litebook.py',"icon_resources": [(1, "litebook.ico")]}],
data_files=[('templates', glob.glob('templates/*.*')),
            ('UnRAR2', glob.glob('UnRAR2/*.*')),
            ('icon', glob.glob('icon/*.*')),
            ('background', glob.glob('background/*.*')),
            ('plugin', glob.glob('plugin/*.py')),
            "litebook.exe.manifest",
            "litebook.ico","unrar.dll","bh.dat","py.dat","defaultconfig.ini",
            "Readme.txt",
            "LTBNET_Readme.txt"
            ],
options = {'py2exe': {'bundle_files': 3,'compressed':False,'optimize':2,
            'includes': ['lxml.etree',
                         'lxml._elementpath',
                         'lxml.html',
                         'gzip',
                         'download_manager',
                         'ctypes.*',

                         ],
            'excludes': [
                        "pywin", "pywin.debugger", "pywin.debugger.dbgcon",
                        "pywin.dialogs", "pywin.dialogs.list",
                        "Tkconstants","Tkinter","tcl",
                        "jieba",

                        ],
            },
},
zipfile = "lib/library.zip",



)

shutil.copytree('helpdoc','.\\dist\\helpdoc',ignore=myignore)