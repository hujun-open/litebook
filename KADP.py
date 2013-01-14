#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Name:        KADP, a Kademlia based P2P protocol
# Purpose:
#
#
# Author:      Hu Jun
#
# Created:     12/09/2011
# Copyright:   (c) Hu Jun 2011
# Licence:     GPLv3
# for latest version, visit project's website: http://code.google.com/p/ltbnet/
#
# ------------------------------------------------------------------------------

#
# todo: need to fix some exception while kpubing
#
#

#import inspect
import platform
MYOS = platform.system()
import sys
import traceback
import os
import urllib
import os.path
import subprocess
import cPickle
import longbin
from operator import attrgetter
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer, task
from twisted.application.internet import TimerService
from twisted.internet.protocol import Protocol, Factory
import hashlib
import socket
import SocketServer
import threading
import time
import struct
import random
import chardet
import Queue
import urlparse
import ConfigParser
import netifaces
##if MYOS != "Darwin":
##    import netifaces
##else:
##    from netifaces_osx import netifaces


# import wx.lib.newevent

import xmlrpclib
from twisted.web.xmlrpc import XMLRPC, withRequest
from twisted.web import server as TW_xmlserver
import base64
import logging
from logging.handlers import DatagramHandler
#from logging.handlers import SysLogHandler
##from pymmseg import mmseg


KPORT = 50200 #UDP port for KADP message
KCPORT = 50201 #tcp port for xmlRPC


# (ResouceUpdateEvt,EVT_RU)=wx.lib.newevent.NewEvent()

def AnyToUnicode(input_str, coding=None):
    """Convert any coding str into unicode str. this function should used with function DetectFileCoding"""

    if isinstance(input_str, unicode):
        return input_str
    if coding != None:
        if coding != 'utf-8':
            if coding.lower() == 'gb2312':
                coding = 'GBK'
            coding = coding.upper()
            output_str = unicode(input_str, coding, errors='replace')
        else:
            output_str = input_str.decode('utf-8', 'replace')
    else:
        output_str = unicode(input_str, 'gbk', errors='replace')
    return output_str

def getOSXIP():
    """
    return the ethernet interface ip that in the OSX
    """
    int_list=netifaces.interfaces()
    if 'en0' in int_list:
        return netifaces.ifaddresses('en0')[2][0]['addr']
    for intf in int_list:
        int_info=netifaces.ifaddresses(intf)
        if 2 in int_info and 18 in int_info:
            return int_info[2][0]['addr']
    return False

class KQueue(Queue.Queue):
    """
    FIFO Q, if maxsize is reached, then oldest item will be removed
    """

    def __init__(self,maxsize,logger):
        Queue.Queue.__init__(self,maxsize)
        self.maxlen=maxsize
        self.logger=logger

    def put(self,item,block=True,timeout=None):
        if self.full() == True:
            try:
                self.get_nowait()
            except Exception, inst:
                self.logger.error('KQueue.put:'+traceback.format_exc())
                self.logger.error('KQueue.put: catched exception: '
                             + str(inst))
        try:
            Queue.Queue.put(self,item,block=False)
        except Exception, inst:
            self.logger.error('KQueue.put:'+traceback.format_exc())
            self.logger.error('KQueue.put: catched exception: '
                         + str(inst))


class KADResList:

    """
    This class is used to store all known resources (KADRes)
    the structure is:
        - {kw:{rid:[res,]}
    """

    def __init__(self,proto):
        """proto is the KADProtocol
        """
        self.reslist = {}
        self.tExpire=86500
        self.tReplicate=3600
        self.tRepublish=86400
        self.proto=proto #This is the KADProtocol
        self.SALT = 'DKUYU'#salt for hashing

    def __contains__(self,res):
        """
        check if the specified res is in
        with same rid and rloc
        """

        for kw in self.reslist.values():
            if res.rid.val in kw:
                for r in kw[res.rid.val]:
                    if r.rloc == res.rloc: return True
        return False

    def setPubed(self,res,pubed=True):
        """
        set the published status of res
        """
        for kw in self.reslist.values():
            if res.rid.val in kw:
                for r in kw[res.rid.val]:
                    if r.rloc == res.rloc:
                        r.published=pubed
                        return True

    def isPubed(self,res):
        """
        check if the res is in the local list and already published
        """
        for kw in self.reslist.values():
            if res.rid.val in kw:
                for r in kw[res.rid.val]:
                    if r.rloc == res.rloc and r.published==True:
                        return True
        return False

    def clearAll(self):
        """
        clear all stored res
        """
        self.reslist={}

    def add_res(self, kw, res_list, src_nodeid):
        """
        kw is a keyword, must be unicode, return False otherwise
        res is a list of KADRes
        src_nodeid is a 20bytes str of source NodeID
        """
        if not isinstance(kw,unicode):
            self.proto.logger.warning(u'add_res:kw is not unicode')
            return False

        if not kw in self.reslist:
            self.reslist[kw] = {}
        for res in res_list:
            if not (res.rid.val in self.reslist[kw].keys()):
                self.reslist[kw][res.rid.val] = [res,]
            else:
                found = False
                for r in self.reslist[kw][res.rid.val]:
                    if r.owner_id == res.owner_id:
                        if res.owner_id == src_nodeid: #only replace the existing res when owner is publishing
                            self.reslist[kw][res.rid.val].remove(r)
                            self.reslist[kw][res.rid.val].append(res)
                        found = True
                        break
                if found == False: # if the res is from another owner
                    self.reslist[kw][res.rid.val].append(res)


    def get_res_list(self, kw, rtype=0):
        """
        return a list of all resources that has kw and rtype
        kw is a keyword string
        rtype is resource type,a integer,0 means all types match
        return False if kw is not found.
        """
        rlist=[]
        for cur_kw in self.reslist.keys():
            if cur_kw.find(kw)!=-1:
        #if kw in self.reslist: #no need for search for kw one by one, because
                for rl in self.reslist[cur_kw].values():
                    for r in rl:
                        if r.type == rtype or rtype == 0:
                            found=False
                            for xr in rlist: #if same res and rloc found in rlist, then skip this one.
                                if xr.rid == r.rid and xr.rloc == r.rloc:
                                    found=True
                                    break
                            if found == False: rlist.append(r)
        if len(rlist) != 0:
            return rlist
        else:
            return False

    def del_res(self,rid,owner_id,kw=None):
        """
        remove a res from the list
        """
        if kw != None: #if kw is known
            if not kw in self.reslist: return
            for r in self.reslist[kw][rid]:
                if r.owner_id == owner_id:
                    self.reslist[kw][rid].remove(r)
                    break
        else:# if kw is unknow
            for rid_list in self.reslist.values():
                for rl in rid_list.values():
                    for r in rl:
                        if r.owner_id == owner_id and r.rid == rid:
                            rl.remove(r)
                            break

    def remove_expired_res(self):
        """
        remove all expired res
        """

        for rid_list in self.reslist.values():
            for rl in rid_list.values():
                for r in rl:
                    curtime=time.time()
                    if curtime - r.creation_time >= self.tExpire:
                        rl.remove(r)

    def get_all_res(self):
        """
        yield all non-expired (kw, res)
        it will also remove exipred res
        """

        for (kw,rid_list) in self.reslist.items():
            for rl in rid_list.values():
                for r in rl:
                    curtime = time.time()
                    delta = curtime - r.creation_time
                    if  delta >= self.tExpire:
                        rl.remove(r)
                    else:
                        yield (kw,r)

    def replicate(self):
        self.proto.logger.debug('Start replicating RES')
        for (kw,rid_list) in self.reslist.items():
            for rl in rid_list.values():
                for r in rl:
                    curtime = time.time()
                    delta = curtime - r.creation_time
                    if  delta >= self.tExpire:
                        rl.remove(r)
                    else:
                        self.proto.logger.debug("KADResList_replicate:"+self.proto.knode.nodeid.val+"'s task_list has "+str(len(self.proto.task_list)))
                        #self.proto.logger.debug(u"replicate: 中文怎么就不行".encode('utf-8')) #need to convert it to utf-8
                        #self.print_me()
                        self.proto.PublishRes([kw,],r)

    def republish(self):
        self.proto.logger.debug('entering republish')
        #self.proto.logger.debug(u'这是一个测试'.encode('utf-8'))

        for (kw,rid_list) in self.reslist.items():
            for rl in rid_list.values():
                for r in rl:
                    curtime = time.time()
                    delta = curtime - r.creation_time
                    if  delta >= self.tExpire:
                        rl.remove(r)
                    else:
                        if r.owner_id == self.proto.knode.nodeid.val:
                            self.proto.logger.debug(u"republish: "+kw+u" "+unicode(r))
                            #self.print_me()
                            self.proto.PublishRes([kw,],r)

    def print_me(self):
        self.proto.logger.debug("kw list has:\n")
        for kw in self.reslist.keys():
            self.proto.logger.debug(kw.encode('utf-8'))
            #print kw
        for (kw,rid_list) in self.reslist.items():
            for rl in rid_list.values():
                for r in rl:
                    self.proto.logger.debug(kw.encode('utf-8')+'---'+
                                        r.rloc.encode('utf-8')+" "+r.owner_id.encode('hex_codec'))
                    #print kw+u'---'+unicode(r.rloc)+u" "+unicode(r.owner_id)


    def saveRes(self):
        fname = self.proto.getConfigDir()+os.sep+'resl.kadp'
        savef = open(fname, 'wb')
        saves = cPickle.dumps(self.reslist, 2)
        t=time.time()
        saves = struct.pack('f',time.time()) + saves
        m = hashlib.sha224()
        m.update(saves+self.SALT)
        savef.write(m.digest()+saves) #use sha224 to hash
        savef.close()

    def loadRes(self):
        self.proto.logger.debug("loading Res from "+self.proto.getConfigDir()+os.sep+'resl.kadp')
        fname = self.proto.getConfigDir()+os.sep+'resl.kadp'
        if not os.path.exists(fname):
            return False
        try:
            savef = open(fname, 'rb')
            loads = savef.read()
            m = hashlib.sha224()
            m.update(loads[28:]+self.SALT)
            if m.digest() != loads[:28]:
                return False
            if time.time() - (struct.unpack('f',loads[28:32])[0]) > self.tExpire:
                return False
            rl = cPickle.loads(loads[32:])
            savef.close()
        except Exception, inst:
            self.proto.logger.error("loadRes failed\n")
            self.proto.logger.error(str(inst))
            return False
        self.reslist = rl
        return True




class KADFile:

    def __init__(
        self,
        ifname=None,
        fsize=None,
        fid=None,
        fpath='',
        ):
        """
        fpath is full path of the file.
        KADFile has following propeties:
            - id, 20 bytes string
            - name, unicode
            - size, int
        """

        if fpath != '' and fpath != None:
            fname = os.path.basename(fpath)
            self.name = AnyToUnicode(fname)
            self.size = os.path.getsize(fpath)
            inf = open(fpath, 'rb')
            m = hashlib.sha1()
            m.update(inf.read())
            self.id = m.digest()
            inf.close()
        else:
            self.name = AnyToUnicode(ifname)
            self.size = fsize
            self.id = fid


##class KADNovel(KADFile):
##    """
##    This is class for Novel, with metadata for novels like author, title.
##    """
##    def __init__(self,fpath):
##        """
##        fpath is the full path of novel
##        title is title of the novel, it might be different from the filename
##        author is the author of the novel
##        """
##        KADFile.__init__(fpath=fpath)
##        (fbasename,fext) = os.path.splitext(fpath)
##        fext = fext.lower()
##        self.title = fbasename
##        self.author = ''
##        self.meta_list = {}
##        if fext == '.epub':
##            meta_list = getEPUBMeta(fpath)
##            if meta_list != False and meta_list != {}:
##                self.title = meta_list['title']
##                self.author = meta_list['creator']
##                self.meta_list = meta_list


class KADTreeNode:

    def __init__(self, nodedata=None, parentnode=None):
        self.left = None
        self.right = None
        self.parent = parentnode
        self.bucket = []
        self.latime = 0 #last time of looking-up in the bucket, 0 means no looking-up since creation
        self.position = None  # left or right child of parent


