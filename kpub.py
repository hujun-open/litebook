#!/usr/bin/python
# -*- coding: utf-8 -*-


#-------------------------------------------------------------------------------
# Name:        KPUB
# Purpose:     publish all books in the specified dir via KADP
#
# Author:      Hu Jun
#
# Created:     17/08/2012
# Copyright:   (c) Hu Jun 2012
# Licence:     GPLv3
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import sys
import re
import xmlrpclib
import zipfile

import hashlib
import traceback
import time
import struct
import cPickle
import threading
import platform
import logging
import longbin
import base64
myos=platform.architecture()
ros = platform.system()
if myos[1]=='ELF' and ros == 'Linux':
    if myos[0]=='64bit':
        from lxml_linux_64 import etree
    elif myos[0]=='32bit':
        from lxml_linux import etree
elif ros == 'Darwin':
    from lxml_osx import etree
else:
    from lxml import etree


def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")


def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))

    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

if we_are_frozen():
    print "I am here", module_path()
    sys.path.append(module_path())
import jieba


##if ros == 'Windows':
##    from pymmseg_win import mmseg
##elif ros == 'Darwin':
##    from pymmseg_osx import mmseg
##elif myos[1]=='ELF' and ros == 'Linux' and myos[0]=='64bit':
##    from pymmseg_linux_64 import mmseg
##else:
##    from pymmseg import mmseg


import urllib

def cur_file_dir():
    #获取脚本路径
    global ros
    if ros == 'Linux':
        path = sys.path[0]
    elif ros == 'Windows':
        x=os.path.dirname(os.path.abspath(sys.argv[0])).decode(sys.getfilesystemencoding())
        print x
        print type(x)
        return x
    else:
        if sys.argv[0].find('/') != -1:
            path = sys.argv[0]
        else:
            path = sys.path[0]
    if isinstance(path,str):
        path=path.decode('utf-8')

    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def getEPUBMeta(ifile):
    """
    return a dict of epub meta data
    ifile is the path to the epub file
    """
    try:
        zfile = zipfile.ZipFile(ifile,'r')
    except:
        return False
    container_xml = zfile.open('META-INF/container.xml')
    context = etree.iterparse(container_xml)
    opfpath='OPS/content.opf'
    for action, elem in context:
        if elem.tag[-8:].lower()=='rootfile':
            try:
                opfpath=elem.attrib['full-path']
            except:
                break
            break
    opf_file = zfile.open(opfpath)
    context = etree.iterparse(opf_file)
    meta_list={}
    for action, elem in context:
        if elem.tag.split('}')[0][1:].lower()=='http://purl.org/dc/elements/1.1/':
            meta_list[elem.tag.split('}')[-1:][0]]=elem.text
    return meta_list

class KPUB(threading.Thread):
    def __init__(self,ipath,rloc_base_url=u'http://SELF:8000/',kcurl='http://127.0.0.1:50201/'):
        """
        ipath is a unicode, represent the share_root
        rloc_base_url is the base URL of resouce location, should be unicode
        kcurl is the XMLRPC URL of the KADP
        """
        threading.Thread.__init__(self)
        # create logger
        self.lifetime=60*60*24*3 #3 day lifetime
        self.SALT = 'DKUYUPUB'
        self.running = True

        self.logger = logging.getLogger("KPUB")
        self.logger.setLevel(logging.DEBUG)

        # create console log handler

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = \
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s'
                              )
        ch.setFormatter(formatter)

        # add console handler to logger, multiple handler could be added to same logger

        self.logger.addHandler(ch)
        self.logger.disabled = True

##        self.states={}#this is a dict used to save pub states

        if os.path.isdir(ipath) != True:
            raise ValueError('Invalid Path:'+ipath)
        else:
            self.root=os.path.abspath(ipath)
        self.rloc_base=unicode(rloc_base_url).encode('utf-8')
        self.kserver=xmlrpclib.Server(kcurl)




        #load saved states



##        rid,
##        data,
##        rtype=1,
##        rloc=None,
##        metadata={},
##        owner_id='SELF',
##        ctime=None


##    def saveStates(self):
##        fname = self.root+os.sep+'.kpub.states'
##        savef = open(fname, 'wb')
##        saves = cPickle.dumps(self.states, 2)
##        saves = struct.pack('f',time.time()) + saves
##        m = hashlib.sha224()
##        m.update(saves+self.SALT)
##        savef.write(m.digest()+saves) #use sha224 to hash
##        savef.close()