class KADTree:

    def __init__(self, proto, max_level=160):
        self.root = KADTreeNode(None)
        self.bucket_size = 20  # maximum contacts in one bucket
        self.proto = proto
        self.max_level = max_level
        self.count = 0
        self.tExpire = 864000 #10 days
        self.SALT = 'DKUYU'#salt for hashing
        self.found = False #used by get1stIB()

    def getRoot(self):
        return self.root

    def insertBucket(
        self,
        bucket,
        newnode,
        iforce=False,
        ):
        """Insert a contact into a bucket
           bucket is a list
           newnode ia KADNode
        """


        newnode.lastsee = time.time()
        for node in bucket:
            if node.nodeid == newnode.nodeid:

                # if newknode already exist

                self.proto.logger.debug('insertBucket---- node already existed in bucket, updated'
                             )
                bucket.remove(node)
                node.lastsee = time.time()
                bucket.append(node)
                bucket.sort(key=attrgetter('lastsee'))
                return
        if len(bucket) < self.bucket_size:  # if bucket is NOT full
            self.proto.logger.debug('KADTree.insertBucket:add new contact')
            bucket.append(newnode)
            self.count += 1
            return
        if len(bucket) >= self.bucket_size:  # bucket is full
            self.proto.logger.debug("InsertBucket: bucket full")
            if iforce == True:
                bucket[self.bucket_size - 1] = newnode
            else:

                 # ping 1st node

                self.proto.logger.debug('insertBucket:bucket is full, ping the 1st node'
                             )
                pseq = self.proto.getSeq()
                self.proto.task_list[pseq] = {'task': 0,
                        'object': {'bucket': bucket, 'node': newnode}}
                self.proto.Ping(bucket[0], self.proto.PingCallback,
                                pseq)


    def remove(self,nodeid):
        """
        remove a contact
        nodeid is LongBin
        """
        bucket = self.getBucket(nodeid)
        for c in bucket:
            if c.nodeid == nodeid:
                bucket.remove(c)
                self.count-=1
                break

    def insert(self, newnode):
        """insert a KADNode into tree
            newnode is a KADNode
        """

        if self.proto.knode.nodeid == newnode.nodeid:  # return if contact is self
            return
        self.insertBucket(self.getBucket(newnode.nodeid),newnode)



    def getBucket(self, nodeid):
        """ return the bucket that nodeid belongs to
            nodeid is a LongBin
        """

        delta = self.proto.knode.nodeid ^ nodeid
        tks = str(delta)
        pnd = self.root
        level = 1
        for c in tks:
            if c == '0':
                if level <= 3:
                    if pnd.right == None:
                        newtnode = KADTreeNode(parentnode=pnd)
                        pnd.right = newtnode
                    pnd = pnd.right
                elif level <= 159:
                    if int(tks[:level], 2) in range(5):  # keep descending
                        if pnd.right == None:
                            newtnode = KADTreeNode(parentnode=pnd)
                            pnd.right = newtnode
                        pnd = pnd.right
                    else:
                        return pnd.bucket
                elif level == self.max_level:
                    return pnd.bucket
            else:
                if level <= 3:
                    if pnd.left == None:
                        newtnode = KADTreeNode(parentnode=pnd)
                        pnd.left = newtnode
                    pnd = pnd.left
                elif level <= 159:
                    if int(tks[:level], 2) in range(5):  # keep descending
                        if pnd.left == None:
                            newtnode = KADTreeNode(parentnode=pnd)
                            pnd.left = newtnode
                        pnd = pnd.left
                    else:
                         return pnd.bucket
                elif level == self.max_level:
                    return pnd.bucket
            level += 1

    def get_list(
        self,
        rlist,
        maxn=None,
        rootnode=None,
        ):
        """
        return at least maxn KADNode in rlist
        rlist should be []
        maxn is an integer
        """

        if rootnode == None:
            cnode = self.root
        else:
            cnode = rootnode
        rlist += cnode.bucket
        if maxn != None and len(rlist) >= maxn:
            return
        if cnode.left == None and cnode.right == None:
            return
        else:
            if cnode.left != None:
                self.get_list(rlist, maxn, cnode.left)
            if cnode.right != None:
                self.get_list(rlist, maxn, cnode.right)

    def get_count(self):
        """
        return the total number of contacts
        """

        clist = []
        self.get_list(clist)
        return len(clist)



    def get1stIB(self):
        """
        get the nid of first idle bucket in the tree.
        the found nid will be put in self.found
        """
        self.found=None
        self.get_idle_bucket(self.root)
        return self.found

    def get_idle_bucket(self,rootnode,nid=''):
        """
        support function for get1stIB()
        """

        if self.found != None:
            return
        #print "latime is ",rootnode.latime, " vaule is ",rootnode.bucket
        if time.time() - rootnode.latime>self.proto.tRefresh and \
                            rootnode.left == None and rootnode.right == None:
            #print "found nid is ",nid
            self.found=nid
            return
        if rootnode.left == None and rootnode.right == None:
            return

        if rootnode.left != None and self.found == None:
            r1=self.get_idle_bucket(rootnode.left,nid+'1')

        if rootnode.right != None and self.found == None:
            r2=self.get_idle_bucket(rootnode.right,nid+'0')




    def print_me(self,rootnode,nid=''):
        """
        print the tree
        """
        #print "i am in level ",level
        if rootnode.bucket != []:
            self.proto.logger.debug('current nid is ---- ' + nid)
            for c in rootnode.bucket:
                self.proto.logger.debug(c.nodeid.hexstr())
                self.proto.logger.debug(c.strME())
                self.proto.logger.debug("_____________")
        if rootnode.left==None and rootnode.right==None:
            return

        if rootnode.left !=None:
            self.print_me(rootnode.left,nid+'1')
        if rootnode.right !=None:
            self.print_me(rootnode.right,nid+'0')


    def get_closest_node(self, target_id):
        """
        return the tree node that target_id belongs to
        target_id is LongBin
        """

##        if self.proto.knode.nodeid==target_id: #return if contact is self
##            return None

        delta = self.proto.knode.nodeid ^ target_id
        tks = str(delta)
        pnd = self.root
        level = 1
        for c in tks:
            if c == '0':
                if level <= 3:
                    if pnd.right == None:
                        newtnode = KADTreeNode(parentnode=pnd)
                        pnd.right = newtnode
                    pnd = pnd.right
                elif level <= 159:
                    if int(tks[:level], 2) in range(5):  # keep descending
                        if pnd.right == None:
                            newtnode = KADTreeNode(parentnode=pnd)
                            pnd.right = newtnode
                        pnd = pnd.right
                    else:

                         # go into bucket
                        pnd.latime=time.time()
                        return pnd
                elif level == self.max_level:
                    pnd.latime=time.time()
                    return pnd
            else:
                if level <= 3:
                    if pnd.left == None:
                        newtnode = KADTreeNode(parentnode=pnd)
                        pnd.left = newtnode
                    pnd = pnd.left
                elif level <= 159:
                    if int(tks[:level], 2) in range(5):  # keep descending
                        if pnd.left == None:
                            newtnode = KADTreeNode(parentnode=pnd)
                            pnd.left = newtnode
                        pnd = pnd.left
                    else:

                         # go into bucket
                        pnd.latime=time.time()
                        return pnd
                elif level == self.max_level:
                    pnd.latime=time.time()
                    return pnd
            level += 1

    def get_closest_list(self, target_id, maxn=None):
        """
        return a sorted list with no more than maxin closest contacs to target_id
        target_id is a LongBin
        """

        rlist = []
        if maxn == None:
            maxn = self.proto.k
        pnd = self.get_closest_node(target_id)
        while len(rlist) < maxn:
            clist = []
            if pnd.parent == None:
                break
            else:
                pnd = pnd.parent
            self.get_list(rlist, rootnode=pnd)
            rlist += clist
        rlist = sorted(rlist, key=lambda c: c.nodeid ^ target_id)
        return rlist[:maxn]

    def saveContact(self):
        fname = self.proto.getConfigDir()+os.sep+'kcl.kadp'
        savef = open(fname, 'wb')
        clist = []
        self.get_list(clist)
        saves = cPickle.dumps(clist, 2)
        saves = struct.pack('f',time.time()) + saves
        m = hashlib.sha224()
        m.update(saves+self.SALT)
        savef.write(m.digest()+saves) #use sha224 to hash
        savef.close()

    def loadContact(self):
        self.proto.logger.debug("loading contact from "+self.proto.getConfigDir()+os.sep+'kcl.kadp')
        fname = self.proto.getConfigDir()+os.sep+'kcl.kadp'
        if not os.path.exists(fname):
            self.proto.logger.error("can not open "+fname)
            return False
        try:
            savef = open(fname, 'rb')
            loads = savef.read()
            m = hashlib.sha224()
            m.update(loads[28:]+self.SALT)
            if m.digest() != loads[:28]:
                return False
            if time.time() - (struct.unpack('f',loads[28:32])[0]) > self.tExpire:
                self.proto.logger.warning('loadContact: saved contacts expired')
                return False
            bl = cPickle.loads(loads[32:])
            savef.close()
        except Exception, inst:
            self.proto.logger.error('loadContact:'+traceback.format_exc())
            self.proto.logger.error('loadContact: catched exception: '
                         + str(inst))
            return False
        if len(bl)>0:
            for c in bl:
                self.insert(c)
            if self.get_count >0:
                return True
            else:
                return False
        else:
            self.proto.logger.error("No contact in the saved file")
            return False


class KADNode:

    def __init__(
        self,
        nodeid=None,
        ip=None,
        port=None,
        nodes=None,
        ):
        """nodeid is LongBin
        ip is string
        port is int
        nodes if a string=4bytes_IP+2bytes_port+20bytes_nodeid,when present,
        other parameter will be ignored.
        """


        if nodes == None:
            self.nodeid = nodeid
            self.v4addr = ip
            self.port = port
        else:
            if len(nodes) != 26:
                raise ValueError('KADNode__init__:nodes must be 26 bytes long,got '
                                + str(len(nodes)) + ' bytes instead')
                return
            ips = nodes[:4]
            self.v4addr = ''
            ipl = struct.unpack('cccc', ips)
            for i in ipl:
                self.v4addr += str(ord(i)) + '.'
            self.v4addr = self.v4addr[:-1]
            self.port = struct.unpack('H', nodes[4:6])
            self.nodeid = longbin.LongBin(nodes[6:26])

        self.lastsee = time.time()
        self.status = 'init'  # status is one of 'init'/'firewalled'/'clear'/'unreachable'
        self.distance = None

    def __str__(self):
        """Generate a binary str=4bytes_IP+2bytes_port+20bytes_nodeid"""

        ips = ''
        ipl = self.v4addr.split('.')
        for i in ipl:
            ips += struct.pack('c', chr(int(i)))
        ports = struct.pack('H', self.port)
        return ips + ports + self.nodeid.val

    def strME(self):
        """
        Generate a printable string for the KADNode
        """
        rs=''
        rs+="NodeId:"+self.nodeid.hexstr()+"-----"
        rs+="Addr:"+self.v4addr+":"+str(self.port)
        return rs



class KADRes:

    """
    Resrouce
    """

    def __init__(
        self,
        rid,
        data,
        rtype=1,
        rloc=None,
        metadata={},
        owner_id='SELF',
        ctime=None
        ):
        """
        rid is a LongBin, represent the resource id
        data is resource data, could be any thing
        rtype is the type of resouce, a integer
        rloc is the location of the resource,like HTTP URL
        metadata is a dict include meta data for the resources, e.g filesize
        ctime is the creation time(int sec)
        owner_id is a str
        """

        self.rid = rid
        self.data = data
        self.type = rtype
        if ctime == None:
            self.creation_time = time.time()
        self.rloc = rloc
        self.meta_list = metadata
        self.owner_id=owner_id
        self.published=False #if this res has been successfully published


##class KAD_Req:
##
##    def __init__(
##        self,
##        dst_node,
##        code,
##        seq,
##        attr_list=None,
##        send_time=0,
##        ):
##        self.dst_node = dst_node
##        self.code = code
##        self.seq = seq
##        self.attr_list = attr_list
##        self.create_time = time.time()
##        self.send_time = send_time



##raising Exception should not be used in network protocol.
##class ParseError(Exception):
##    def __init__(self,msg,packet):
##        self.msg=msg
##        self.wrong_packet=packet
##    def __str__(self):
##        return self.msg
##
##class EncapError(Exception):
##    def __init__(self,msg):
##        self.msg=msg
##    def __str__(self):
##        return self.msg
##
##class ProtoError(Exception):
##    """
##    id is the ErrorID, following is a table of all defined ID:
##        - 1: no contact in contact list
##    """
##    def __init__(self,id):
##        self.id=id
##
##    def __str__(self):
##        return str(self.id)

class KADProtocol(DatagramProtocol):

    def __init__(
        self,
        win=None,
        lport=KPORT,
        nodeid=None,
        addrf=None, #geoip address file, used for bootscan
        #dstnode=None,
        bip=None,#the ipaddr that protocol listen on,'' means any interface
        conf_dir=None,#the directory of configuration files
        force_scan=False,#force ip address scan
        cserver_url=None, #control server URL, a XMLRPC server URL that search result sent to
        nodebug=False, #if enabling display log at start
        ):
        global MYOS

##        mmseg.dict_load_defaults()

        # following are test code, should be removed

##        self.dstnode = dstnode

        # end of test code
        # current index for bootscan

        self.current_ii = 0
        self.current_ai = 0
        self.bip = bip
        self.conf_dir = conf_dir
        try:
            self.cserver = xmlrpclib.Server(cserver_url)
        except:
            self.cserver = None


        self.rptlist = None

        self.packet_seq = 0
        self.msg_code_list = range(11)
        self.win = win
        self.numofcontact = 0
        #self.default_lport = KPORT
        self.bstrap_url = 'http://boot-ltbnet.rhcloud.com/?'
        self.chkport_url = 'http://boot-ltbnet.rhcloud.com/check?'
        self.port_open_status = 'INIT' #'INIT' means unknow, 1 means open,-1 means closed, 0 means waiting
        self.port_open_nonce = None
        self.force_scan = force_scan



        # the following two dic apply to all RPCs

        self.req_list = {}  # seq of reqest packet as the key, used for re-tran
        self.task_list = {}  # seq of reqest packet as the key, used to do real job

        # task == 0 replace contact
        #
        #
        #

        self.send_interval = 8  # re-transmission interval, in seconds
        self.max_resend = 2  # max number of times for re-tran

        #some protocol timers
        self.tClearResInterval=600 #interval of clear expired res
        self.tExpire=86500 #expire time for res, will be reset by owner publish
        self.tRefresh=3600 #refersh time for bucket
        self.tReplicate=3600 #republish time for all res in res list
        self.tRepublish=86400 #republish time for owning res


        #test code
##        self.tReplicate=600 #republish time for all res in res list
##        self.tRepublish=1200 #republish time for owning res
        #end of test code

        # parameter for bootscan

        self.run_bootscan = False  # enable/disable bootscan
        self.run_bootscan_interval = 1  # number of seconds
        self.max_bootscan_answers = 20  # change interval or stop bootscan when got this number of contacts


        self.buck_list = KADTree(self)
        self.rlist = KADResList(self)  # resource list
        self.k = 20
        self.buck_size = self.k
        self.alpha = 3
        self.buck_list_len = 160



        #some scale limit
        self.MAX_NUM_CONTACT = 5000
        self.MAX_NUM_RES = 50000


        # create logger

        self.logger = logging.getLogger("KADP")
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
        self.logger.disabled = nodebug

        #create Qs
        self.updateContactQ = KQueue(512,self.logger)
        self.FindNodeReplyQ = Queue.Queue()
        self.BootReplyQ = Queue.Queue()
        self.StoreReplyQ = Queue.Queue()
        self.FindValueReplyQ = Queue.Queue()

        #try to load the configuration file
##        if nodeid != None:
##            testc = True
##        else:
##            self.logger.debug("loading KADP config...")
##            testc = not self.loadConfig()
##
##        if testc == True:
##            self.listening_port = lport
##            if nodeid != None:
##                self.knode = KADNode(nodeid,
##                                     socket.gethostbyname(socket.gethostname()),
##                                     lport)
##            else:
##                self.knode = KADNode(self.genNodeID(),
##                                     socket.gethostbyname(socket.gethostname()),
##                                     lport)
        self.listening_port = lport
        if MYOS=='Darwin':
            myhostip=getOSXIP()
        else:
            myhostip=socket.gethostbyname(socket.gethostname())

        if nodeid != None:
            self.knode = KADNode(nodeid,
                                 myhostip,
                                 lport)
        else:
            self.knode = KADNode(self.genNodeID(),
                                 myhostip,
                                 lport)
        self.rlist.loadRes()



        # bootstrapping code by scan IP space of CT/CU/CM
        # load addr list into self.addrlist as list of [start_addr,count,network]

        self.addrlist = LoadAddr(addrf)

        #

        self.bookext_list = ['txt', 'umd', 'jar']

    def getInfo(self):
        """
        return lport and self nodeid as string
        """
        return [self.listening_port,str(self.knode.nodeid)]

    def printme(self):
        return [self.listening_port,self.knode.nodeid.hexstr()]

    def setTaskList(self, rptlist):
        self.rptlist = rptlist

    def getDBcastAddr(self, addr, netmask):
        """return a subnet broadcast address
        """

        alist = addr.split('.')
        nmlist = netmask.split('.')
        if len(alist) != 4 or len(nmlist) != 4:
            return None

##        try:

        a1 = int(alist[0])
        if a1 == 127 or a1 >= 224 or a1 == 0:
            return None
        tlist = []
        for x in alist:
            if int(x) <= 0 or int(x) > 255:
                return None
            tlist.append(chr(int(x)))
        fms = 'cccc'
        rs = struct.pack(fms, tlist[0], tlist[1], tlist[2], tlist[3])
        fms = 'I'
        ai = struct.unpack(fms, rs)
        tlist = []
        for x in nmlist:
            if int(x) < 0 or int(x) > 255:
                return None
            tlist.append(chr(int(x)))
        fms = 'cccc'
        rs = struct.pack(fms, tlist[0], tlist[1], tlist[2], tlist[3])
        fms = 'I'
        ni = struct.unpack(fms, rs)

##        except:
##            return None

        fms = 'cccc'
        rs = struct.pack(fms, chr(255), chr(255), chr(255), chr(255))
        fms = 'I'
        allone = struct.unpack(fms, rs)
        tmpi = allone[0] ^ ni[0]
        dbi = ai[0] | tmpi
        fms = 'I'
        rs = struct.pack(fms, dbi)
        fms = 'cccc'
        (s1, s2, s3, s4) = struct.unpack(fms, rs)
        rlist = (s1, s2, s3, s4)
        dbcast = ''
        for r in rlist:
            dbcast += str(ord(r)) + '.'
        return dbcast[:-1]

    def genNodeID(self):
        """
        Generate NodeID for self
        """
        global MYOS
        if MYOS == 'Darwin':
            hostip=getOSXIP()
        else:
            hostip = socket.gethostbyname(socket.gethostname())
        hostname = socket.gethostname()
        times = str(time.time())
        fid = '00000000000000000000'
        while fid == '00000000000000000000':
            rrr = str(random.randint(1, 10000))
            m = hashlib.sha1()
            m.update(rrr + ':' + times + ':' + hostip + ':' + hostname)
            for x in range(5):#repeat random seeding for 5 times
                rrr = str(random.randint(1, 10000))
                m.update(rrr)
            fid = m.digest()
        return longbin.LongBin(fid)

    def ErrCallback(self, fail):

        self.logger.error('ErrBack:' + fail.getErrorMessage())

    def FindNodeCallback(self, r):

        try:  # otherwise the exception won't get print out
            if r['result'] != 'NoContact':
                self.logger.debug('Entering FindNodeCallback')
                taskseq = self.req_list[r['seq']]['taskseq']
                #self.logger.debug('taskseq is ' + str(taskseq))
                #self.logger.debug('the task is ' + str(self.task_list[taskseq]))
                if not taskseq in self.task_list:
                    self.logger.warning('FindNodeCallback: no such task')
                    return
                thetask = self.task_list[taskseq]
                #print taskseq,'--->',thetask['shortlist']
                for c in thetask['shortlist']:
                    if c['contact'].nodeid.val == r['src_id']:
                        c['status'] = 'answered'
                        if r['result'] != False:
                            self.logger.debug('FindNodeCallback: found '
                                         + str(c['contact'].nodeid.hexstr()))
                        thec = c
                        break
            if r['result'] == True:  # if got the reply to FindNode

                self.logger.debug('FindNodeCallback:Got the answer')
                host_alist = r['attr_list'][4]

                # following code is used to add all contacts from FindNodeReply into buck_list
                # you may want to change this behavior

                for h in host_alist:
                    newnode = KADNode(h['nodeid'], h['ipv4'], h['port'])
                    newnode.distance = newnode.nodeid ^ thetask['target'
                            ]
                    found = False
                    for s in thetask['shortlist']:
                        if s['contact'].nodeid == newnode.nodeid:
                            s['contact'] = newnode
                            found = True
                            break
                    if found == False:
                        thetask['shortlist'
                                ].append({'contact': newnode,
                                'status': 'init'})
                        self.updateContactQ.put(newnode)
                thetask['shortlist'].sort(key=lambda c: c['contact'
                        ].distance)
                thetask['shortlist'] = (thetask['shortlist'])[:self.k]
                thetask['onthefly'] -= 1
                if thetask['onthefly'] < 0:
                    thetask['onthefly'] = 0
                found = False
                self.logger.debug('onthefly is ' + str(thetask['onthefly']))
                #print 'short list is', thetask['shortlist']
                for c in thetask['shortlist']:
                    if c['status'] == 'init':
                        found = True
                        if thetask['onthefly'] < self.alpha:
                            c['status'] = 'sent'
                            self.logger.debug('FindNodeCallback:send another FindNode'
                                    )
                            self.FindNode(c['contact'], thetask['target'
                                    ], self.FindNodeCallback,
                                    taskseq=taskseq)
                            thetask['onthefly'] += 1
                            break  # twisted doesn't have any sending buffer, you need release the control to reactor to do the sending, if reactor doesn't have chance to gain the control, then then packet may NOT have chance to get sent
                    elif c['status'] != 'answered':
                        found = True

                if found == False:  # lookup stops
                    self.logger.debug('FindNodeCallback: Stopped')
                    self.logger.debug('FindNodeCallback: '+self.knode.nodeid.hexstr()+' found '+str(len(thetask['shortlist']))+' contacts')
                    del self.task_list[taskseq]
                    thetask['defer'
                            ].callback({'context': thetask['callback_context'
                            ], 'shortlist': thetask['shortlist'],
                            'result': True})

                    # following are test code

##                    for c in thetask['shortlist']:
##                        print c['contact'].nodeid.val
            elif r['result'] == 'NoContact':

                                          # if there is no contact in local buck_list
                # send signal to wx app
                self.logger.debug('FindNodeCallback:No Contact')
                return
            else:

                 # if there is no answer
                self.logger.warning("FindNodeCallback: "+str(r['seq'])+" NO ANSWER FROM "+r['src_id'].encode('hex_codec'))
                thetask['shortlist'].remove(thec)
                self.buck_list.remove(thec['contact'].nodeid)
                thetask['onthefly'] -= 1
                if thetask['onthefly'] < 0:
                    thetask['onthefly'] = 0
                found = False
                for c in thetask['shortlist']:
                    if c['status'] == 'init':
                        found = True
                        if thetask['onthefly'] < self.alpha:
                            c['status'] = 'sent'
                            self.FindNode(c['contact'], thetask['target'
                                    ], self.FindNodeCallback,
                                    taskseq=taskseq)
                            thetask['onthefly'] += 1
                    elif c['status'] != 'answered':
                        found = True

                if found == False:  # lookup stops
                    self.logger.debug('FindNodeCallback:'+self.knode.nodeid.hexstr()+' found '+str(len(thetask['shortlist'])))
                    self.logger.debug('FindNodeCallback: Stopped')
                    del self.task_list[taskseq]
                    thetask['defer'
                            ].callback({'context': thetask['callback_context'
                            ], 'shortlist': thetask['shortlist'],
                            'result': False})

            del self.req_list[r['seq']]
        except Exception, inst:
                                 # otherwise the exception won't get print out
            self.logger.error('FindNodeCallback:'+traceback.format_exc())
            self.logger.error('FindNodeCallback: catched exception: '
                         + str(inst))


    def FindNodeReply(self):
        """Scan FindNodeReplyQ periodically and send FindNode-Reply
        return up to k closet contacts.
        """

        # print "FindNodeReply ---- running"

##        try:
##            (t_nodeid, src_node, rseq) = self.FindNodeReplyQ.get(False)
##        except Queue.Empty:
##            return

        newreqlist=[]

        for i in range(50):
            try:
                (t_nodeid, src_node, rseq,ctime) = self.FindNodeReplyQ.get(False)
                newreqlist.append((t_nodeid, src_node, rseq, ctime))
            except Queue.Empty:
                break
        if len(newreqlist) == 0: return

        for (t_nodeid, src_node, rseq, ctime) in newreqlist:
            if time.time()-ctime>self.send_interval*self.max_resend:
                with self.FindNodeReplyQ.mutex:
                    self.FindNodeReplyQ.queue.clear()
                self.logger.debug( "FindNodeReply: FindNodeReplyQ Cleared")
                return #clear the queue and return

            c_list = self.buck_list.get_closest_list(t_nodeid)
            attrs = ''
            for c in c_list:
                attrs += self.gen_attr(4, str(c))

            # r_attr=self.gen_attr(0,True) #result attr is needed for FindNode?
            # attrs+=r_attr

            (header, seq) = self.gen_header(5, self.knode.nodeid.val,
                    src_node.nodeid.val, rseq)
            packet = self.gen_packet(header, attrs)
            self.sendDatagram(src_node.v4addr, src_node.port, packet)
            self.logger.debug(str(rseq)+" Send FindNodeReply to "+src_node.nodeid.hexstr())

    def FindNode(
        self,
        dst_node,
        fnode_id,
        findnodecallback,
        iseq=None,
        taskseq=None,
        ):
        """FindNode RPC, this is primitive operation, not an iterative one.
        dst_node is knode that being contacted
        fnode_id is the key value is being looked for
        """


        (header, seq) = self.gen_header(4, self.knode.nodeid.val,
                dst_node.nodeid.val, iseq)
        attr = self.gen_attr(3, fnode_id.val)
        packet = self.gen_packet(header, attr)

        if not seq in self.req_list:  # if this is a new request
            self.logger.debug('Initiate a new FindNode...')
            d = defer.Deferred()
            d.addErrback(self.ErrCallback)
            d.addCallback(findnodecallback)  # you might want to change this
            self.sendDatagram(dst_node.v4addr, dst_node.port, packet)
            callid = reactor.callLater(
                self.send_interval,
                self.FindNode,
                dst_node,
                fnode_id,
                findnodecallback,
                seq,
                )
            self.req_list[seq] = {
                'code': 4,
                'callid': callid,
                'defer': d,
                'send_time': 1,
                'dst_node': dst_node,
                'fnode': fnode_id,
                'taskseq': taskseq,
                }
            #self.req_list[seq]['send_time'] += 1
            return
        else:
            if self.req_list[seq]['send_time'] > self.max_resend:

                # no respond, and max resend time reached

                self.logger.debug('stop sending FindNode,no answer from '
                             + dst_node.v4addr + ', calling callback')
                self.req_list[seq]['defer'].callback({'seq': seq,
                        'result': False, 'src_id': dst_node.nodeid.val})
            else:

                self.logger.debug('re-tran FindNode')
                self.sendDatagram(dst_node.v4addr, dst_node.port,
                                  packet)
                self.req_list[seq]['send_time'] += 1
                callid = reactor.callLater(
                    self.send_interval,
                    self.FindNode,
                    dst_node,
                    fnode_id,
                    findnodecallback,
                    seq,
                    )
                self.req_list[seq]['callid'] = callid

    def NodeLookup(self, target_key, callback_context=None):
        """
        the purpose of NodeLook is to find k closest contact to target_key(longbin)
        This is iterative operation, NOT primitive(like FindNode)
        target_key is a LongBin
        """


        self.logger.debug('init a new NodeLookup')
        cshortlist = self.buck_list.get_closest_list(target_key,
                self.alpha)


        if len(cshortlist) == 0:
            self.logger.debug("NodeLookup:cshosrtlist is empty")

            # this is how you handle error in protocol, always use callback
            # to clean-up, do NOT use raise exception.

            return self.FindNodeCallback({'result': 'NoContact'})

        for c in cshortlist:  # cal the distance to the target
            c.distance = c.nodeid ^ target_key

        shortlist = []
        for c in cshortlist:
            shortlist.append({'contact': c, 'status': 'init'})

        # use first seq number as the key for this task?

        d = defer.Deferred()
        thetask = {
            'shortest': shortlist[0],
            'onthefly': self.alpha,
            'shortlist': shortlist,
            'defer': d,
            'target': target_key,
            'callback_context': callback_context,
            }
        task_seq = self.getSeq()
        self.task_list[task_seq] = thetask
        for c in shortlist:
            c['status'] = 'sent'
            self.FindNode(c['contact'], target_key,
                          self.FindNodeCallback, taskseq=task_seq)
        return d  # return deferred, use addCallback() to add functions, this defered used to add different function for different purposes like publish,search ..etc.

    def FindValueCallback(self, r):

        try:  # otherwise the exception won't get print out
            self.logger.debug('Entering FindValueCallback')
            if r['result'] == 'NoContact':
                # if there is no contact in local buck_list
                # send signal to wx app
                self.logger.warning('FindValueCallback:No Contact')
                return
            taskseq = self.req_list[r['seq']]['taskseq']
##            self.logger.debug('taskseq is ' + str(taskseq))
##            self.logger.debug('the task is ' + str(self.task_list[taskseq]))
            if not taskseq in self.task_list:
                self.logger.warning('FindValueCallback: no such task')
                return
            thetask = self.task_list[taskseq]