##    def loadStates(self):
##        fname = self.root+os.sep+'.kpub.states'
##        if not os.path.exists(fname):
##            self.logger.warning('saved states not found')
##            return False
##        try:
##            savef = open(fname, 'rb')
##            loads = savef.read()
##            m = hashlib.sha224()
##            m.update(loads[28:]+self.SALT)
##            if m.digest() != loads[:28]:
##                return False
##            if time.time() - (struct.unpack('f',loads[28:32])[0]) > self.lifetime:
##                return False
##            self.states = cPickle.loads(loads[32:])
##            savef.close()
##        except Exception, inst:
##            self.logger.error("loadStates failed\n")
##            self.logger.error(str(inst))
##            return False
##        return True


    def pubBook(self,bookpath):
        """
        Publish a book via KADP
        bpath is the full path to the book
        """
        global ros
        bpath=os.path.abspath(bookpath)
        if os.path.isfile(bpath) == False:
            return False
        meta_list={}
        if os.path.splitext(bpath)[1].lower()=='.epub':
            meta_list=getEPUBMeta(bpath)
        else:
            meta_list['size']=os.stat(bpath).st_size
        for k,v in meta_list.items():
            if v == None:
                meta_list[k]=''
        inf=open(bpath,'rb')
        m = hashlib.sha1()
        m.update(inf.read())
        rid=m.digest()
        #rid = longbin.LongBin(rid)

        inf.close()
        data=os.path.basename(bpath)
        #data=KADP.AnyToUnicode(data)
        if isinstance(data,str):
            data=data.decode(sys.getfilesystemencoding())
##            if ros != 'Windows':
##                data=data.decode('utf-8')
##            else:
##                data=data.decode('utf-16')
        try:
            rlpath=os.path.relpath(bpath,self.root)
        except Exception, inst:
            self.logger.error('pubBook:'+traceback.format_exc())
            self.logger.error('pubBook: catched exception: '
                         + str(inst))
            return False

        if rlpath[:2]=='..':
            return False
        if isinstance(rlpath,unicode):
            rlpath=rlpath.encode('utf-8')
        rlpath=urllib.quote(rlpath)
        #check if the resource has been published within last lifetime
##        if rid in self.states:
##            if self.states[rid]['relpath']==rlpath:
##                if time.time()-self.states[rid]['lastpub']<=self.lifetime:
##                    return False
##            else:
##                if os.path.exists(self.states[rid]['bookpath']):
##                    return False
        rloc=self.rloc_base+rlpath
        rtype=1
        #kres = KADP.KADRes(rid,data,rtype,rloc,meta_list)
        fname=os.path.splitext(data)[0]
        if os.path.splitext(bpath)[1].lower()=='.epub':
            if 'title' in meta_list:
                fname=meta_list['title']
        if not isinstance(fname,unicode):
            fname=fname.decode('utf-8')
        fname=fname.encode('utf-8')
        kw_list = list(jieba.cut(fname,cut_all=False))
        klist = []
        p = re.compile('^\d+$')
        for kw in kw_list:
##            kw = tok.text.decode('utf-8')
            if len(kw)<2:continue
            if p.search(kw) != None:continue
            klist.append(kw.encode('utf-8'))
        if not fname in klist:
            klist.append(fname)
        #book_state={'rid':rid,'relpath':rlpath,'lastpub':time.time(),'bookpath':bookpath}
        if klist != []:
            try:
                self.logger.debug(u'pubBook: publishing '+data+u' with keywords: '+(' '.join(klist).decode('utf-8')))
                self.kserver.publishRes(klist,base64.b16encode(rid),data,rtype,rloc,meta_list,'SELF')
            except Exception, inst:
                self.logger.error('pubBook:'+traceback.format_exc())
                self.logger.error('pubBook: catched exception: '
                             + str(inst))
                return False
##        self.states[rid]={'relpath':rlpath,'lastpub':time.time(),'bookpath':bookpath}
        return True


    def getNovelFileList(self):
        """
        return a list of file with following suffix:
            txt/html/htm/epub/umd/jar/zip/rar
        following files will be excluded:
            - filesize smaller than 256KB
            -
        """
        ext_list=['txt','html','htm','epub','umd','jar','zip','rar']
        rlist=[]
        #p = re.compile('^[0-9_]+$')
        for root,dirs,files in os.walk(self.root):
            for fname in files:
                if os.path.splitext(fname)[1].lower()[1:] in ext_list:
                    #if p.match(os.path.splitext(fname)[0]) == None:
                    fpath=os.path.join(root,fname)
                    if os.stat(fpath).st_size>=256000: # this is to avoid publishing small file
                        rlist.append(fpath)
        return rlist

    def run(self):
##        mmseg.dict_load_chars(cur_file_dir()+os.sep+'chars.dic')
##        mmseg.dict_load_words(cur_file_dir()+os.sep+'booknames.dic')
        time.sleep(10)#wait for KADP startup
##        self.loadStates()
        while self.running == True:
            flist=self.getNovelFileList()
            for book in flist:
                self.pubBook(book)
                if self.running == False:
##                    self.saveStates()
                    return
                time.sleep(3)
            time.sleep(60)
##            self.saveStates()
        return

    def stop(self):
        self.running=False




if __name__ == '__main__':

##    import signal
##    def signal_handler(signal, frame):
##        global kp
##        print 'You pressed Ctrl+C!'
##        kp.stop()
##    signal.signal(signal.SIGINT, signal_handler)
    if len(sys.argv)>=2:
        sroot=sys.argv[1]
        try:
            kcurl=sys.argv[2]
        except:
            kcurl='http://127.0.0.1:50201/'
        kp = KPUB(sroot,kcurl=kcurl)
        kp.start()
        print "starting..."
        while True:
            try:
                kp.join(1)
            except KeyboardInterrupt:
                print "stopped"
                kp.stop()
                break
    else:
        print "kpub <share_root> <ctrl_url>"