##            print thetask['defer'].callbacks
##            print thetask['defer']._debugInfo

            for c in thetask['shortlist']:
                if c['contact'].nodeid.val == r['src_id']:
                    if 'attr_list' in r:
                        if 6 in r['attr_list']:
                            c['status'] = 'answered-file'
                        else:
                            c['status'] = 'answered'
                        self.logger.debug('FindValueCallback: found '
                                     + str(c['contact'].nodeid.hexstr()))
                    thec = c
                    break

            if r['result'] == True:  # if got the reply to FindNode
                self.logger.debug('FindValueCallback:Got the answer')
                if thec['status'] == 'answered-file':  # got the search result
                    self.logger.debug('FindValueCallback: got result from '
                                 + r['src_id'].encode('hex_codec'))
                    for xr in r['attr_list'][6]:
                        if not xr in thetask['rlist']:
                            thetask['rlist'].append(xr)

                # else:#got some contacts
                # process the contacts

                if 4 in r['attr_list']:
                    host_alist = r['attr_list'][4]

                    # following code is used to add all contacts from FindNodeReply into buck_list
                    # you may want to change this behavior

                    for h in host_alist:
                        newnode = KADNode(h['nodeid'], h['ipv4'],
                                h['port'])
                        newnode.distance = newnode.nodeid \
                            ^ thetask['target']
                        found = False
                        for s in thetask['shortlist']:
                            if s['contact'].nodeid == newnode.nodeid:
                                s['contact'] = newnode
                                found = True
                                break
                        if found == False:
                            thetask['shortlist'
                                    ].append({'contact': newnode,
                                    'status': 'init'})
                            self.updateContactQ.put(newnode)
                    thetask['shortlist'].sort(key=lambda c: c['contact'
                            ].distance)
                    thetask['shortlist'] = (thetask['shortlist'
                            ])[:self.k]
                thetask['onthefly'] -= 1
                if thetask['onthefly'] < 0:
                    thetask['onthefly'] = 0
                found = False
                self.logger.debug('onthefly is ' + str(thetask['onthefly']))
                #print 'short list is', thetask['shortlist']
                for c in thetask['shortlist']:
                    if c['status'] == 'init':
                        found = True
                        if thetask['onthefly'] < self.alpha:
                            c['status'] = 'sent'
                            self.logger.debug('FindValueCallback:send another FindValue'
                                    )
                            self.FindValue(c['contact'], thetask['kw'],
                                    thetask['rtype'],
                                    self.FindValueCallback,
                                    taskseq=taskseq)
                            thetask['onthefly'] += 1
                            break  # twisted doesn't have any sending buffer, you need release the control to reactor to do the sending, if reactor doesn't have chance to gain the control, then then packet may NOT have chance to get sent
                    elif c['status'] != 'answered' and c['status'] \
                        != 'answered-file':
                        found = True

                if found == False:  # lookup stops
                    self.logger.debug('FindValueCallback: Stopped')

                    # following are test code

                    self.logger.debug('i found '+str(len(thetask['shortlist'])))
##                    for c in thetask['shortlist']:
##                        print c['contact'].nodeid.val
##                    print thetask['rlist']

                    # end of test code

                    del self.task_list[taskseq]
                    thetask['defer'].callback({
                        'context': thetask['callback_context'],
                        'rlist': thetask['rlist'],
                        'shortlist': thetask['shortlist'],
                        'result': True,
                        'kw': thetask['kw'],
                        })
##            elif r['result'] == 'NoContact':
##
##                # if there is no contact in local buck_list
##                # send signal to wx app
##
##                self.logger.warning('FindValueCallback:No Contact')
##                return
            else:

                 # if there is no answer

                self.logger.warning('FindValueCallback:No Answer')
                thetask['shortlist'].remove(thec)
                self.buck_list.remove(thec['contact'].nodeid)
                thetask['onthefly'] -= 1
                if thetask['onthefly'] < 0:
                    thetask['onthefly'] = 0
                found = False
                for c in thetask['shortlist']:
                    if c['status'] == 'init':
                        found = True
                        if thetask['onthefly'] < self.alpha:
                            c['status'] = 'sent'
                            self.FindValue(c['contact'], thetask['kw'],
                                    thetask['rtype'],
                                    self.FindValueCallback,
                                    taskseq=taskseq)
                            thetask['onthefly'] += 1
                    elif c['status'] != 'answered' and c['status'] \
                        != 'answered-file':
                        found = True

                if found == False:  # lookup stops
                    del self.task_list[taskseq]
                    thetask['defer'].callback({
                        'context': thetask['callback_context'],
                        'rlist': thetask['rlist'],
                        'shortlist': thetask['shortlist'],
                        'result': False,
                        'kw': thetask['kw'],
                        })
            del self.req_list[r['seq']]
        except Exception, inst:

                                 # otherwise the exception won't get print out
            self.logger.error('FindValueCallback:'+traceback.format_exc())
            self.logger.error('FindValueCallback: catched exception: '
                         + str(inst))

    def FindValueReply(self):
        """Scan FindValueReplyQ periodically and send FindValue-Reply
        return up to k closet contacts or resource info.
        """

        newreqlist=[]

        for i in range(50):
            try:
                (kw, rtype, src_node, rseq,ctime) = self.FindValueReplyQ.get(False)
                newreqlist.append((kw, rtype, src_node, rseq,ctime))
            except Queue.Empty:
                break
        if len(newreqlist) == 0: return

        for (kw, rtype, src_node, rseq,ctime) in newreqlist:
            if time.time()-ctime>self.send_interval*self.max_resend:
                with self.FindValueReplyQ.mutex:
                    self.FindValueReplyQ.queue.clear()
                self.logger.debug("FindValueReply: FindValueReplyQ cleared")
                return #clear the queue and return

            attrs = ''
            rrlist = self.rlist.get_res_list(kw, rtype)
            if rrlist != False:  # if kw is found locally, return resource list
                for res in rrlist:
                    if res.type == rtype or rtype == 0:
                        self.logger.debug("FindValueReply: The owner is "+res.owner_id)
                        attrs += self.gen_res_attr(res.rid, res.owner_id, res.type,
                                res.data, res.rloc, res.meta_list)

            # always return k cloest contacks

            kw = kw.encode('utf-8')
            m = hashlib.sha1()
            m.update(kw)
            t_nodeid = longbin.LongBin(m.digest())
            c_list = self.buck_list.get_closest_list(t_nodeid)

            for c in c_list:
                attrs += self.gen_attr(4, str(c))

            (header, seq) = self.gen_header(7, self.knode.nodeid.val,
                    src_node.nodeid.val, rseq)
            packet = self.gen_packet(header, attrs)
            self.sendDatagram(src_node.v4addr, src_node.port, packet)

    def FindValue(
        self,
        dst_node,
        fkw,
        res_type,
        findvaluecallback,
        iseq=None,
        taskseq=None,
        ):
        """FindValue RPC, this is primitive operation, not an iterative one.
        dst_node is knode that being contacted
        fkw is a key word is being looked for
        rtype is the resource type
        res_type is resource type, int
        """

        (header, seq) = self.gen_header(6, self.knode.nodeid.val,
                dst_node.nodeid.val, iseq)
        attrs = ''
##        kw = AnyToUnicode(fkw)
##        kw = kw.encode('utf-8')
        kw = fkw
        attrs += self.gen_attr(1, kw)
        attrs += self.gen_attr(7, res_type)
        packet = self.gen_packet(header, attrs)

        if not seq in self.req_list:  # if this is a new request
            self.logger.debug('Initiate a new FindValue...')
            d = defer.Deferred()
            d.addErrback(self.ErrCallback)
            d.addCallback(findvaluecallback)  # you might want to change this
            self.sendDatagram(dst_node.v4addr, dst_node.port, packet)
            callid = reactor.callLater(
                self.send_interval,
                self.FindValue,
                dst_node,
                fkw,
                res_type,
                findvaluecallback,
                seq,
                )
            self.req_list[seq] = {
                'code': 6,
                'callid': callid,
                'defer': d,
                'send_time': 0,
                'dst_node': dst_node,
                'fkw': fkw,
                'taskseq': taskseq,
                }
            self.req_list[seq]['send_time'] += 1
            return
        else:
            if self.req_list[seq]['send_time'] > self.max_resend:

                # no respond, and max resend time reached

                self.logger.debug('stop sending FindValue,no answer from '+dst_node.v4addr+', calling callback'
                             )
                self.req_list[seq]['defer'].callback({'seq': seq,
                        'result': False, 'src_id': dst_node.nodeid.val})
            else:
                self.logger.debug('re-tran FindValue')
                self.sendDatagram(dst_node.v4addr, dst_node.port,
                                  packet)
                self.req_list[seq]['send_time'] += 1
                callid = reactor.callLater(
                    self.send_interval,
                    self.FindValue,
                    dst_node,
                    fkw,
                    res_type,
                    findvaluecallback,
                    seq,
                    )
                self.req_list[seq]['callid'] = callid

    def ValueLookup(
        self,
        fkw,
        rtype,
        callback_context=None,
        ):
        """
        the purpose of ValueLook is to find resource related to keyword
        This is iterative operation, NOT primitive(like FindValue)
        fkw is a keyword to search
        rtype is resource type
        """


        self.logger.debug('init a new ValueLookup')
        kw = AnyToUnicode(fkw)
        kw = kw.encode('utf-8')
        m = hashlib.sha1()
        m.update(kw)
        target_key = longbin.LongBin(m.digest())
        cshortlist = self.buck_list.get_closest_list(target_key,
                self.alpha)

        if len(cshortlist) == 0:

            # this is how you handle error in protocol, always use callback
            # to clean-up, do NOT use raise exception.

            #return self.FindValueCallback({'result': 'NoContact'})
            self.logger.warning('ValueLookup:No Contact')
            return None

        for c in cshortlist:  # cal the distance to the target
            c.distance = c.nodeid ^ target_key

        shortlist = []
        for c in cshortlist:
            shortlist.append({'contact': c, 'status': 'init'})

        # use first seq number as the key for this task?

        d = defer.Deferred()
        thetask = {
            'shortest': shortlist[0],
            'onthefly': self.alpha,
            'shortlist': shortlist,
            'defer': d,
            'target': target_key,
            'callback_context': callback_context,
            'rlist': [],
            'kw': fkw,
            'rtype': rtype,
            }
        task_seq = self.getSeq()
        self.task_list[task_seq] = thetask
        #print "valuelookup,len:",len(shortlist)
        for c in shortlist:
            c['status'] = 'sent'
            self.logger.debug("ValueLookup: Send FindValue to "+c['contact'].v4addr)
##            print "DDDD valuelookup ", type(fkw)
            self.FindValue(c['contact'], fkw, rtype,
                           self.FindValueCallback, taskseq=task_seq)
        return d  # return deferred, use addCallback() to add functions, this defered used to add different function for different purposes like publish,search ..etc.

    def Store(
        self,
        kw_list,
        res_list,
        dst_node,
        storecallback,
        iseq=None,
        ):
        """
        store keywork list on dst_node
        kw_list is a list of keyword,should be utf-8 encoded str
        res_list is a list of KADRes
        dst_node is KAD
        """


        self.logger.debug('Sending a Store request to ' + dst_node.v4addr)
        (header, seq) = self.gen_header(2, self.knode.nodeid.val,
                dst_node.nodeid.val, iseq)
        attrs = ''
        for kw in kw_list:
            attrs += self.gen_attr(1, kw)

        for res in res_list:
            if res.owner_id == 'SELF':
                owner_id = self.knode.nodeid.val
            else:
                owner_id = res.owner_id
            attrs += self.gen_res_attr(res.rid,owner_id, res.type,
                    res.data, res.rloc, res.meta_list)

        packet = self.gen_packet(header, attrs)

        if not seq in self.req_list:  # if this is a new request
            d = defer.Deferred()
            d.addCallback(storecallback)  # you might want to change this
            self.sendDatagram(dst_node.v4addr, dst_node.port, packet)
            callid = reactor.callLater(
                self.send_interval,
                self.Store,
                kw_list,
                res_list,
                dst_node,
                storecallback,
                seq,
                )
            self.req_list[seq] = {
                'code': 2,
                'callid': callid,
                'defer': d,
                'send_time': 0,
                'dst_node': dst_node,
                }
            self.req_list[seq]['send_time'] += 1
            return
        else:
            if self.req_list[seq]['send_time'] > self.max_resend:

                # no respond, and max resend time reached

                self.logger.debug('stop resending Store, calling callback...'
                             )
                self.req_list[seq]['defer'].callback({'seq': seq,
                        'result': False})  # change this,
            else:
                self.sendDatagram(dst_node.v4addr, dst_node.port,
                                  packet)
                self.logger.debug('re-tran Store...')
                self.req_list[seq]['send_time'] += 1
                callid = reactor.callLater(
                    self.send_interval,
                    self.Store,
                    kw_list,
                    res_list,
                    dst_node,
                    storecallback,
                    seq,
                    )
                self.req_list[seq]['callid'] = callid

    def StoreReply(self):
        """Scan StoreReplyQ periodically and send Store-Reply
        """

        newreqlist=[]

        for i in range(50):
            try:
                (kw_list, res_list, src_node, rseq) = self.StoreReplyQ.get(False)
                newreqlist.append((kw_list, res_list, src_node, rseq))
            except Queue.Empty:
                break
        if len(newreqlist) == 0: return


        # {'rid':20byte str,'rtype':int,'rdata':unicode,'rloc':unicode,'meta_list':dict of unicode}

        for (kw_list, res_list, src_node, rseq) in newreqlist:

            newlist = []
            for res in res_list:
                if u'//SELF/' in res['rloc'] or u'//SELF:' in res['rloc']:
                    rloc = res['rloc'].replace('SELF', src_node.v4addr, 1)
                else:
                    rloc = res['rloc']
                kres = KADRes(longbin.LongBin(res['rid']), res['rdata'], res['rtype'], rloc,
                              res['meta_list'],res['owner_id'])
                newlist.append(kres)

            for k in kw_list:
                self.rlist.add_res(k, newlist, src_node.nodeid.val)

            attrs = self.gen_attr(0, None)
            (header, seq) = self.gen_header(3, self.knode.nodeid.val,
                    src_node.nodeid.val, rseq)
            packet = self.gen_packet(header, attrs)
            self.sendDatagram(src_node.v4addr, src_node.port, packet)
            self.logger.debug('StoreReply: stored one')

    def StoreCallback(self, r):

        self.logger.debug('Entering storecallback')
        if r['seq'] in self.req_list:
            if r['result'] == False:  # if timeout
                self.logger.warning('store failed, dst_node no answer')
            elif r['result'] == True:
                self.logger.debug('store succeed')
        del self.req_list[r['seq']]

    def Publishcallback(self, r):

        self.logger.debug('Entering Publishcallback')
        shortlist = r['shortlist']
        context = r['context']
        if len(shortlist) == 0:  # no contacts has been found

            # send a signal to wx application here
            self.logger.warning('publishcallback: no contact in shortlist!')
            return False
        else:

            # res_list is a list of dict: {res_id: res_type,res_data,meta_list}
            # {'rid':20byte str,'rtype':int,'rdata':unicode,'rloc':unicode,'meta_list':dict of unicode}
            kres = context['res']
            for cc in shortlist:
                self.logger.debug('publishcallback: store ' + context['kw']
                             + ' to ' + cc['contact'].nodeid.val)
                self.Store([context['kw']], [kres], cc['contact'],
                           self.StoreCallback)
            self.rlist.setPubed(kres)

    def PublishRes(self,kw_list,res,check_pubed=False):
        """
        pulish function for all type of resource
        res is KADRes
        kw is a unicode
        check_pubed is a boolean to control if system should check the res is already published
        """
        if self.rlist.isPubed(res)==True and check_pubed==True:
            self.logger.debug('PublishRes:res already in local list')
            return

        self.logger.debug('PublishRes:start a new publish')
##        self.logger.debug('PublishRes:kw_list is '+str(kw_list))
##        print "kw_list is ",kw_list
        for kw in kw_list:
            self.logger.debug('PublishRes: Got- ' + kw.encode('utf-8'))
            self.rlist.add_res(kw,[res,],self.knode.nodeid.val)#add it into local rlist
            m = hashlib.sha1()
            kw = kw.encode('utf-8')
            m.update(kw)
            target = m.digest()
            target = longbin.LongBin(target)
            callback_context = {'res': res, 'kw': kw, 'rtype': 1}  # both are utf-8 encoded
            d = self.NodeLookup(target, callback_context)
            if d != None:
                d.addCallback(self.Publishcallback)


##    def Publish_kfile(self, kfile):
##        #
##        # don't use this method, it is outdated, use PublishRes instead
##        #
##        """
##        publish a new filename
##        kfile is KADFile
##        """
##
##
##        fname = os.path.splitext(kfile.name)[0]
##        fname = fname.encode('utf-8')
##        kw_list = mmseg.Algorithm(fname)
##        klist = []
##        for tok in kw_list:
##            klist.append(tok.text)
##        klist.append(fname)
##        url = u'http://SELF:' + unicode(self.listening_port) \
##                    + u'/' + kfile.name  # this could be other type of transportation like ftp
##
##        kres = KADRes(kfile.id,kfile.name,1,url,{'size':kfile.size},self.knode.nodeid.val)
##        newklist = []
##        for tok in klist:
##            kw = tok.decode('utf-8')
##            newklist.append(kw)
##            #self.rlist.add_res(kw,[kres,],self.knode.nodeid.val)#add it into local rlist
##
##        self.PublishRes(newklist,kres)


    def Searchcallback(self, r):
        """
        Searchcallback func
        """


        try:
            self.logger.debug('Entering Searchcallback')
            kw = r['kw']
            shortlist = r['shortlist']
            kw = AnyToUnicode(kw)
            rlist = r['rlist']
            context = r['context']
            if not context['search_task_seq'] in self.task_list:
                return
            thetask = self.task_list[context['search_task_seq']]
            for r in rlist:
                if not r in thetask['rlist']:
                    thetask['rlist'].append(r)

            # if the closest node did NOT return file, then we store kw on it.
            if len(shortlist)>0:
                if shortlist[0]['status'] != 'answered-file' and rlist != []:
                    krlist=[]
                    for r in thetask['rlist']:
                        krlist.append(KADRes(longbin.LongBin(r['rid']),r['rdata'],r['rtype'],r['rloc'],r['meta_list'],r['owner_id']))
                    self.Store([kw], krlist, shortlist[0]['contact'],
                               self.StoreCallback)
            thetask['todo_list'].remove(kw)
            if thetask['todo_list'] == []:  # search stops
                self.logger.debug('Searchcallback:Search Stops')
                # following is test code
                self.logger.debug("Searchcallback: following are the results:")
                for r in thetask['rlist']:
                    self.logger.debug(str(r))
                # end of test code
##                if thetask['cserver'] != None:
                try:
                    rrs=base64.b16encode(cPickle.dumps(thetask['rlist']))
                    #thetask['cserver'].report(thetask['rlist'])
                    thetask['cserver'].report(rrs)
                except Exception, inst:
                    self.logger.error('SearchCallback:'+traceback.format_exc())
                    self.logger.error('SearchCallback: catched exception: '
                                 + str(inst))
                del self.task_list[context['search_task_seq']]
        except Exception, inst:
            # otherwise the exception won't get print out
            self.logger.error('searchCallback:'+traceback.format_exc())
            self.logger.error('SearchCallback: catched exception: '
                         + str(inst))
##            print Exception.message

        if len(rlist) == 0:  # no contacts has been found

            # send a signal to wx application here

            self.logger.warning('Searchcallback: no resource found')
            try:
                thetask['cserver'].report(base64.b16encode(cPickle.dumps([])))
            except Exception, inst:
                self.logger.error('SearchCallback:'+traceback.format_exc())
                self.logger.error('SearchCallback: catched exception: '
                             + str(inst))
            return False

    def MaintainContactList(self):
        """
        go through all buckets, for 1st buckets that have NOT been lookup
        tRefresh time, do a NodeLookup with a random key in the bucket range.
        """
        nid_prefix = self.buck_list.get1stIB()
        if nid_prefix == None:
            self.logger.debug("MaintainContactList: No Idle bucket found")
            return
        self.logger.debug("MaintainContactList: nid_prefix is "+nid_prefix)
        nlen = len(nid_prefix)
        while nlen < 160:
            nid_prefix+=random.choice(['0','1'])
            nlen+=1
        target_key = self.knode.nodeid ^ longbin.LongBin(binstr=nid_prefix)
        self.logger.debug("MaintainContactList:looking for "+str(target_key))
        self.NodeLookup(target_key)


    def MaintainRes(self):
        """
        Maintain resource list:
            - remove expired res
        """
        self.logger.debug('MaintainRes: cleaning expired res')
        self.rlist.remove_expired_res()


    def Search(self, kw_list, rtype, cserver=None):
        """search a list of keywords with a resource type
        kw_list is list of keyword to be searched, must be unicode
        rtype is the resource type to be searched
        cserver is the url of xmlrpc callbacksvr to report search results ,a
            non-None value will override self.cserver
        """



        if kw_list == None or len(kw_list)==0: return
        for k in kw_list:
            if not isinstance(k,unicode):
##                print "Search:"+k+" is not unicode"
                self.logger.warning("Search:"+k+" is not unicode")
                return
            #fkw_list.append(AnyToUnicode(k))
        cxmlsvr = None
        if cserver != None:
            try:
                cxmlsvr = xmlrpclib.Server(cserver)
            except:
                cxmlsvr = None
        else:
            cxmlsvr = self.cserver

        thetask = {'kw_list': kw_list, 'todo_list': kw_list,
                   'rlist': [],'cserver':cxmlsvr}
        task_seq = self.getSeq()
        self.task_list[task_seq] = thetask
        callback_context = {'search_task_seq': task_seq}
        for kw in kw_list:
            d = self.ValueLookup(kw, rtype, callback_context)
            if d != None:
                d.addCallback(self.Searchcallback)
            else:
                cxmlsvr.report(base64.b16encode(cPickle.dumps('NoContact')))


    def PingCallback(self, r):

        self.logger.debug('Entering pingcallback')
        if r['seq'] in self.task_list:
            if self.task_list[r['seq']]['task'] == 0:
                if r['result'] == False:  # if timeout
                    self.logger.debug('adding new contact')
                    obj = self.task_list[r['seq']]['object']
                    obj['bucket'].__delitem__(0)
                    obj['bucket'].append(obj['node'])
                    obj['bucket'].sort(key=attrgetter('distance'))
                    self.numofcontact += 1
                elif r['result'] == True:
                    self.logger.debug('New Contact Ignored')
                    pass  # ignore the new contact
            del self.task_list[r['seq']]
        del self.req_list[r['seq']]

    def PingReply(self, dst_node, iseq):

        self.logger.debug('sending ping-reply')
        (header, seq) = self.gen_header(1, self.knode.nodeid.val,
                dst_node.nodeid.val, iseq)
        packet = self.gen_packet(header)
        self.sendDatagram(dst_node.v4addr, dst_node.port, packet)

    def Ping(
        self,
        dst_node,
        pingcallback,
        iseq=None,
        ):

        self.logger.debug('Entering Ping')
        (header, seq) = self.gen_header(0, self.knode.nodeid.val,
                dst_node.nodeid.val, iseq)
        packet = self.gen_packet(header)
        if not seq in self.req_list:  # if this is a new request
            d = defer.Deferred()
            d.addCallback(pingcallback)  # you might want to change this
            self.sendDatagram(dst_node.v4addr, dst_node.port, packet)
            callid = reactor.callLater(self.send_interval, self.Ping,
                    dst_node, pingcallback, seq)
            self.req_list[seq] = {
                'code': 0,
                'callid': callid,
                'defer': d,
                'send_time': 0,
                'dst_node': dst_node,
                }
            self.req_list[seq]['send_time'] += 1
            return
        else:
            if self.req_list[seq]['send_time'] > self.max_resend:

                # no respond, and max resend time reached

                self.logger.debug('stop resending ping, calling callback...'
                             )
                self.req_list[seq]['defer'].callback({'seq': seq,
                        'result': False})  # change this,
            else:
                self.sendDatagram(dst_node.v4addr, dst_node.port,
                                  packet)
                self.logger.debug('re-tran ping...')
                self.req_list[seq]['send_time'] += 1
                callid = reactor.callLater(self.send_interval,
                        self.Ping, dst_node, pingcallback, seq)
                self.req_list[seq]['callid'] = callid

    def Boot(
        self,
        dst_ip,
        bootcallback,
        iseq=None,
        dst_port=KPORT,
        ):
        """Bootstrapping request, used to request 20 contacts from dst_ip
        """


        self.logger.debug('Bootstrapping...')
        (header, seq) = self.gen_header(9, self.knode.nodeid.val,
                '00000000000000000000', iseq)
        packet = self.gen_packet(header)
        if not seq in self.req_list:  # if this is a new request
            d = defer.Deferred()
            d.addCallback(bootcallback)  # you might want to change this
            self.sendDatagram(dst_ip, dst_port, packet)
            callid = reactor.callLater(
                self.send_interval,
                self.Boot,
                dst_ip,
                bootcallback,
                seq,
                dst_port,
                )
            self.req_list[seq] = {
                'code': 9,
                'callid': callid,
                'defer': d,
                'send_time': 0,
                'dst_ip': dst_ip,
                }
            self.req_list[seq]['send_time'] += 1
            return
        else:
            if self.req_list[seq]['send_time'] > self.max_resend:

                # no respond, and max resend time reached

                self.logger.debug('stop resending boot, calling callback...'
                             )
                self.req_list[seq]['defer'].callback({'seq': seq,
                        'result': False})  # change this,
            else:
                self.sendDatagram(dst_ip, dst_port, packet)
                self.logger.debug('re-tran boot...')
                self.req_list[seq]['send_time'] += 1
                callid = reactor.callLater(
                    self.send_interval,
                    self.Boot,
                    dst_ip,
                    bootcallback,
                    seq,
                    dst_port,
                    )
                self.req_list[seq]['callid'] = callid

    def BootReply(self):
        """Bootstrapping reply, return 20 contacts
        """
        newreqlist=[]
        for i in range(50):
            try:
                (src_node, rseq, ctime) = self.BootReplyQ.get(False)
                newreqlist.append((src_node, rseq, ctime))
            except Queue.Empty:
                break
        if len(newreqlist) == 0: return

        for (src_node, rseq, ctime) in newreqlist:
            if time.time()-ctime>self.send_interval*self.max_resend:
                with self.BootReplyQ.mutex:
                    self.BootReplyQ.queue.clear()
                self.logger.debug("BootRely: BootReplyQ cleared ")
                return #clear the queue and return

            c_list = []
            self.buck_list.get_list(c_list, self.k)
            c_list = c_list[:self.k]
            attrs = ''
            for c in c_list:
                attrs += self.gen_attr(4, str(c))
            (header, seq) = self.gen_header(10, self.knode.nodeid.val,
                    src_node.nodeid.val, rseq)
            packet = self.gen_packet(header, attrs)
            self.sendDatagram(src_node.v4addr, src_node.port, packet)

    def BootCallback(self, r):

        del self.req_list[r['seq']]
        if self.buck_list.count >= self.max_bootscan_answers:
            try:
                self.logger.debug('bootscan stopped')
                self.rptlist['BootScan'].stop()  # stop the bootscan task
            except:
                pass
        else:
            if r['result'] == True:  # if got the reply to Boot
                self.logger.debug('BootCallback:Got the answer')
                if not 4 in r['attr_list']:
                    return
                host_alist = r['attr_list'][4]
                for h in host_alist:
                    newnode = KADNode(h['nodeid'], h['ipv4'], h['port'])
                    self.updateContactQ.put(newnode)
            else:
                 # if there is no answer
                self.logger.warning('BootCallback:No Answer')

    def getSeq(self):
        if self.packet_seq == 4294967295:
            self.packet_seq = 0
        else:
            self.packet_seq += 1
        return self.packet_seq

    def getConfigDir(self):
        """
        return the directory of configuration files resides in.
        """
        global MYOS
        if self.conf_dir == None:
            if MYOS == 'Windows':
                return os.environ['APPDATA']
            elif MYOS == 'Linux' or MYOS == 'Darwin':
                cdir = os.environ['HOME']+'/.kadp/'

            else:
                return False
        else:
            cdir = self.conf_dir

        if not os.path.isdir(cdir):
            os.mkdir(cdir,0755)
        self.conf_dir = cdir
        return cdir



##    def saveConfig(self):
##        """
##        Save configuration
##        """
##        config = MyConfig()
##        config.add_section('settings')
##        config.set('settings','nodeid',str(self.knode.nodeid))
##        config.set('settings','lport',str(self.listening_port))
##        try:
##            config_file = open(self.getConfigDir()+os.sep+"kadp.ini","w")
##            config.write(config_file)
##            config_file.close()
##            return True
##        except:
##            return False
##
##    def loadConfig(self):
##        """
##        Load configuration
##        """
##        config = MyConfig()
##        try:
##            fp = open(self.getConfigDir()+os.sep+"kadp.ini","r")
##            config.readfp(fp)
##            nodeid = longbin.LongBin(binstr=config.get('settings','nodeid'))
##            self.listening_port = config.getint('settings','lport')
##            self.knode = KADNode(nodeid,
##                                     socket.gethostbyname(socket.gethostname()),
##                                     self.listening_port)
##            return True
##        except:
##            return False







    def updateContactList(self, newc=None):
        """
        if newc==None then get newknode from Q
        """

        newclist=[]
        if newc == None:
            for i in range(50):
                try:
                    newknode = self.updateContactQ.get(False)
                    newclist.append(newknode)
                except Queue.Empty:
                    break
        else:
            newclist.append(newc)
        if len(newclist) == 0: return
        for c in newclist:
            self.buck_list.insert(c)


    def prefix2mask(self, prefix):
        i = 2 ** prefix - 1
        rs = struct.pack('I', i)
        (c1, c2, c3, c4) = struct.unpack('cccc', rs)
        rs = ''
        for c in (c1, c2, c3, c4):
            rs += str(ord(c)) + '.'
        return rs[:-1]


    def testcode(self):  # this is test function, should be removed
        """This is used to test Nodelookup function"""

        kw = u'上海'
        kw = kw.encode('utf-8')
        m = hashlib.sha1()
        m.update(kw)
        target = longbin.LongBin(m.digest())
        self.NodeLookup(target)

    def test4(self):  # this is a test function, should be removed
        """This is used to test valueLookup"""

        self.Search([u'上海'], 1)

##    def test_pub(self):  # this is test function, should be removed
##        """This is used to test publish function"""
##
##        testf = KADFile(u'上海五角场风云录.txt', 15000, '99999999999999999999')
##        self.Publish_kfile(testf)

    def test2(self):  # this is a test function, should be removed
        """This is used to test store function"""

        finfo = KADFile(u'中国北京.txt', 1500)
        ff = False
        for b in self.buck_list:
            for node in b:
                dstn = node
                ff = True
                break
            if ff == True:
                break
        kw_list = []
        kw_list.append(u'中国'.encode('utf-8'))
        kw_list.append(u'北京'.encode('utf-8'))
        self.Store(kw_list, finfo, dstn, self.StoreCallback)

    def setLPort(self,lport):
        """
        Set the IListeningPort, used to stop listening
        """
        self.ilport=lport

    def startProtocol(self):

        self.transport.socket.setsockopt(socket.SOL_SOCKET,
                socket.SO_REUSEADDR, 1)
        self.transport.socket.setsockopt(socket.SOL_SOCKET,
                socket.SO_BROADCAST, 1)

        # don't use while loop, use task.LoopingCall, otherwise ctrl+c won't work

        rpt_list = {}
        rpt1 = task.LoopingCall(self.updateContactList)
        rpt1.start(1.0)
        rpt_list['updateContactList'] = rpt1
        rpt2 = task.LoopingCall(self.FindNodeReply)
        rpt2.start(1.0)
        rpt_list['FindNodeReply'] = rpt2
        rpt3 = task.LoopingCall(self.BootReply)
        rpt3.start(0.8)
        rpt_list['BootReply'] = rpt3
        if self.force_scan == True:
            rpt4 = task.LoopingCall(self.BootScan)
            rpt4.start(0.02)
            rpt_list['BootScan'] = rpt4
        rpt5 = task.LoopingCall(self.StoreReply)
        rpt5.start(1.0)
        rpt_list['StoreReply'] = rpt5
        rpt6 = task.LoopingCall(self.FindValueReply)
        rpt6.start(1.0)
        rpt_list['FindValueReply'] = rpt6
        rpt7 = task.LoopingCall(self.MaintainRes)
        rpt7.start(self.tClearResInterval)
        rpt_list['MaintainRes'] = rpt7


        rpt8 = task.LoopingCall(self.rlist.replicate)
        rpt8.start(self.tReplicate)
        rpt_list['ReplicateRes'] = rpt8

        rpt9 = task.LoopingCall(self.rlist.republish)
        rpt9.start(self.tRepublish)
        rpt_list['RepublishRes'] = rpt9

        rpt10 = task.LoopingCall(self.MaintainContactList)
        rpt10.start(300)
        rpt_list['MaintainContactList'] = rpt10


        if self.force_scan == False:
            if self.buck_list.loadContact() == True:
                self.logger.debug('startProtocol: contact loaded sucessfully, \
                            No bootscan')
                #self.rptlist['BootScan'].stop()
                self.NodeLookup(self.knode.nodeid) #broadcast self, should enable this in production code
            else:
                self.logger.warning('startProtocol: load contact failed.')
                if self.BootStrap() == False:
                    self.logger.warning("startProtocol: can not bootstrap, will\
                                        try agin later")
                    rpt11 = task.LoopingCall(self.BootStrap)
                    rpt11.start(300)
                    rpt_list['BootStrap'] = rpt11

        self.setTaskList(rpt_list)
        #self.checkPort()




        # starting test code, should be removed in production
##        if self.dstnode != None:
##            self.Boot(self.dstnode.v4addr, self.BootCallback)
        # end of test code

    def prepareStop(self):
        self.logger.debug("preparing stop")
##        self.saveConfig()
        self.buck_list.saveContact()
        self.rlist.saveRes()
        self.ilport.stopListening()


    def stopAll(self):
        #self.prepareStop()
        reactor.stop()



    def stopProtocol(self):
        self.prepareStop()
        self.logger.debug("KADP STOPPED.")

    def answerPortOpen(self,nonce=99):
        """
        this function is called while receving code=11 packet
        """
        if self.port_open_status==0:
            if self.port_open_nonce==nonce:
                self.port_open_status=1
                self.logger.debug("answerPortOpen:Port is open!")
                self.checkportopen_call.cancel()
            else:
                self.port_open_status=-1
                self.logger.error("answerPortOpen:Port is NOT open!")


    def checkPort(self):
        """
        check if the listening port is open
        """
        self.logger.debug("checkPort: i am in")
        if self.port_open_status == 0:
            return
        self.port_open_status = 'INIT'
        reactor.callLater(10,self.checkPortOpen)
        self.checkportopen_call = reactor.callLater(
                20,
                self.answerPortOpen,
                99
                )

    def checkPortOpen(self):
        """
        supporting function for checkPort, checkPort() should be used
        """
        if self.port_open_status == 0:
            return
        self.logger.debug("checkPortOpen:start checking port")
        nonce=os.urandom(8)
        cnode = {'nid':self.knode.nodeid.val,'port':self.listening_port,
                    'nonce':nonce
                }
        encodes = urllib.urlencode(cnode)
        full_url = self.chkport_url + encodes
        try:
            clistf = urllib.urlopen(full_url)
        except Exception, inst:
            self.logger.error("checkPortOpen: Error opening check URL!")
            return False

        self.port_open_nonce=nonce
        self.port_open_status=0
        self.logger.debug("checkPortOpen:port check request submited")


    def BootStrap(self):
        """
        Get some contact from bootstrap server
        """
        cnode = {'nid':self.knode.nodeid.val,'port':self.listening_port}
        encodes = urllib.urlencode(cnode)
        full_url = self.bstrap_url + encodes
        try:
            clistf = urllib.urlopen(full_url)
        except Exception, inst:
            self.logger.error("BootStrap: Error opening bootstrap URL!")
            return False
        found = False
        if clistf.getcode() != 200:
            self.logger.error("BootStrap: not a 200 answer")
            return False
        self.logger.debug("BootStrap: got following from bootstrap server:\n")
        for cls in clistf:
            self.logger.debug(cls)
            cdict = urlparse.parse_qs(cls,strict_parsing=True)
            knode = KADNode(longbin.LongBin(cdict['nid'][0]),cdict['addr'][0].strip(),int(cdict['port'][0].strip()))
            self.buck_list.insert(knode)
            #print "adding ", cdict['nid'][0].strip()
            found = True
        if found==True and self.rptlist != None and 'BootStrap' in self.rptlist:
            self.rptlist['BootStrap'].stop()
        return found

    def BootScan(self):
        if self.addrlist != []:
            if self.current_ai >= len(self.addrlist):
                return
            caddr = self.addrlist[self.current_ai]
            if self.current_ii > int(caddr[1]):
                self.current_ii = 0
                self.current_ai += 1
            sipi = struct.unpack('>L', socket.inet_aton(caddr[0]))[0]
            tipi = sipi + self.current_ii
            ips = socket.inet_ntoa(struct.pack('>L', tipi))
            lastn = ips.split('.')[3]

            # if self.current_ii % 10000==0: print self.current_ii

            if lastn != '0' and lastn != '255':
                if ips != self.bip:
                    self.Boot(ips, self.BootCallback)

            self.current_ii += 1

    def sendDatagram(
        self,
        v4addr,
        udpport,
        packet,
        ):
        """
        send a packet directly
        """


        self.logger.debug('sending a packet.')
        try:
            self.transport.write(packet, (v4addr, udpport))
        except Exception, inst:
            self.logger.error('sendDatagram:'+traceback.format_exc())
            self.logger.error('sendDatagram: send failed. ' + str(inst))
            return

    def datagramReceived(self, datagram, host):
        """ Executed when a UDP packet is received:
            - datagram: received udp payload; str
            - host: remote host is a tuple of (addr,port); tupple
        """



        self.logger.debug('Received a packet.')

##        if host[0] in self.IPList.keys(): #drop packet sent from self
##            return

        rr = self.parse_packet(datagram)
        if rr == False:
            return
        else:
            (pheader, alist) = rr
        src_node = KADNode(longbin.LongBin(pheader['src_id']), host[0],
                           host[1])#the src-port in the IP header is used iso listening port in the KADP header
        if pheader['code'] != 11:
            self.updateContactQ.put(src_node)  # put dst_node into queue
        if pheader['code'] == 0:  # if it is ping-request
            self.PingReply(src_node, pheader['seq'])
            return
        if pheader['code'] == 1:  # if it is ping-reply
            rseq = pheader['seq']
            if rseq in self.req_list:
                self.req_list[rseq]['callid'].cancel()
                self.req_list[rseq]['defer'].callback({'seq': rseq,
                        'result': True})
            else:
                self.logger.error('unknown seq, dropped')
            return
        if pheader['code'] == 6:  # if it is FindValue-Request
            if 1 in alist and 7 in alist:
                self.FindValueReplyQ.put([alist[1][0], alist[7],
                        src_node, pheader['seq'], time.time()])  # only use 1st keyword attr
            return
        if pheader['code'] == 7:  # if it is FindValue-Reply
            rseq = pheader['seq']
            if rseq in self.req_list:
                try:
                    self.req_list[rseq]['callid'].cancel()
                    if 6 in alist:
                        for r in alist[6]:
                            if u'//SELF/' in r['rloc'] or u'//SELF:' in r['rloc']:
                                r['rloc'] = r['rloc'].replace('SELF', src_node.v4addr, 1)
                    self.req_list[rseq]['defer'].callback({
                        'seq': rseq,
                        'result': True,
                        'attr_list': alist,
                        'src_id': pheader['src_id'],
                        })
                except Exception, inst:
                    self.logger.error('datagramReceived:'+traceback.format_exc())
                    self.logger.error(str(inst))
            return

        if pheader['code'] == 4:  # if it is FindNode-Request
            #print "get FindNodeRequest from ",src_node.nodeid.val," seq ",pheader['seq']
            if 3 in alist:
                t_node = longbin.LongBin(alist[3][0])
                self.FindNodeReplyQ.put([t_node, src_node, pheader['seq'
                        ],time.time()])
            return
        if pheader['code'] == 5:  # if it is FindNode-Reply
            rseq = pheader['seq']
            if rseq in self.req_list:
                try:
                    self.req_list[rseq]['callid'].cancel()
                    self.req_list[rseq]['defer'].callback({
                        'seq': rseq,
                        'result': True,
                        'attr_list': alist,
                        'src_id': pheader['src_id'],
                        })
                except Exception, inst:
                    self.logger.error('datagramReceived:'+traceback.format_exc())
                    self.logger.error(str(inst))
            return
        if pheader['code'] == 2:  # if it is store
            if 1 in alist and 6 in alist:
                self.StoreReplyQ.put([alist[1], alist[6], src_node,
                        pheader['seq']])
            return

        if pheader['code'] == 3:  # if it is Store-Reply
            rseq = pheader['seq']
            if rseq in self.req_list:
                try:
                    self.req_list[rseq]['callid'].cancel()
                    self.req_list[rseq]['defer'].callback({
                        'seq': rseq,
                        'result': True,
                        'attr_list': alist,
                        'src_id': pheader['src_id'],
                        })
                except Exception, inst:
                    self.logger.error('datagramReceived:'+traceback.format_exc())
                    self.logger.error(str(inst))
            return

        if pheader['code'] == 9:  # if it is Boot
            self.BootReplyQ.put([src_node, pheader['seq'], time.time()])
            return
        if pheader['code'] == 11:  # if it is check_port_open
            self.answerPortOpen(alist[8][0])
            return
        if pheader['code'] == 10:  # if it is Boot-reply
            rseq = pheader['seq']
            if rseq in self.req_list:
                try:
                    self.req_list[rseq]['callid'].cancel()
                    self.req_list[rseq]['defer'].callback({'seq': rseq,
                            'result': True, 'attr_list': alist})
                except Exception, inst:
                    self.logger.error('datagramReceived:'+traceback.format_exc())
                    self.logger.error(str(inst))
        else:
            self.logger.error('datagramReceived:'+traceback.format_exc())
            self.logger.info('unknown seq, dropped')

    def gen_header(
        self,
        code,
        src_id,
        dst_id,
        seq_num=None,
        ):
        """ Generate KAD protocol header:
        - code: message type; unsigned int
        - src_id/dst_id: Node_ID(str) of src and dest
        - payload_len: length of payload, unsigned int
        return (header,seq)
        """


        ver = chr(1)  # protocol version is 1
        if not code in self.msg_code_list:
            self.logger.warning('gen_header:Invalid Code')
            return False
        mcode = chr(code)  # msg type
        flag = chr(0)  # request
        resvr = chr(0)
        if seq_num == None:
            if self.packet_seq == 4294967295:
                self.packet_seq = 0
            else:
                self.packet_seq += 1
            fseq = int(self.packet_seq)
        else:
            fseq = int(seq_num)
        fseqs = struct.pack('I', fseq)

        # print type(ver),type(mcode),type(flag),type(src_id),type(dst_id),type(fseqs)

        lps = struct.pack('H', self.listening_port)
        rheader = ver + mcode + flag + src_id + dst_id + lps + fseqs
        return (rheader, fseq)

    def gen_attr(self, atype, aval):
        """ Generate a KADP attribute:
            - atype: attribute type; int
            - aval: attribute value; str or unicode
        note: aval will be encoded as UTF-8 when atype==0
        note2: struct.pack/unpack can NOT be used to pack/unpack complex combo,otherwise, unexpected '\x00' will be padded
        """

        if aval != None:
            if atype == 1:  # if attr is keyword
##                print "aval is", aval
                if isinstance(aval, str):
                    encoding = chardet.detect(aval)['encoding']
                    try:
                        aval = aval.decode(encoding)
                    except:
                        aval = aval.decode('utf-8')
                if isinstance(aval, unicode):
                    aval = aval.encode('utf-8')
            if atype == 7:
                fmts = 'HHH'
                return struct.pack(fmts, atype, 2, aval)

            alen = len(aval)
            if atype == 0:  # if attr is result
                fmt_str = 'HHc'
                alen = 1
                aval = int(aval)
                rattr = struct.pack(fmt_str, atype, alen, aval)
            else:
                fmt_str = 'HH' + str(alen) + 's'
                rattr = struct.pack(fmt_str, atype, alen, aval)
        else:
            fms = 'HH'
            rattr = struct.pack(fms, atype, 0)
        return rattr

    def gen_res_attr(
        self,
        res_id,
        owner_id,
        res_type,
        res_data,
        res_loc,
        meta_list,
        ):
        """
        Generate a KAD general resource attr
        res_id is a 20 bytes string
        owner_id is the owner's NodeID,20bytes string
        res_type is a int, 1 means file_url is currently supported
        res_data is a unicode or a utf-8 string
        res_local is a unicode or a utf-8 string
        meta_list is a dict, all string in this dict must be unicode
        """
        if owner_id == 'SELF':
            oid = self.knode.nodeid.val
        else:
            oid = owner_id
        supported_types = [1]
        if len(oid) != 20:
            raise ValueError('owner_id must be 20 bytes str.')
        if not res_type in supported_types:
            raise ValueError('unsupported res_type')
        attr_val = ''
        types = struct.pack('H', res_type)
        attr_val += res_id.val + oid + types

        if isinstance(res_data, unicode):
            res_data = res_data.encode('utf-8')
        datalen = len(res_data)
        datalens = struct.pack('H', datalen)
        attr_val += datalens + res_data

        if isinstance(res_loc, unicode):
            res_loc = res_loc.encode('utf-8')
        loclen = len(res_loc)
        loclens = struct.pack('H', loclen)
        attr_val += loclens + res_loc

        newmlist = {}
        for (k, v) in meta_list.items():  # encode all unicode into utf-8
            newk=k
            newv=v
            if isinstance(k, unicode):
                newk = urllib.quote_plus(k.encode('utf-8'))
            if isinstance(v, unicode):
                newv = urllib.quote_plus(v.encode('utf-8'))
            newmlist[newk] = newv
##        if len(newmlist.keys())>1:
##            print newmlist
        metas = urllib.urlencode(newmlist)
        attr_val += metas
        return self.gen_attr(6, attr_val)

    def gen_packet(self, header, payload=''):
        m = hashlib.sha1()
        m.update(header + payload)
        checksum = m.digest()
        return header + payload + checksum[:10]

    def parse_packet(self, ipacket):
        """ Parse input packet, return:
            - a dict store header info
            - a dict store attributes
        """


        plen = len(ipacket)
        if plen < 59:
            self.logger.warning('Invalid packet size,packet dropped')
            return False
        if ord(ipacket[0]) != 1:
            self.logger.warning('Unsupported version,packet dropped')
            return False
        m = hashlib.sha1()
        m.update(ipacket[:-10])
        if m.digest()[:10] != ipacket[-10:]:
            self.logger.warning('Invalid checksum,packet dropped')
            return False
        header = {}
        header['ver'] = ord(ipacket[0])
        header['code'] = ord(ipacket[1])
        header['flag'] = ord(ipacket[2])
        header['src_id'] = ipacket[3:23]
        header['dst_id'] = ipacket[23:43]
        header['listen_port'] = struct.unpack('H', ipacket[43:45])[0]#this could be used to detect the NAT within src node
        if header['dst_id'] != self.knode.nodeid.val and header['dst_id'
                ] != '00000000000000000000':  # if dst_id <> self.id
            self.logger.warning('Invalid dst_id, packet dropped')
            return False
        header['seq'] = struct.unpack('I', ipacket[45:49])[0]
        attr_list = {}
        ats = ipacket[49:-10]
        if ats != '':
            attr_list = self.parse_attrs(ats)
        return (header, attr_list)

    def parse_attrs(self, attrs):
        """ Parse recived attributes, return a dict,
            - key is attribute type
            - The value depends on attr type like following:
                - 0: a bool
                - 1 or 2: a list of unicode(by using utf-8 decode)
                - 3: a binary str
                - 4: a list of {'ipv4':str,'port':int,'nodeid':longbin}
                - 5: a dict of {'fname':unicode,'size':int}
                - 6: depends on res_type, for type 1, a list of dict of
                                {'rid':20byte str,'owner_id':20bytes str,
                                'rtype':int,'rdata':unicode,'rloc':unicode,
                                'meta_list':dict of unicode}
                - 7: int

        """
        attr_list = {}
        try:
            while attrs != '':
                fmts = 'HH'
                (atype, alen) = struct.unpack(fmts, attrs[:4])
                fmts = 'HH' + str(alen) + 's'
                (atype, alen, aval) = struct.unpack(fmts, attrs[:4
                        + alen])
                etc = True
                if atype == 1 or atype == 2:  # if attr is keyword or url
                    aval = aval.decode('utf-8')
                    if not atype in attr_list:

                    # attr_list[atype]=[[atype,alen,aval[:alen]]]

                        attr_list[atype] = [aval]
                    else:
                        attr_list[atype].append(aval)
                    etc = False

                if atype == 0:  # if attr is result

                    # attr_list[atype]=[[atype,alen,bool(aval[:alen])]]

                    attr_list[atype] = bool(aval)
                    etc = False

                if atype == 4:  # if attr is v4host_info
                    fmts = '4sH20s'
                    (ipbs, udpport, nodeidval) = struct.unpack(fmts,
                            aval)
                    ipv4addr = ''
                    for c in ipbs:
                        ipv4addr += str(ord(c)) + '.'
                    ipv4addr = ipv4addr[:-1]
                    contact = {'ipv4': ipv4addr, 'port': udpport,
                               'nodeid': longbin.LongBin(nodeidval)}

                    if not atype in attr_list:

                        # attr_list[atype]=[[atype,alen,aval[:alen]]]

                        attr_list[atype] = [contact]
                    else:
                        attr_list[atype].append(contact)
                    etc = False

                if atype == 5:  # if attr is fileinfo
                    aval = aval.decode('utf-8')
                    aalist = aval.split('>')
                    attr_list[atype] = {'fname': aalist[0],
                            'size': int(aalist[1])}
                    etc = False

                if atype == 6:  # if attr is general resource
                    rid = aval[:20]
                    owner_id = aval[20:40]
                    rtype = struct.unpack('H', aval[40:42])[0]

                    # varstr=aval[22:]

                    rdatalen = struct.unpack('H', aval[42:44])[0]
                    rdata = aval[44:44 + rdatalen]
                    rloclen = struct.unpack('H', aval[44 + rdatalen:46
                            + rdatalen])[0]
                    rloc = aval[46 + rdatalen:46 + rdatalen + rloclen]
                    rmetas = aval[46 + rdatalen + rloclen:]
                    if rtype == 1:
                        rdata = rdata.decode('utf-8')
                        rloc = rloc.decode('utf-8')
                        metas_list = rmetas.split('&')
                        mlist = {}
                        for meta in metas_list:
                            (k, v) = meta.split('=')
                            k = urllib.unquote_plus(k).decode('utf-8')
                            v = urllib.unquote_plus(v).decode('utf-8')
                            mlist[k] = v
                        if not atype in attr_list:
                            attr_list[atype] = [{
                                'rid': rid,
                                'owner_id' : owner_id,
                                'rtype': rtype,
                                'rdata': rdata,
                                'rloc': rloc,
                                'meta_list': mlist,
                                }]
                        else:
                            attr_list[atype].append({
                                'rid': rid,
                                'owner_id' : owner_id,
                                'rtype': rtype,
                                'rdata': rdata,
                                'rloc': rloc,
                                'meta_list': mlist,
                                })
                    etc = False

                if atype == 7:  # if attr is resource type
                    attr_list[atype] = struct.unpack('H', aval)[0]
                    etc = False

                if etc == True:
                    if not atype in attr_list:
                        # attr_list[atype]=[[atype,alen,aval[:alen]]]
                        attr_list[atype] = [aval[:alen]]
                    else:
                        attr_list[atype].append(aval[:alen])
                attrs = attrs[4 + alen:]
        except Exception, inst:

                                 # otherwise the exception won't get print out

            self.logger.error('parse_attrs:'+traceback.format_exc())
            self.logger.error('parse_attrs: catched exception: '
                         + str(inst))
        return attr_list

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    print recved data
    """

    def handle(self):
        data = self.request[0]
        rec = logging.makeLogRecord(cPickle.loads(data[4:]))
        #socket = self.request[1]
        #print "{} wrote:".format(self.client_address[0])
        print "\n"+rec.asctime+" - "+rec.name+" - "+rec.levelname+" : "+rec.getMessage()

class ThreadingUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass

class tXMLSvr(XMLRPC):

    def __init__(self, proto):
        XMLRPC.__init__(self)
        self.proto = proto
        self.log_list = []

    def addlog(self, cip):
        if not cip in self.log_list:
            lh = DatagramHandler(cip, 9999)
            lh.setLevel(logging.DEBUG)
            formatter = \
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                                  )
            lh.setFormatter(formatter)
            self.proto.logger.addHandler(lh)
            self.log_list.append(cip)
##        rid,
##        data,
##        rtype=1,
##        rloc=None,
##        metadata={},
##        owner_id='SELF',
##        ctime=None
    def xmlrpc_publishRes(self,kw_list,rid_val,res_data,res_rtype,res_rloc,res_metadata,res_owner):
        #{'rloc': 'http://1.1.1.1/', 'meta_list': {'size': 9999}, 'type': 1, 'creation_time': 1343344275.1678779, 'rid': {'val': '10101011010000000000', 'nlen': 20}, 'data': u'\u8fd9\u662f\u4e00\u4e2a\u6d4b\u8bd5\u95ee\u955c', 'owner_id': '10101011019999999999'}
        ridv=base64.b16decode(rid_val)
        rid = longbin.LongBin(ridv)
        newklist=[]
        for k in kw_list:
            k = k.strip()
            if k !='':
                if not isinstance(k,unicode):
                    newklist.append(k.decode('utf-8'))
                else:
                    newklist.append(k)
##        print "newklist is",newklist
        if newklist != []:
            kkres = KADRes(rid,res_data,res_rtype,res_rloc,res_metadata,res_owner)
            self.proto.PublishRes(newklist,kkres,True)
        return 'ok'


    @withRequest
    def xmlrpc_report(self, request, attrs):
        """attrs is a string represent attr name, could be a func"""



        # following code is test code, use to add syslog handler to XML_RPC client
        # should be removed from production.

        cip = request.getClientIP()
        self.addlog(cip)

        # end of test code

        try:
            return base64.b16encode(cPickle.dumps(getattr(self.proto,
                                    attrs), 2))
        except Exception, inst:
            print attrs
            print inst
            return base64.b16encode(cPickle.dumps('ErrOOR', 2))

    @withRequest
    def xmlrpc_EnableLogging(self, request):

        self.proto.logger.disabled = False
        cip = request.getClientIP()
        self.addlog(cip)
        return 'Logging enabled'

    def xmlrpc_DisableLogging(self):

        self.proto.logger.disabled = True
        return 'Logging disabled'

    def xmlrpc_testcode(self, dump):
        self.proto.testcode()
        return 'ok'

    def xmlrpc_test2(self, dump):
        self.proto.test2()
        return 'ok'

##    def xmlrpc_test_pub(self, dump):
##        self.proto.test_pub()
##        return 'ok'

    def xmlrpc_test4(self, dump):
        self.proto.test4()
        return 'ok'
#Search(self, kw_list, rtype, cserver=None):
    def xmlrpc_search(self, kw_list,cserver):
        """
        kw_list is a list of utf-8 encoded keywords
        """
        uklist=[]
##        print "I got ",kw_list
        for k in kw_list: #convert utf-8 to unicode
            if isinstance(k,unicode):
                uklist.append(k)
            else:
                uklist.append(k.decode('utf-8'))
        self.proto.Search(uklist,0,cserver)
        return 'ok'

    def xmlrpc_savecontact(self, dump):
        self.proto.saveContact()
        return 'ok'

    def xmlrpc_displaycontact(self, dump):
        self.proto.displayContactList()
        return 'ok'

    def xmlrpc_stopall(self, dump):
        self.proto.stopAll()
        #return 'ok'

    def xmlrpc_checkPort(self, dump):
##        print "xml is checking port"
        self.proto.checkPort()
        return 'ok'

    def xmlrpc_PortStatus(self, dump):
        return self.proto.port_open_status

    def xmlrpc_preparestop(self, dump):
        self.proto.prepareStop()

    def xmlrpc_publish(self, fname):
        self.proto.Publish(fname)
        return 'ok'

    def xmlrpc_numofcontact(self, dump):
        return str(self.proto.buck_list.count)

    def xmlrpc_printbucklist(self, dump):
        self.proto.buck_list.print_me(self.proto.buck_list.root)
        return 'ok'

    def xmlrpc_printreslist(self, dump):
        self.proto.rlist.print_me()
        return 'ok'


    def xmlrpc_getbucket(self, dump):
        return self.proto.buck_list.get_idle_bucket()

    def xmlrpc_getinfo(self, dump):
        return self.proto.getInfo()

    def xmlrpc_printme(self, dump):
        return self.proto.printme()

def KShell(proc_list):
    """
    A debug CLI
    """
    if platform.system() == 'Windows':
        import pyreadline
    else:
        import readline
    cmd = ''
    print 'ctrl+c to quit'
    log_list = []
    while True:
        cmd = raw_input('KADP_Ctrl@>')
        cmd = cmd.lower()
        cmd = cmd.strip()
        clist = cmd.split(' ')
        try:
            i = int(clist[1])
        except:
            i = None
        if i < 0 or i >= len(proc_list):
            i = None
        if clist[0] == 'end':
            break
        if clist[0] == 'd':  # display log of instance x
            if i != None:
                proc_list[i]['debug'].EnableLogging()
                log_list.append(i)
            continue
        if clist[0] == 'nd':  # disable log of instance x
            if i != None:
                proc_list[i]['debug'].DisableLogging()
                try:
                    log_list.remove(i)
                except Exception, inst:
                    print traceback.format_exc()
                    print str(inst)
            continue
        if clist[0] == 'xd':  # disable all current logging and enable log for instance x
            if i != None:
                for n in log_list:
                    proc_list[n]['debug'].DisableLogging()
                proc_list[i]['debug'].EnableLogging()
                log_list = [i]
            continue
        if clist[0] == 'lookup':  # excute testcode, lookup a target
            if i != None:
                proc_list[i]['debug'].testcode(False)
            continue

        if clist[0] == 'store':  # excute testcode, store some key words
            if i != None:
                proc_list[i]['debug'].test2(False)
            continue

        if clist[0] == 'pub':  # excute testcode, publish a filename
            if i != None:
                proc_list[i]['debug'].test_pub(False)
            continue

        if clist[0] == 'ss':  # search for '上海'
            if i != None:
                proc_list[i]['debug'].test4(False)
            continue

        if clist[0] == 'search':  # excute testcode, search a kw
            if len(clist) >= 3:
                kw = clist[2].decode('utf-8')
            else:
                print 'search <id> <kw>'
                continue
            if i != None:
                proc_list[i]['debug'].search(kw)
            continue

        if clist[0] == 'save':  # save contacts
            for p in proc_list:
                p['debug'].savecontact(False)
            continue

        if clist[0] == 'stop':  # stop all process
            for p in proc_list:
                try:
                    p['debug'].stopall(False)
                except:
                    pass
            continue

        if clist[0] == 'nc':  # display number of contacts
            if i != None:
                print proc_list[i]['debug'].numofcontact(False)
            continue

        if clist[0] == 'pc':  # print bucket tree
            if i != None:
                proc_list[i]['debug'].printbucklist(False)
            continue

        if clist[0] == 'printme':  # print bucket tree
            if i != None:
                print proc_list[i]['debug'].printme(False)
            continue

        if clist[0] == 'pr':  # print res list
            if i != None:
                proc_list[i]['debug'].printreslist(False)
            continue

        if clist[0] == 'p':  # publish a keyword
            if i != None:
                print 'clist is', clist[2]
                proc_list[i]['debug'].publish(clist[2])
            continue

        if clist[0] == 'gb':  # get 1st idle bucket
            if i != None:
                print proc_list[i]['debug'].getbucket(False)
            continue

        if clist[0] == 'savef':  # save test setup into file
            try:
                fname = clist[1]
            except:
                print 'usage:savef filename'
                continue
            print 'save setup in ' + fname
            newf = open(fname, 'wb')
            for p in proc_list:
                newf.write(p['ip'] + '\n')
            newf.close()
            continue

        if clist[0] == 'e':  # excute debug command on instance x
            if i != None:
                robj = \
                    cPickle.loads(base64.b16decode(proc_list[i]['debug'
                        ].report(clist[2])))
                if len(clist) > 3:
                    ac = clist[3].replace(clist[2], 'robj')
                    try:
                        print eval(ac)
                    except Exception, inst:
                        print inst
                else:
                    print robj
            else:
                print ' iam false'
            continue
    if len(proc_list)>1 or proc_list[0]['process'] != None:
        print 'killing instances...'
        for p in proc_list:
            os.kill(p['process'].pid, signal.SIGKILL)




def LoadAddr(addrf):
    addrlist = []
    if addrf != None:
        inf = open(addrf, 'r')
        for a in inf:
            a = a.strip()
            addrlist.append(a.split())
        inf.close()
        return addrlist

##
##def debugCLI(xmlSvrList):
##    """
##    This provides a debug CLI
##    xmlSvrList is a list of XML RPC server
##    """
##    pass


if __name__ == '__main__':

    if len(sys.argv) >= 2:
        if sys.argv[1].lower() == '-server' or sys.argv[1].lower() == '-product':

##            print 'starting KADP...'
            lport = KPORT
            nodeid = None
            bip = ''
            if sys.argv[1].lower() == '-product':
                bip = ''
                mynodeid = None
                #lport = KPORT
                conf_dir = None
                cserver = None
                try:
                    lport = int(sys.argv[2])
                except:
                    lport=KPORT
                if sys.argv[3] == 'NONE':
                    mynodeid = None
                else:
                    mynodeid = longbin.LongBin(binstr=sys.argv[3])

                try:
                    fscan = bool(int(sys.argv[4]))
                except:
                    fscan = False
                try:
                    nodebug = bool(int(sys.argv[5]))
                except:
                    nodebug = False
                try:
                    cserver = sys.argv[6]
                except:
                    cserver = None
            # following are test code
            else:
                if sys.argv[2]=='NONE':
                    bip = ''
                else:
                    bip = sys.argv[2]
                if sys.argv[4]=='NONE':
                    myid=None
                else:
                    myid = sys.argv[4]
                lport = int(sys.argv[3])
                if sys.argv[5]=='NONE':
                    conf_dir=None
                else:
                    conf_dir = sys.argv[5]
                mynodeid = longbin.LongBin(myid)
                try:
                    fscan = bool(int(sys.argv[6]))
                except:
                    fscan = False
                try:
                    cserver = sys.argv[7]
                except:
                    cserver = None
                nodebug = True


            # end of test code

            protocol = KADProtocol(None, lport, mynodeid, 'mainlist.txt'
                                   , bip=bip,conf_dir=conf_dir,force_scan=fscan,
                                   cserver_url=cserver,nodebug=nodebug)

            # bind protocol to reactor
            t = reactor.listenUDP(protocol.listening_port, protocol,
                                  interface=bip)
            protocol.setLPort(t)

            # reactor.callInThread(protocol.updateContactList)

            # reactor.callInThread(protocol.BootScan)
            # create XML interface for debug
            # Have to use twisted.web.xmlrpc module, otherwise ctrl+c won't work

            txmlsvr = tXMLSvr(protocol)
            if bip == '':
                reactor.listenTCP(KCPORT, TW_xmlserver.Site(txmlsvr),
                              interface="127.0.0.1")
            else: #listen on loopback int
                reactor.listenTCP(KCPORT, TW_xmlserver.Site(txmlsvr),
                              interface=bip)
            reactor.run()
            #print 'stopped'
            sys.exit(0)
        elif sys.argv[1].lower() == '-debug':

            # this is a debug shell via XML-RPC
            # shell command format is 'attr-name(of KADProtocol) expression'
            # for example, "buck_list len(buck_list)" to return len of buck_list
            # command "end" to quit

            #start UDP server @ port 9999
            HOST, PORT = "localhost", 9999
            server = ThreadingUDPServer((HOST, PORT), MyUDPHandler)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.start()

            print "log listener started."

            if len(sys.argv) <= 2:
                dst_host = '127.0.0.1'
                dst_port = KCPORT
            else:

                  # use argv[2] as the XML-RPC server's domain name(or IP)

                dst_host = sys.argv[2]
                dst_port = int(sys.argv[3])
            s = xmlrpclib.Server('http://' + dst_host + ':'
                                 + str(dst_port))
            proc_list = []
            instance = {'process': None, 'debug': s, 'ip': dst_host}
            print instance
            proc_list.append(instance)
            KShell(proc_list)
            server.shutdown()
            print 'Quit from ' + dst_host + '.'


        elif sys.argv[1].lower() == '-test':#this is for testing&debug purpose
            if MYOS != 'Linux' or (MYOS=='Linux' and os.geteuid() != 0):
                print "Testing function only works under Linux as root"
                sys.exit(1)
            print "Testing start at ",time.asctime()

                                          # start mulitple instances

            import signal
            import sys


            def signal_handler(signal, frame):
                global protocol
                print 'You pressed Ctrl+C!'
                protocol.run_bootscan = False



            signal.signal(signal.SIGINT, signal_handler)

            start_port = KPORT
            lport = start_port
            start_id = 11110111100000000000
            proc_list = []
            if len(sys.argv) >= 3:
                try:
                    inumber = int(sys.argv[2])
                    fscan = sys.argv[3]

                except:
                    fname = sys.argv[2]
                    #instance_count = int(sys.argv[3])
                    inumber = False
                    fscan = '0'
            else:
                inumber = 10
                fscan = '0'

            if inumber != False:
                addrlist = LoadAddr('mainlist.txt')
                addr = addrlist[0]  # only use first block to speeds up bootstrapping
                blocksize = int(addr[1])

                start_addr = addr[0]
                sipi = struct.unpack('>L',
                        socket.inet_aton(start_addr))[0]
                stepsize = blocksize / inumber

                for i in range(inumber):
                    tip = '0.0.0.0'
                    while tip.split('.')[3] == '0' or tip.split('.')[3] \
                        == '255':
                        delta = random.randint(stepsize * i + 1,
                                stepsize * (i + 1))

                        # delta=random.randint(1,100)

                        tipi = sipi + delta
                        tip = socket.inet_ntoa(struct.pack('>L', tipi))
                    cmd = ['ifconfig', 'eth0:' + str(i), tip + '/30']

                    # cmd="ifconfig eth0:"+str(i)+" "+tip+"/32"

                    print cmd
                    subprocess.call(cmd)

                    # lport=start_port+i

                    myid = '{0:020d}'.format(i * 100 + start_id)
                    cmd = [
                        '/usr/bin/python',
                        'KADP.py',
                        '-server',
                        tip,
                        str(lport),
                        myid,
                        os.environ['HOME']+"/kconf-"+str(i),
                        fscan,
                        ]

                    # cmd="/usr/bin/python KADP.py -server "+tip+" "+str(lport)+" "+myid

                    print cmd

                    # p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

                    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
                    s = xmlrpclib.Server('http://' + tip + ':'
                            + str(KCPORT))
                    instance = {'process': p, 'debug': s, 'ip': tip}
                    proc_list.append(instance)
                print 'forked ' + str(inumber) + ' KADP instances.'
            else:# load a config file
                newf = open(fname, 'r')
                i = 0
                for tip in newf:
                    #if i > instance_count: break
                    tip = tip[:-1]
                    cmd = ['ifconfig', 'eth0:' + str(i), tip + '/30']

                    # cmd="ifconfig eth0:"+str(i)+" "+tip+"/32"

                    print cmd
                    subprocess.call(cmd)

                    # lport=start_port+i

                    myid = '{0:020d}'.format(i * 100 + start_id)
                    cmd = [
                        '/usr/bin/xterm',
                        '-xrm',
                        "'XTerm*VT100.translations: #override <Btn1Up>: select-end(PRIMARY, CLIPBOARD, CUT_BUFFER0)'",
                        '-hold',
                        '-T',
                        myid,
                        '-e',
                        '/usr/bin/python',
                        'KADP.py',
                        '-server',
                        tip,
                        str(lport),
                        myid,
                        os.environ['HOME']+"/kconf-"+str(i),
                        '0',
                        ]


                    # cmd="/usr/bin/python KADP.py -server "+tip+" "+str(lport)+" "+myid

                    print cmd

                    # p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

                    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
                    s = xmlrpclib.Server('http://' + tip + ':'
                            + str(KCPORT))
                    instance = {'process': p, 'debug': s, 'ip': tip}
                    proc_list.append(instance)
                    i += 1
                print 'forked ' + str(i) + ' instances from ' + fname
            KShell(proc_list)
            print 'Done.'
    else:
        print 'KADP, a Kademlia based P2P protcol in python.'
        print 'Usage:'
        print ' -server [bip lport nodeid(20byte str) conf_dir] [force_scan] [cserver_url]'
        print ' -product [lport nodeid(160byte str) force_scan [nodebug] [cserver_url]]'
        print ' -debug [SVR-hostname port]'
        print ' -test [{numberofinstances [forcescan]|conf_file_name}]'

