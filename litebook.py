#!/usr/bin/env py32
# -*- coding: utf-8 -*-


#This is the source file of LiteBook (for all Windows/Linux/OSX)
#see Readme.txt for module dependcy
#
#
#


import download_manager
import ltbsearchdiag
import signal
import xmlrpclib
import myup
import fj
import traceback
import platform
import sys
import kpub
#from lxml import etree
#import jft
MYOS = platform.system()
osarch=platform.architecture()
if osarch[1]=='ELF' and MYOS == 'Linux':
    if osarch[0]=='64bit':
        from lxml_linux_64 import etree
    elif osarch[0]=='32bit':
        from lxml_linux import etree
elif MYOS == 'Darwin':
    from lxml_osx import etree
else:
    from lxml import etree

if MYOS != 'Linux' and MYOS != 'Darwin' and MYOS != 'Windows':
    print "This version of litebook only support Linux and MAC OSX"
    sys.exit(1)
if MYOS == 'Linux':
    import dbus
elif MYOS == 'Darwin':
    import netifaces
elif MYOS == 'Windows':
    import wmi
    import win32api
import Zeroconf
import socket
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import SocketServer
import posixpath
import BaseHTTPServer
import ez_epub
import gcepub
import ComboDialog
import liteview
import webbrowser
import keygrid

import imp
import urllib2
import HTMLParser
import glob
import math
import htmlentitydefs
import wx
import wx.lib.mixins.listctrl
import wx.lib.newevent
import sqlite3
import struct
import zlib
import os
import glob
import sys
import ConfigParser
import time
from datetime import datetime
import re
import zipfile
import rarfile
import codecs
import shutil
import encodings.gbk
import encodings.utf_8
import encodings.big5
import encodings.utf_16
from chardet.universaldetector import UniversalDetector
import chardet
if MYOS == 'Windows':
    import win32process
    import UnRAR2
import subprocess
import thread
import hashlib
import urllib
import threading


try:
    from agw import hyperlink as hl
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.hyperlink as hl
try:
    from agw import genericmessagedialog as GMD
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.genericmessagedialog as GMD

# begin wxGlade: extracode
# end wxGlade

(UpdateStatusBarEvent, EVT_UPDATE_STATUSBAR) = wx.lib.newevent.NewEvent()
(ReadTimeAlert,EVT_ReadTimeAlert)=wx.lib.newevent.NewEvent()
(ScrollDownPage,EVT_ScrollDownPage)=wx.lib.newevent.NewEvent()
##(GetPosEvent,EVT_GetPos)=wx.lib.newevent.NewEvent()
(VerCheckEvent,EVT_VerCheck)=wx.lib.newevent.NewEvent()
(DownloadFinishedAlert,EVT_DFA)=wx.lib.newevent.NewEvent()
(DownloadUpdateAlert,EVT_DUA)=wx.lib.newevent.NewEvent()
(AlertMsgEvt,EVT_AME)=wx.lib.newevent.NewEvent()
(UpdateEvt,EVT_UPD)=wx.lib.newevent.NewEvent()






def GetMDNSIP_OSX():
    """
    return v4 addr of 1st wlan interface in OSX, if there is no wlan interface,
    then the v4 addr of 1st network interface will be returned
    """

    try:
        r = subprocess.check_output(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport','prefs'])
    except:
        r = False
    if r != False:
        wif = r.splitlines()[0].split()[-1:][0][:-1]
        try:
            return netifaces.ifaddresses(wif)[2][0]['addr']
        except:
            pass
    for ifname in netifaces.interfaces(): #return addr of 1st network interface
        if 2 in netifaces.ifaddresses(ifname):
            if_addr = netifaces.ifaddresses(wif)[2][0]['addr']
            if if_addr != '127.0.0.1' and if_addr != None and if_addr != '':
                return if_addr




def GetMDNSIP_Win():#windows version
    global GlobalConfig
    """This function return IPv4 addr of 1st WLAN interface. if there is no WLAN interface, then it will return the v4 address of the main interface """
    if sys.platform=='win32':
        if GlobalConfig['mDNS_interface']=='AUTO':
            wlan_int_id=None
            for nic in wmi.WMI().Win32_NetworkAdapter():
                if nic.NetConnectionID == "Wireless Network Connection":
                    wlan_int_id=nic.Index
                    break

            if wlan_int_id<>None:
                for nic in wmi.WMI ().Win32_NetworkAdapterConfiguration (IPEnabled=1):
                    if nic.Index==wlan_int_id:
                        wlan_ip=nic.IPAddress[0]
                        break
            else:
                wlan_ip=None
        else:
            wlan_ip=None
            for nic in wmi.WMI ().Win32_NetworkAdapterConfiguration (IPEnabled=1):
                if nic.Caption==GlobalConfig['mDNS_interface']:
                    wlan_ip=nic.IPAddress[0]
                    break
    if wlan_ip<>None:
        try:
            socket.inet_aton(wlan_ip)
        except:
            wlan_ip=None
    if wlan_ip<>None:
        if wlan_ip=='0.0.0.0':wlan_ip=None
        else:
            if wlan_ip[:7]=='169.254':wlan_ip=None
    if wlan_ip==None:
        ar=socket.getaddrinfo(socket.gethostname(), 80, 0, 0, socket.SOL_TCP)
        if socket.has_ipv6:
            if len(ar)>1:
                wlan_ip=ar[1][4][0]
            else:
                wlan_ip=ar[0][4][0]
        else:
            wlan_ip=ar[0][4][0]
        if wlan_ip == '0.0.0.0' or wlan_ip=='127.0.0.1':
            return False
    else:
        return wlan_ip


def GetMDNSIP():
    global GlobalConfig
    """This function return IPv4 addr of 1st WLAN interface. if there is no WLAN interface, then it will return the v4 address of the main interface """
    bus = dbus.SystemBus()
    proxy = bus.get_object("org.freedesktop.NetworkManager",
    "/org/freedesktop/NetworkManager")
    manager = dbus.Interface(proxy, "org.freedesktop.NetworkManager")
    # Get device-specific state
    devices = manager.GetDevices()
    for d in devices:
       dev_proxy = bus.get_object("org.freedesktop.NetworkManager", d)
       prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")

       # Get the device's current state and interface name
       state = prop_iface.Get("org.freedesktop.NetworkManager.Device", "State")
       name = prop_iface.Get("org.freedesktop.NetworkManager.Device", "Interface")
       ifa = "org.freedesktop.NetworkManager.Device"
       type = prop_iface.Get(ifa, "DeviceType")
       addr = prop_iface.Get(ifa, "Ip4Address")

       wlan_ip=None
       candidate_ip=None

       if state == 8:   # activated
           addr_dotted = socket.inet_ntoa(struct.pack('<L', addr))
           str_addr=str(addr_dotted)
           if type==2: #if it is a wifi interface
               wlan_ip=str_addr
               break
           else:
               if type==1:
                   candidate_ip=str_addr

    if wlan_ip == '0.0.0.0' or wlan_ip=='127.0.0.1':
        return False
    elif wlan_ip==None:
        if candidate_ip<>None:
            return candidate_ip
        else:
            return False
    else:
        return wlan_ip

def cmp_filename(x,y):
    p=re.compile('\d+')
    if p.search(x)==None:
        m=0
    else:
        m=int(p.search(x).group())

    if p.search(y)==None:
        n=0
    else:
        n=int(p.search(y).group())
    return m-n


def parseBook(instr,divide_method=0,zishu=10000):
    """
    preparation for epub file generation
    """
    if not isinstance(instr,unicode):
        instr=instr.decode('GBK','ignore')
##    rlist,c_list=GenCatalog(instr,divide_method,zishu)
    rlist=GenCatalog(instr,divide_method,zishu)
    sections = []
    istr=instr
    last_pos=0
    i=0
    for c in rlist:
        section = ez_epub.Section()
        #section.css = """.em { font-style: italic; }"""
        section.title = c[0]
        x=c[1]
        if i<len(rlist)-1:
            sec_str=istr[x:rlist[i+1][1]]
        else:
            sec_str=istr[x:]
##        line_list = sec_str.splitlines()
##        sec_str=''
##        for line in line_list:
##            sec_str+=u'<p>'+line+u'</p>\n'
        section.text.append(sec_str)
        last_pos=x
        sections.append(section)
        i+=1
    return sections

def txt2epub(instr,outfile,title='',authors=[],divide_method=0,zishu=10000):
    """
    infile: path of input text file
    outfile: path of output text file.(don't add .epub)
    title: book title
    authors: list of author names
    """
    book = ez_epub.Book()
    if title=='':
        book.title=outfile
    else:
        book.title = title
    book.authors = authors
    book.sections = parseBook(instr,divide_method,zishu)
    book.make(outfile)
    try:
        shutil.rmtree(outfile)
    except:
        pass







OnDirectSeenPage=False
GlobalConfig={}
KeyConfigList=[]
KeyMenuList={}
PluginList={}
OpenedFileList=[]
current_file=''
load_zip=False
current_file_list=[]
current_zip_file=''
OnScreenFileList=[]
CurOnScreenFileIndex=0
BookMarkList=[]
ThemeList=[]
BookDB=[]
Ticking=True
Version='3.0 '+MYOS
I_Version=3.00 # this is used to check updated version
lb_hash='3de03ac38cc1c2dc0547ee09f866ee7b'

def cur_file_dir():
    #获取脚本路径
    global MYOS
    if MYOS == 'Linux':
        path = sys.path[0]
    elif MYOS == 'Windows':
        return os.path.dirname(AnyToUnicode(os.path.abspath(sys.argv[0])))
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

def str2list(istr):
    rlist=[]
    if istr[0]<>'[' and istr[0]<>'(':
        return istr
    mlist=istr[1:-1].split(',')
    for m in mlist:
        rlist.append(int(m))
    return rlist

def DetectFileCoding(filepath,type='txt',zipfilepath=''):
    """Return a file's encoding, need import chardet """
    global MYOS
    if type=='txt':
        try:
            input_file=open(filepath,'r')
        except:
            dlg = wx.MessageDialog(None, filepath+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return "error"
    else:
        if type=='zip':
            try:
                zfile=zipfile.ZipFile(zipfilepath)
                if isinstance(filepath, unicode):
                    filepath=filepath.encode('gbk')
                input_file=zfile.read(filepath)
            except:
                dlg = wx.MessageDialog(None, zipfilepath+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return "error"
            lines=input_file.splitlines()
            detector = UniversalDetector()
            line_count=0
            for line in lines:
                detector.feed(line)
                if detector.done or line_count==50: break# decrease this number to improve speed
                line_count+=1
            detector.close()
            if detector.result['encoding']<>None:
                return detector.result['encoding'].lower()
            else:
                return None
    if type=='rar':
        if MYOS == 'Windows':
            try:
                rfile=UnRAR2.RarFile(zipfilepath)
                buff=rfile.read_files(filepath)
            except Exception as inst:
                dlg = wx.MessageDialog(None, zipfilepath+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return "error"
            lines=buff[0][1].splitlines()
        else:
            buff=unrar(zipfilepath,filepath)
            if buff==False:
                dlg = wx.MessageDialog(None, zipfilepath+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return "error"
            lines=buff.splitlines()
        detector = UniversalDetector()
        line_count=0
        for line in lines:
            line=line[:800] # decrease this number to improve speed
            detector.feed(line)
            if detector.done or line_count==1000: break# decrease this number to improve speed
            line_count+=1
        detector.close()
        if detector.result['encoding']<>None:
            return detector.result['encoding'].lower()
        else:
            return None
    detector = UniversalDetector()
    line_count=0
    while line_count<50: # decrease this number to improve speed
        if type=='txt':line=input_file.readline(100) # decrease this number to improve speed
        detector.feed(line)
        if detector.done: break
        line_count+=1
    detector.close()
    input_file.close()
    if detector.result['encoding']<>None:
        return detector.result['encoding'].lower()
    else:
        return None

def GetPint():
    p=platform.architecture()
    if p[0]=='32bit': return 'L'
    else:
        return 'I'

def isfull(l):
    xx=0
    n=len(l)
    count=0
    while xx<n:
        if l[xx]==-1: count+=1
        xx+=1

    if count==0: return True
    else:
        return int((float(n-count)/float(n))*100)

def JtoF(data):
   #简体到繁体
   max=fj.zh_dict.__len__()
   dlg = wx.ProgressDialog(u"简体－>繁体", u'    正在转换中...   ',max,None,wx.PD_SMOOTH|wx.PD_AUTO_HIDE)
   i=0
   for s in fj.zh_dict:
       i+=1
       dlg.Update(i)
       data = data.replace(s,fj.zh_dict[s])
   dlg.Destroy()
   return data

def FtoJ(data):
   #繁体到简体
   max=fj.zh_dict.__len__()
   dlg = wx.ProgressDialog(u"繁体－>简体", u'    正在转换中...    ',max,None,wx.PD_SMOOTH|wx.PD_AUTO_HIDE)
   i=0
   for s in fj.zh_dict:
       i+=1
       dlg.Update(i)
       data = data.replace(fj.zh_dict[s],s)
   dlg.Destroy()
   return data



def GenCatalog(instr,divide_method=0,zishu=10000):
    """
    Return a list of : [cname,pos]
    """
    if not isinstance(instr,unicode):
        instr=instr.decode("gbk")
    rlist=[]
    #c_list=[]
    if divide_method==0:
    #自动划分章节
        max_chapter_len=50 #the chapter len>50 will be skipped,this is used to detect redundant chapter lines
        cur_pos=0
        n=len(instr)
        hash_len=len(lb_hash)
        cpos=instr.find(lb_hash)
        if cpos<>-1:
            while cur_pos<n:
                cur_pos=instr.find(lb_hash,cur_pos)
                if cur_pos==-1: break
                tstr=instr[cur_pos:cur_pos+100]
                llist=tstr.splitlines()
                chapter=llist[0][hash_len:]
                rlist.append([chapter,cur_pos])
##                rlist[chapter]=cur_pos
##                c_list.append(chapter)
                cur_pos+=1
        else:
            #if there is NO lb_hash string found, try to automatic guess the catalog
            chnum_str=u'(零|一|壹|二|俩|两|贰|三|叁|四|肆|五|伍|六|陆|七|柒|八|捌|九|玖|十|拾|百|佰|千|仟|万|0|1|2|3|4|5|6|7|8|9)'
            ch_ten_str=u'(十|百|千|万)'
            ch_ten_dict={u'十':u'0',u'百':u'00',u'千':u'000',u'万':u'0000',}
            ch_dict={u'零':u'0',u'一':u'1',u'二':u'2',u'三':u'3',u'四':u'4',u'五':u'5',u'六':u'6',u'七':u'7',u'八':u'8',u'九':u'9',}
            p=re.compile(u'第'+chnum_str+u'+(章|节|部|卷|回)',re.L|re.U)
            nlist=p.findall(instr)
            m_list=p.finditer(instr)
            if len(nlist)<5:
                p=re.compile(u'(章|节|部|卷|回)'+chnum_str+u'+\s',re.L|re.U)
                m_list=p.finditer(instr)
            #last_chapter=None
##            c_list.append(u'本书首页>>>>')
##            rlist[u'本书首页>>>>']=0
            rlist.append([u'本书首页>>>>',0])
            last_end=0
##            last_chapter=None
            for m in m_list:
                if instr[last_end:m.start()].find('\n')==-1:

                    continue
                re_start_pos=m.start()
                re_end_pos=m.end()
                last_end=re_end_pos
    ##            if last_chapter==instr[re_start_pos:re_end_pos]:
    ##                continue
    ##            else:
    ##                last_chapter=instr[re_start_pos:re_end_pos]
                start_pos=re_start_pos
                ch=instr[start_pos]
                pos1=start_pos
                while ch<>'\n':
                    pos1-=1
                    ch=instr[pos1]
                pos1+=1
                pos2=start_pos
                ch=instr[start_pos]
                while ch<>'\n':
                    pos2+=1
                    ch=instr[pos2]
                #pos2-=1
                if pos2-pos1>50:
                    continue
                chapter=instr[pos1:pos2].strip()
##                if chapter == last_chapter:
##                    continue
                rlist.append([chapter,pos1])
##                rlist[chapter]=pos1
##                c_list.append(chapter)
##                last_chapter = chapter

    elif divide_method==1:
        #按字数划分
        c_list=[]
        len_str=len(instr)
        num_ch,left=divmod(len_str,zishu)
        cur_pos=0
        i=1
        while i<=num_ch:
            cur_pos=(i-1)*zishu
            chapter=u'第'+unicode(i)+u'章(字数划分)'
            c_list.append(chapter)
            rlist.append([chapter,cur_pos])
            #rlist[chapter]=cur_pos
            i+=1
        chapter=u'第'+unicode(i)+u'章(字数划分)'
        rlist.append([chapter,num_ch*zishu])
##        c_list.append(chapter)
##        rlist[chapter]=num_ch*zishu
    #for c in c_list:print c
##
##    print "the final rlist is ", rlist
##    print "the final clist is ",c_list
##    return (rlist,c_list)
    return rlist


def AnyToUnicode(input_str,coding=None):
    """Convert any coding str into unicode str. this function should used with function DetectFileCoding"""
    if isinstance(input_str,unicode): return input_str
    if coding<>None:
        if coding <> 'utf-8':
            if coding.lower()=='gb2312':
                coding='GBK'
            output_str=unicode(input_str,coding,errors='replace')
        else:
            output_str=input_str.decode('utf-8',"replace")
    else:
        output_str=unicode(input_str,'gbk',errors='replace')
    return output_str

def readPlugin():
    global PluginList, MYOS
    PluginList={}
    if MYOS != 'Windows':
        flist=glob.glob(cur_file_dir()+"/plugin/*.py")
    else:
        flist=glob.glob(os.path.dirname(AnyToUnicode(os.path.abspath(sys.argv[0])))+u"\\plugin\\*.py")
    i=0
    for f in flist:
        if MYOS != 'Windows':
            bname=os.path.basename(f)
            fpath=cur_file_dir()+"/plugin/"+bname
            fpath=fpath.encode('utf-8')
        else:
            bname=os.path.basename(AnyToUnicode(f))
            fpath=os.path.dirname(AnyToUnicode(os.path.abspath(sys.argv[0])))+u'\\plugin\\'+bname
            fpath=fpath.encode('gbk')
        try:
            PluginList[bname]=imp.load_source(str(i),fpath)
        except Exception as inst:
##            print traceback.format_exc()
##            print inst
            return False
        i+=1
##    for k in PluginList.keys():
##        print k

def InstallDefaultConfig():
    global ThemeList,KeyConfigList
    fname=cur_file_dir()+u"/defaultconfig.ini"
    config=MyConfig()
    try:
        ffp=codecs.open(fname,encoding='utf-8',mode='r')
        config.readfp(ffp)
    except:
        return

    #install appearance
    if config.has_section('Appearance'):
        ft_list=config.items('Appearance')
        for ft in ft_list:
            tname=ft[0]
            f=ft[1].split('|')
            if len(f)<>21: continue
            try:
                l={}
                l['font']=wx.Font(int(f[0]),int(f[1]),int(f[2]),int(f[3]),eval(f[4]),f[5],int(f[6]))
                l['fcolor']=eval(f[7])
                l['bcolor']=eval(f[8])
                if f[9]<>'None':
                    l['backgroundimg']=f[9]
                else:
                    l['backgroundimg']=None
                l['showmode']=f[10]
                l['backgroundimglayout']=f[11]
                l['underline']=eval(f[12])
                l['underlinestyle']=int(f[13])
                l['underlinecolor']=f[14]
                l['pagemargin']=int(f[15])
                l['bookmargin']=int(f[16])
                l['vbookmargin']=int(f[17])
                l['centralmargin']=int(f[18])
                l['linespace']=int(f[19])
                l['vlinespace']=int(f[20])
                l['name']=tname
                l['config']=ft[1]
            except:
                continue
            ThemeList.append(l)
    #install key config
    secs=config.sections()
    secs.remove('Appearance')
    for sec in secs:
        tname=sec
        kconfig=[]
        kconfig.append(tname)
        for f,v in keygrid.LB2_func_list.items():
            try:
                cstr=config.get(sec,f)
                cstr_list=cstr.split('&&')
                for cs in cstr_list:
                    kconfig.append((f,cs))
            except:
                kconfig.append((f,v))
        KeyConfigList.append(kconfig)
    GlobalConfig['InstallDefaultConfig']=False




def readKeyConfig():
    global KeyConfigList,KeyMenuList,MYOS
    config=MyConfig()
    try:
        if MYOS == 'Windows':
            ffp=codecs.open(os.environ['APPDATA'].decode('gbk')+u"\\litebook_key.ini",encoding='utf-8',mode='r')
        else:
            ffp=codecs.open(unicode(os.environ['HOME'],'utf-8')+u"/.litebook_key.ini",encoding='utf-8',mode='r')
        config.readfp(ffp)
    except:
        kconfig=[]
        kconfig.append(('last'))
        for func,keyval in keygrid.LB2_func_list.items():
            kconfig.append((func,keyval))
##        kconfig.append((u'向上翻行',"----+WXK_UP"))
##        kconfig.append((u'向下翻行',"----+WXK_DOWN"))
##        kconfig.append((u'向上翻页',"----+WXK_PAGEUP"))
##        kconfig.append((u'向上翻页',"----+WXK_LEFT"))
##        kconfig.append((u'向下翻页',"----+WXK_PAGEDOWN"))
##        kconfig.append((u'向下翻页',"----+WXK_RIGHT"))
##        kconfig.append((u'向下翻页',"----+WXK_SPACE"))
##        kconfig.append((u'向上翻半页','----+","'))
##        kconfig.append((u'向下翻半页','----+"."'))
##        kconfig.append((u'后退10%','----+"["'))
##        kconfig.append((u'前进10%','----+"]"'))
##        kconfig.append((u'后退1%','----+"9"'))
##        kconfig.append((u'前进1%','----+"0"'))
##
##        kconfig.append((u'跳到首页',"----+WXK_HOME"))
##        kconfig.append((u'跳到结尾',"----+WXK_END"))
##        kconfig.append((u'文件列表','C---+"O"'))
##        kconfig.append((u'打开文件','C---+"P"'))
##        kconfig.append((u'另存为','C---+"S"'))
##        kconfig.append((u'关闭','C---+"Z"'))
##        kconfig.append((u'上一个文件','C---+"["'))
##        kconfig.append((u'下一个文件','C---+"]"'))
##        kconfig.append((u'搜索小说网站','-A--+"C"'))
##        kconfig.append((u'搜索LTBNET','-A--+"S"'))
##        kconfig.append((u'重新载入插件','C---+"R"'))
##        kconfig.append((u'选项','-A--+"O"'))
##        kconfig.append((u'退出','-A--+"X"'))
##        kconfig.append((u'拷贝','C---+"C"'))
##        kconfig.append((u'查找','C---+"F"'))
##        kconfig.append((u'查找下一个','----+WXK_F3'))
##        kconfig.append((u'查找上一个','----+WXK_F4'))
##        kconfig.append((u'替换','C---+"H"'))
##        kconfig.append((u'纸张显示模式','-A--+"M"'))
##        kconfig.append((u'书本显示模式','-A--+"B"'))
##        kconfig.append((u'竖排书本显示模式','-A--+"N"'))
##        kconfig.append((u'显示目录','C---+"U"'))
##        kconfig.append((u'显示工具栏','C---+"T"'))
##        kconfig.append((u'缩小工具栏','C---+"-"'))
##        kconfig.append((u'放大工具栏','C---+"="'))
##        kconfig.append((u'全屏显示','C---+"I"'))
##        kconfig.append((u'显示文件侧边栏','-A--+"D"'))
##        kconfig.append((u'自动翻页','-A--+"T"'))
##        kconfig.append((u'智能分段','-A--+"P"'))
##        kconfig.append((u'添加到收藏夹','C---+"D"'))
##        kconfig.append((u'整理收藏夹','C---+"M"'))
##        kconfig.append((u'简明帮助','----+WXK_F1'))
##        kconfig.append((u'版本更新内容','----+WXK_F2'))
##        kconfig.append((u'检查更新','----+WXK_F5'))
##        kconfig.append((u'关于','----+WXK_F6'))
##        kconfig.append((u'过滤HTML标记','----+WXK_F9'))
##        kconfig.append((u'切换为简体字','----+WXK_F7'))
##        kconfig.append((u'切换为繁体字','----+WXK_F8'))
##        kconfig.append((u'显示进度条','----+"Z"'))
##        kconfig.append((u'增大字体','----+"="'))
##        kconfig.append((u'减小字体','----+"-"'))
##        kconfig.append((u'清空缓存','CA--+"Q"'))
##        kconfig.append((u'最小化','----+WXK_ESCAPE'))
##        kconfig.append((u'生成EPUB文件','C---+"E"'))
##        kconfig.append((u'启用WEB服务器','-A--+"W"'))
##        kconfig.append((u'显示章节侧边栏','-A--+"J"'))
        KeyConfigList.append(kconfig)
        i=1
        tl=len(kconfig)
        while i<tl:
            KeyMenuList[kconfig[i][0]]=keygrid.str2menu(kconfig[i][1])
            i+=1
        return
    if not config.has_section('last'):
        kconfig=[]
        kconfig.append(('last'))
        for func,keyval in keygrid.LB2_func_list.items():
            kconfig.append((func,keyval))
##        kconfig.append((u'向上翻行',"----+WXK_UP"))
##        kconfig.append((u'向下翻行',"----+WXK_DOWN"))
##        kconfig.append((u'向上翻页',"----+WXK_PAGEUP"))
##        kconfig.append((u'向上翻页',"----+WXK_LEFT"))
##        kconfig.append((u'向下翻页',"----+WXK_PAGEDOWN"))
##        kconfig.append((u'向下翻页',"----+WXK_RIGHT"))
##        kconfig.append((u'向下翻页',"----+WXK_SPACE"))
##        kconfig.append((u'向上翻半页','----+","'))
##        kconfig.append((u'向下翻半页','----+"."'))
##        kconfig.append((u'后退10%','----+"["'))
##        kconfig.append((u'前进10%','----+"]"'))
##        kconfig.append((u'后退1%','----+"9"'))
##        kconfig.append((u'前进1%','----+"0"'))
##
##        kconfig.append((u'跳到首页',"----+WXK_HOME"))
##        kconfig.append((u'跳到结尾',"----+WXK_END"))
##        kconfig.append((u'文件列表','C---+"O"'))
##        kconfig.append((u'打开文件','C---+"P"'))
##        kconfig.append((u'另存为','C---+"S"'))
##        kconfig.append((u'关闭','C---+"Z"'))
##        kconfig.append((u'上一个文件','C---+"["'))
##        kconfig.append((u'下一个文件','C---+"]"'))
##        kconfig.append((u'搜索小说网站','-A--+"C"'))
##        kconfig.append((u'搜索LTBNET','-A--+"S"'))
##        kconfig.append((u'重新载入插件','C---+"R"'))
##        kconfig.append((u'选项','-A--+"O"'))
##        kconfig.append((u'退出','-A--+"X"'))
##        kconfig.append((u'拷贝','C---+"C"'))
##        kconfig.append((u'查找','C---+"F"'))
##        kconfig.append((u'替换','C---+"H"'))
##        kconfig.append((u'查找下一个','----+WXK_F3'))
##        kconfig.append((u'查找上一个','----+WXK_F4'))
##        kconfig.append((u'纸张显示模式','-A--+"M"'))
##        kconfig.append((u'书本显示模式','-A--+"B"'))
##        kconfig.append((u'竖排书本显示模式','-A--+"N"'))
##        kconfig.append((u'显示工具栏','C---+"T"'))
##        kconfig.append((u'缩小工具栏','C---+"-"'))
##        kconfig.append((u'放大工具栏','C---+"="'))
##        kconfig.append((u'显示目录','C---+"U"'))
##        kconfig.append((u'全屏显示','C---+"I"'))
##        kconfig.append((u'显示文件侧边栏','-A--+"D"'))
##        kconfig.append((u'自动翻页','-A--+"T"'))
##        kconfig.append((u'智能分段','-A--+"P"'))
##        kconfig.append((u'添加到收藏夹','C---+"D"'))
##        kconfig.append((u'整理收藏夹','C---+"M"'))
##        kconfig.append((u'简明帮助','----+WXK_F1'))
##        kconfig.append((u'版本更新内容','----+WXK_F2'))
##        kconfig.append((u'检查更新','----+WXK_F5'))
##        kconfig.append((u'关于','----+WXK_F6'))
##        kconfig.append((u'过滤HTML标记','----+WXK_F9'))
##        kconfig.append((u'切换为简体字','----+WXK_F7'))
##        kconfig.append((u'切换为繁体字','----+WXK_F8'))
##        kconfig.append((u'显示进度条','----+"Z"'))
##        kconfig.append((u'增大字体','----+"="'))
##        kconfig.append((u'减小字体','----+"-"'))
##        kconfig.append((u'清空缓存','CA--+"Q"'))
##        kconfig.append((u'最小化','----+WXK_ESCAPE'))
##        kconfig.append((u'生成EPUB文件','C---+"E"'))
##        kconfig.append((u'启用WEB服务器','-A--+"W"'))
##        kconfig.append((u'显示章节侧边栏','-A--+"J"'))

        KeyConfigList.append(kconfig)
    else:
        kconfig=[]
        kconfig.append(('last'))
        for f,v in keygrid.LB2_func_list.items():
            try:
                cstr=config.get('last',f)
                cstr_list=cstr.split('&&')
                for cs in cstr_list:
                    kconfig.append((f,cs))
            except:
                kconfig.append((f,v))
        KeyConfigList.append(kconfig)
    secs=config.sections()
    secs.remove('last')
    for sec in secs:
        kconfig=[]
        kconfig.append((sec))
        opts=config.options(sec)
        for opt in opts:
            cstr=config.get(sec,opt)
            cstr_list=cstr.split('&&')
            for cs in cstr_list:
                kconfig.append((opt,cs))
        KeyConfigList.append(kconfig)


    for kconfig in KeyConfigList:
        if kconfig[0]=='last':
            break
    i=1
    tl=len(kconfig)
    while i<tl:
        KeyMenuList[kconfig[i][0]]=keygrid.str2menu(kconfig[i][1])
        i+=1



def writeKeyConfig():
    global KeyConfigList,MYOS
    config=MyConfig()
    for kconfig in KeyConfigList:
        config.add_section(kconfig[0])
        i=1
        kl=len(kconfig)
        cstr={}
        while i<kl:
            if kconfig[i][0] not in cstr:
                cstr[kconfig[i][0]]=kconfig[i][1]
            else:
                cstr[kconfig[i][0]]+="&&"+kconfig[i][1]
            i+=1
        for key,val in cstr.items():
            config.set(kconfig[0],unicode(key),val)

    try:
        if MYOS == 'Windows':
            ConfigFile=codecs.open(os.environ['APPDATA'].decode('gbk')+u'\\litebook_key.ini',encoding='utf-8',mode='w')
        else:
            ConfigFile=codecs.open(unicode(os.environ['HOME'],'utf-8')+u'/.litebook_key.ini',encoding='utf-8',mode='w')
        config.write(ConfigFile)
        ConfigFile.close()
    except:
        dlg = wx.MessageDialog(None, u'写入按键配置文件错误！',u"错误！",wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False


def readConfigFile():
    """This function will read config from litebook.ini to a global dict var: GlobalConfig"""
    global GlobalConfig,OpenedFileList,BookMarkList,ThemeList,BookDB,MYOS
    config = MyConfig()
    try:
        if MYOS == 'Windows':
            ffp=codecs.open(os.environ['APPDATA'].decode('gbk')+u"\\litebook.ini",encoding='utf-8',mode='r')
        else:
            ffp=codecs.open(unicode(os.environ['HOME'],'utf-8')+u"/.litebook.ini",encoding='utf-8',mode='r')
        config.readfp(ffp)
    except:

        if MYOS == 'Windows':
            GlobalConfig['LastDir']=os.path.dirname(AnyToUnicode(os.path.abspath(sys.argv[0])))
            GlobalConfig['ConfigDir']=os.environ['APPDATA'].decode('gbk')
            GlobalConfig['IconDir']=os.path.dirname(AnyToUnicode(os.path.abspath(sys.argv[0])))+u"\\icon"
            GlobalConfig['ShareRoot']=os.environ['USERPROFILE'].decode('gbk')+u"\\litebook\\shared"
        else:
            GlobalConfig['LastDir']=os.environ['HOME'].decode('utf-8')
            GlobalConfig['IconDir']=cur_file_dir()+u"/icon"
            GlobalConfig['ConfigDir']=unicode(os.environ['HOME'],'utf-8')+u'/litebook/'
            GlobalConfig['ShareRoot']=unicode(os.environ['HOME'],'utf-8')+u"/litebook/shared"
        GlobalConfig['LTBNETRoot']=GlobalConfig['ShareRoot']
        GlobalConfig['LTBNETPort']=50200
        GlobalConfig['LTBNETID']='NONE'
        OpenedFileList=[]
        GlobalConfig['LastFile']=''
        GlobalConfig['LastZipFile']=''
        GlobalConfig['LastPos']=0
        BookMarkList=[]
        GlobalConfig['CurFont']=wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "")
        GlobalConfig['CurFColor']=(0,0,0,0)
        GlobalConfig['CurBColor']='LIGHT BLUE'
        GlobalConfig['LoadLastFile']=True
        GlobalConfig['AutoScrollInterval']=12000
        GlobalConfig['MaxBookDB']=50
        GlobalConfig['MaxOpenedFiles']=5
        GlobalConfig['RemindInterval']=60
        GlobalConfig['EnableSidebarPreview']=True
        GlobalConfig['VerCheckOnStartup']=True
        GlobalConfig['HashTitle']=False
        GlobalConfig['ShowAllFileInSidebar']=True
        GlobalConfig['HideToolbar']=False
        GlobalConfig['EnableESC']=False
        GlobalConfig['useproxy']=False
        GlobalConfig['proxyserver']=''
        GlobalConfig['proxyport']=0
        GlobalConfig['proxyuser']=''
        GlobalConfig['proxypass']=''
        GlobalConfig['DAUDF']=0
        GlobalConfig['lastwebsearchkeyword']=''
        GlobalConfig['defaultsavedir']=GlobalConfig['LastDir']
        GlobalConfig['numberofthreads']=10
        GlobalConfig['lastweb']=''
        GlobalConfig['backgroundimg']="default.jpg"
        GlobalConfig['backgroundimglayout']='tile'
        GlobalConfig['showmode']='paper'
        GlobalConfig['underline']=True
        GlobalConfig['underlinecolor']='GREY'
        GlobalConfig['underlinestyle']=wx.DOT
        GlobalConfig['pagemargin']=50
        GlobalConfig['bookmargin']=50
        GlobalConfig['vbookmargin']=50
        GlobalConfig['centralmargin']=20
        GlobalConfig['linespace']=5
        GlobalConfig['vlinespace']=15
        GlobalConfig['InstallDefaultConfig']=True

        GlobalConfig['RunWebserverAtStartup']=False
        GlobalConfig['ServerPort']=8000
        GlobalConfig['mDNS_interface']='AUTO'
        GlobalConfig['ToolSize']=32
        GlobalConfig['RunUPNPAtStartup']=True
        GlobalConfig['EnableLTBNET']=True

        return

    try:
        GlobalConfig['mDNS_interface']=config.get('settings','mDNS_interface')
    except:
        GlobalConfig['mDNS_interface']='AUTO'

    try:
        GlobalConfig['RunUPNPAtStartup']=config.getboolean('settings','RunUPNPAtStartup')
    except:
        GlobalConfig['RunUPNPAtStartup']=True

    try:
        GlobalConfig['EnableLTBNET']=config.getboolean('settings','EnableLTBNET')
    except:
        GlobalConfig['EnableLTBNET']=True

    try:
        GlobalConfig['RunWebserverAtStartup']=config.getboolean('settings','RunWebserverAtStartup')
    except:
        GlobalConfig['RunWebserverAtStartup']=False

    try:
        GlobalConfig['ServerPort']=config.getint('settings','ServerPort')
    except:
        GlobalConfig['ServerPort']=8000

    try:
        GlobalConfig['ToolSize']=config.getint('settings','toolsize')
    except:
        GlobalConfig['ToolSize']=32

    try:
        GlobalConfig['ShareRoot']=os.path.abspath(config.get('settings','ShareRoot'))
    except:
        if MYOS == 'Windows':
            GlobalConfig['ShareRoot']=os.environ['USERPROFILE'].decode('gbk')+u"\\litebook\\shared"
        else:
            GlobalConfig['ShareRoot']=unicode(os.environ['HOME'],'utf-8')+u"/litebook/shared"

    #if the path is not writeable, restore to default value
    if not os.access(GlobalConfig['ShareRoot'],os.W_OK | os.R_OK):
        if MYOS == 'Windows':
            GlobalConfig['ShareRoot']=os.environ['USERPROFILE'].decode('gbk')+u"\\litebook\\shared"
        else:
            GlobalConfig['ShareRoot']=unicode(os.environ['HOME'],'utf-8')+u"/litebook/shared"

    try:
        GlobalConfig['LTBNETRoot']=config.getboolean('settings','LTBNETRoot')
    except:
        GlobalConfig['LTBNETRoot']=GlobalConfig['ShareRoot']

    try:
        GlobalConfig['LTBNETPort']=config.getint('settings','LTBNETPort')
    except:
        GlobalConfig['LTBNETPort']=50200

    try:
        GlobalConfig['LTBNETID']=(config.get('settings','LTBNETID')).strip()
    except:
        GlobalConfig['LTBNETID']='NONE'

    try:
        GlobalConfig['InstallDefaultConfig']=config.getboolean('settings','installdefaultconfig')
    except:
        GlobalConfig['InstallDefaultConfig']=True



    try:
        GlobalConfig['lastweb']=config.get('settings','lastweb')
    except:
        GlobalConfig['lastweb']=''
    try:
        GlobalConfig['lastwebsearchkeyword']=config.get('settings','LastWebSearchKeyword')
    except:
        GlobalConfig['lastwebsearchkeyword']=''

    try:
        GlobalConfig['DAUDF']=config.getint('settings','DefaultActionUponDownloadFinished')
    except:
        GlobalConfig['DAUDF']=0

    try:
        GlobalConfig['EnableESC']=config.getboolean('settings','EnableESC')
    except:
        GlobalConfig['EnableESC']=False

    try:
        GlobalConfig['useproxy']=config.getboolean('settings','UseProxy')
    except:
        GlobalConfig['useproxy']=False


    try:
        GlobalConfig['proxyserver']=config.get('settings','ProxyServer')
    except:
        GlobalConfig['proxyserver']=''

    try:
        GlobalConfig['proxyport']=config.getint('settings','ProxyPort')
    except:
        GlobalConfig['proxyport']=0
    try:
        GlobalConfig['proxyuser']=config.get('settings','ProxyUser')
    except:
        GlobalConfig['proxyuser']=''
    try:
        GlobalConfig['proxypass']=config.get('settings','ProxyPass')
    except:
        GlobalConfig['proxypass']=''
    if MYOS != 'Windows':
        GlobalConfig['ConfigDir']=unicode(os.environ['HOME'],'utf-8')+u'/litebook/'
    else:
        GlobalConfig['ConfigDir']=os.environ['APPDATA'].decode('gbk')

    try:
        GlobalConfig['LastDir']=config.get('settings','LastDir')
    except:
        if MYOS == 'Windows':
            GlobalConfig['LastDir']=os.path.dirname(AnyToUnicode(os.path.abspath(sys.argv[0])))
        else:
            GlobalConfig['LastDir']=os.environ['HOME'].decode('utf-8')

    if GlobalConfig['LastDir'].strip()=='' or os.path.isdir(GlobalConfig['LastDir'])==False:
        if MYOS == 'Windows':
            GlobalConfig['LastDir']=os.path.dirname(AnyToUnicode(os.path.abspath(sys.argv[0])))
        else:
            GlobalConfig['LastDir']=os.environ['HOME'].decode('utf-8')

    if MYOS == 'Windows':
        GlobalConfig['IconDir']=os.path.dirname(AnyToUnicode(os.path.abspath(sys.argv[0])))+u"\\icon"
    else:
        GlobalConfig['IconDir']=cur_file_dir()+u"/icon"

    try:
        GlobalConfig['defaultsavedir']=config.get('settings','defaultsavedir')
    except:
        GlobalConfig['defaultsavedir']=GlobalConfig['LastDir']
    try:
        GlobalConfig['numberofthreads']=config.getint('settings','numberofthreads')
    except:
        GlobalConfig['numberofthreads']=10

    try:
        GlobalConfig['LoadLastFile']=config.getboolean('settings','LoadLastFile')
    except:
        GlobalConfig['LoadLastFile']=True


    try:
        GlobalConfig['AutoScrollInterval']=config.getfloat('settings','AutoScrollInterval')
    except:
        GlobalConfig['AutoScrollInterval']=12000

    try:
        GlobalConfig['MaxBookDB']=config.getint('settings','MaxBookDB')
    except:
        GlobalConfig['MaxBookDB']=50
    try:
        GlobalConfig['HideToolbar']=config.getboolean('settings','HideToolbar')
    except:
        GlobalConfig['HideToolbar']=False

    try:
        GlobalConfig['MaxOpenedFiles']=config.getint('settings','MaxOpenedFiles')
    except:
        GlobalConfig['MaxOpenedFiles']=5

    try:
        GlobalConfig['RemindInterval']=config.getint('settings','RemindInterval')
    except:
        GlobalConfig['RemindInterval']=60

    try:
        GlobalConfig['EnableSidebarPreview']=config.getboolean('settings','EnableSidebarPreview')
    except:
        GlobalConfig['EnableSidebarPreview']=True

    try:
        GlobalConfig['VerCheckOnStartup']=config.getboolean('settings','VerCheckOnStartup')
    except:
        GlobalConfig['VerCheckOnStartup']=True

    try:
        GlobalConfig['HashTitle']=config.getboolean('settings','HashTitle')
    except:
        GlobalConfig['HashTitle']=False

    try:
        GlobalConfig['ShowAllFileInSidebar']=config.getboolean('settings','ShowAllFileInSidebar')
    except:
        GlobalConfig['ShowAllFileInSidebar']=True

    try:
        t_flist=(config.items('LastOpenedFiles'))
        di={}
        for f in t_flist:
            di[f[0]]=f[1]
        flist=[]
        tmp_newl=di.keys()
        newl=[]
        for n  in tmp_newl:
            newl.append(int(n))
        newl.sort()
        for k in newl:
            flist.append((k,di[str(k)]))
        i=1
        for f in flist:
            if i>GlobalConfig['MaxOpenedFiles']: break
            else:
                i+=1
            if f[1].find(u'|')==-1:OpenedFileList.append({'file':f[1],'type':'normal','zfile':''})
            else:
                (zfile,filename)=f[1].split('|',2)
                OpenedFileList.append({'file':filename,'type':'zip','zfile':zfile})
    except:
        OpenedFileList=[]


    try:
        GlobalConfig['LastPos']=config.getint('LastPosition','pos')
        filename=config.get('LastPosition','lastfile')
        if filename.find(u"*")==-1:
            if filename.find(u"|")<>-1:
                GlobalConfig['LastZipFile']=filename.split(u"|")[0]
                GlobalConfig['LastFile']=filename.split(u"|")[1]
            else:
                GlobalConfig['LastFile']=filename
                GlobalConfig['LastZipFile']=''
        else:
             GlobalConfig['LastFile']=filename
             GlobalConfig['LastZipFile']=''
    except:
        GlobalConfig['LastFile']=''
        GlobalConfig['LastZipFile']=''
        GlobalConfig['LastPos']=0


    try:
        blist=(config.items('BookMark'))
        bookmark={}
        for bk in blist:
            bk_info=bk[1].split(u'?',2)
            BookMarkList.append({'filename':bk_info[0],'pos':int(bk_info[1]),'line':bk_info[2]})
    except:
        BookMarkList=[]


    #Read Font and Color
    try:
        ft_list=(config.items('Appearance'))
        gen_last=False
        for ft in ft_list:
            name=ft[0]
            f=ft[1].split('|')
            if name=='last':
                GlobalConfig['CurFont']=wx.Font(int(f[0]),int(f[1]),int(f[2]),int(f[3]),eval(f[4]),f[5],int(f[6]))
                GlobalConfig['CurFColor']=eval(f[7])
                GlobalConfig['CurBColor']=eval(f[8])
                if len(f)>9:
                    if f[9]<>'None':
                        GlobalConfig['backgroundimg']=f[9]
                    else:
                        GlobalConfig['backgroundimg']=None
                    GlobalConfig['showmode']=f[10]
                    GlobalConfig['backgroundimglayout']=f[11]
                    GlobalConfig['underline']=eval(f[12])
                    GlobalConfig['underlinestyle']=int(f[13])
                    GlobalConfig['underlinecolor']=str2list(f[14])
                    GlobalConfig['pagemargin']=int(f[15])
                    GlobalConfig['bookmargin']=int(f[16])
                    GlobalConfig['vbookmargin']=int(f[17])
                    GlobalConfig['centralmargin']=int(f[18])
                    GlobalConfig['linespace']=int(f[19])
                    GlobalConfig['vlinespace']=int(f[20])
                gen_last=True

            else:
                l={}
                l['font']=wx.Font(int(f[0]),int(f[1]),int(f[2]),int(f[3]),eval(f[4]),f[5],int(f[6]))
                l['fcolor']=eval(f[7])
                l['bcolor']=eval(f[8])
                if len(f)>9:
                    if f[9]<>'None':
                        l['backgroundimg']=f[9]
                    else:
                        l['backgroundimg']=None
                    l['showmode']=f[10]
                    l['backgroundimglayout']=f[11]
                    l['underline']=eval(f[12])
                    l['underlinestyle']=int(f[13])
                    l['underlinecolor']=str2list(f[14])
                    l['pagemargin']=int(f[15])
                    l['bookmargin']=int(f[16])
                    l['vbookmargin']=int(f[17])
                    l['centralmargin']=int(f[18])
                    l['linespace']=int(f[19])
                    l['vlinespace']=int(f[20])
                    if len(f)==22:
                        l['name']=f[21]
                    else:
                        l['name']=name
                    l['config']=ft[1]
                ThemeList.append(l)

    except:
        GlobalConfig['CurFont']=wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "")
        GlobalConfig['CurFColor']=(0,0,0,0)
        GlobalConfig['CurBColor']='LIGHT BLUE'
        GlobalConfig['backgroundimg']="default.jpg"
        GlobalConfig['backgroundimglayout']='tile'
        GlobalConfig['showmode']='paper'
        GlobalConfig['underline']=True
        GlobalConfig['underlinecolor']='GREY'
        GlobalConfig['underlinestyle']=wx.DOT
        GlobalConfig['pagemargin']=50
        GlobalConfig['bookmargin']=50
        GlobalConfig['vbookmargin']=50
        GlobalConfig['centralmargin']=20
        GlobalConfig['linespace']=5
        GlobalConfig['vlinespace']=15

    if gen_last==False:
        GlobalConfig['CurFont']=wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "")
        GlobalConfig['CurFColor']=(0,0,0,0)
        GlobalConfig['CurBColor']='LIGHT BLUE'
        GlobalConfig['backgroundimg']="default.jpg"
        GlobalConfig['backgroundimglayout']='tile'
        GlobalConfig['showmode']='paper'
        GlobalConfig['underline']=True
        GlobalConfig['underlinecolor']='GREY'
        GlobalConfig['underlinestyle']=wx.DOT
        GlobalConfig['pagemargin']=50
        GlobalConfig['bookmargin']=50
        GlobalConfig['vbookmargin']=50
        GlobalConfig['centralmargin']=20
        GlobalConfig['linespace']=5
        GlobalConfig['vlinespace']=15




    #Read BookDB
    try:
        bk_list=(config.items('BookDB'))
        for bk in bk_list:
            BookDB.append({'key':bk[0],'pos':int(bk[1])})
    except:
        BookDB=[]

    if MYOS != "Windows":
        if os.path.isdir(GlobalConfig['ConfigDir']+u'/litebook_tmp/')==False:
            cmd_line=[]
            cmd_line.append('rm')
            cmd_line.append('-f')
            cmd_line.append(GlobalConfig['ConfigDir']+u'/litebook_tmp')
            subprocess.call(cmd_line)
            cmd_line=[]
            cmd_line.append('mkdir')
            cmd_line.append('-p')
            cmd_line.append(GlobalConfig['ConfigDir']+u'/litebook_tmp')
            subprocess.call(cmd_line)
        else:
            tmp_list=glob.glob(GlobalConfig['ConfigDir']+u'/litebook_tmp/*')
            for f in tmp_list:
                try:
                    os.remove(f)
                except:
                    return


    #print os.path.abspath(GlobalConfig['IconDir'])




def writeConfigFile(lastpos):
    global GlobalConfig,OpenedFileList,load_zip,current_file,current_zip_file,OnScreenFileList,BookMarkList,ThemeList,BookDB
    # save settings
    config = MyConfig()
    config.add_section('settings')
    config.set('settings','LastDir',GlobalConfig['LastDir'])
    config.set('settings','LoadLastFile',unicode(GlobalConfig['LoadLastFile']))
    config.set('settings','AutoScrollInterval',unicode(GlobalConfig['AutoScrollInterval']))
    config.set('settings','MaxOpenedFiles',unicode(GlobalConfig['MaxOpenedFiles']))
    config.set('settings','MaxBookDB',unicode(GlobalConfig['MaxBookDB']))
    config.set('settings','RemindInterval',unicode(GlobalConfig['RemindInterval']))
    config.set('settings','EnableSidebarPreview',unicode(GlobalConfig['EnableSidebarPreview']))
    config.set('settings','VerCheckOnStartup',unicode(GlobalConfig['VerCheckOnStartup']))
    config.set('settings','HashTitle',unicode(True))
    config.set('settings','ShowAllFileInSidebar',unicode(GlobalConfig['ShowAllFileInSidebar']))
    config.set('settings','HideToolbar',unicode(GlobalConfig['HideToolbar']))
    config.set('settings','ProxyServer',unicode(GlobalConfig['proxyserver']))
    config.set('settings','EnableESC',unicode(GlobalConfig['EnableESC']))
    config.set('settings','ProxyPort',unicode(GlobalConfig['proxyport']))
    config.set('settings','ProxyUser',unicode(GlobalConfig['proxyuser']))
    config.set('settings','ProxyPass',unicode(GlobalConfig['proxypass']))
    config.set('settings','UseProxy',unicode(GlobalConfig['useproxy']))
    config.set('settings','DefaultActionUponDownloadFinished',unicode(GlobalConfig['DAUDF']))
    config.set('settings','LastWebSearchKeyword',unicode(GlobalConfig['lastwebsearchkeyword']))
    config.set('settings','defaultsavedir',unicode(GlobalConfig['defaultsavedir']))
    config.set('settings','numberofthreads',unicode(GlobalConfig['numberofthreads']))
    config.set('settings','lastweb',unicode(GlobalConfig['lastweb']))
    config.set('settings','installdefaultconfig',unicode(GlobalConfig['InstallDefaultConfig']))
    config.set('settings','ShareRoot',unicode(GlobalConfig['ShareRoot']))
    config.set('settings','LTBNETRoot',unicode(GlobalConfig['LTBNETRoot']))
    if 'kadp_ctrl' in GlobalConfig:
        (lport,nodeids)=GlobalConfig['kadp_ctrl'].getinfo(False)
        config.set('settings','LTBNETID',nodeids)
    config.set('settings','LTBNETPort',unicode(GlobalConfig['LTBNETPort']))
    config.set('settings','RunWebserverAtStartup',unicode(GlobalConfig['RunWebserverAtStartup']))
    config.set('settings','RunUPNPAtStartup',unicode(GlobalConfig['RunUPNPAtStartup']))
    config.set('settings','EnableLTBNET',unicode(GlobalConfig['EnableLTBNET']))
    config.set('settings','ServerPort',unicode(GlobalConfig['ServerPort']))
    config.set('settings','mDNS_interface',unicode(GlobalConfig['mDNS_interface']))
    config.set('settings','toolsize',unicode(GlobalConfig['ToolSize']))
    # save opened files
    config.add_section('LastOpenedFiles')
    i=0
    for f in OpenedFileList:
        if f['type']=='normal':config.set('LastOpenedFiles',unicode(i),f['file'])
        else:
            config.set('LastOpenedFiles',unicode(i),f['zfile']+u"|"+f['file'])
        i+=1
    # save last open files and postion
    config.add_section('LastPosition')
    config.set('LastPosition','pos',unicode(lastpos))
    if OnScreenFileList.__len__()==1: #if there are multiple files opening, then last postition can not be remembered
        if not load_zip or current_zip_file=='':
            config.set('LastPosition','lastfile',current_file)
        else:
            config.set('LastPosition','lastfile',current_zip_file+u"|"+current_file)
    else:
        tstr=u''
        for onscrfile in OnScreenFileList:
            tstr+=onscrfile[0]+u'*'
        tstr=tstr[:-1]
        config.set('LastPosition','lastfile',tstr)

    # save bookmarks
    config.add_section('BookMark')
    bookmark={}
    i=0
    for bookmark in BookMarkList:
        config.set('BookMark',unicode(i),bookmark['filename']+u'?'+unicode(bookmark['pos'])+u'?'+bookmark['line'])
        i+=1

    # Save font and color
    config.add_section('Appearance')
    ft=GlobalConfig['CurFont']
    save_str=unicode(ft.GetPointSize())+u'|'+unicode(ft.GetFamily())+u'|'+unicode(ft.GetStyle())+u'|'+unicode(ft.GetWeight())+u'|'+unicode(ft.GetUnderlined())+u'|'+ft.GetFaceName()+u'|'+unicode(ft.GetDefaultEncoding())+u'|'+unicode(GlobalConfig['CurFColor'])+u'|'+unicode(GlobalConfig['CurBColor'])
    save_str+=u'|'+unicode(GlobalConfig['backgroundimg'])
    save_str+=u'|'+unicode(GlobalConfig['showmode'])
    save_str+=u'|'+unicode(GlobalConfig['backgroundimglayout'])
    save_str+=u'|'+unicode(GlobalConfig['underline'])
    save_str+=u'|'+unicode(GlobalConfig['underlinestyle'])
    save_str+=u'|'+unicode(GlobalConfig['underlinecolor'])
    save_str+=u'|'+unicode(GlobalConfig['pagemargin'])
    save_str+=u'|'+unicode(GlobalConfig['bookmargin'])
    save_str+=u'|'+unicode(GlobalConfig['vbookmargin'])
    save_str+=u'|'+unicode(GlobalConfig['centralmargin'])
    save_str+=u'|'+unicode(GlobalConfig['linespace'])
    save_str+=u'|'+unicode(GlobalConfig['vlinespace'])

    config.set('Appearance','last',save_str)



    # Save Theme List
    for t in ThemeList:
        config.set('Appearance',t['name'],t['config'])

    # Save Book DB
    config.add_section('BookDB')
    for bk in BookDB:
        config.set('BookDB',unicode(bk['key']),unicode(bk['pos']))


    #write into litebook.ini
#    try:
    if MYOS == 'Windows':
        ConfigFile=codecs.open(os.environ['APPDATA'].decode('gbk')+u'\\litebook.ini',encoding='utf-8',mode='w')
    else:
        ConfigFile=codecs.open(unicode(os.environ['HOME'],'utf-8')+u'/.litebook.ini',encoding='utf-8',mode='w')
    config.write(ConfigFile)
    ConfigFile.close()
#    except:
#        dlg = wx.MessageDialog(None, u'写入配置文件错误！',u"错误！",wx.OK|wx.ICON_ERROR)
#        dlg.ShowModal()
#        dlg.Destroy()
#        return False
    return True






def UpdateOpenedFileList(filename,ftype,zfile=''):
    global OpenedFileList,GlobalConfig,SqlCon
    fi={}
    fi['type']=ftype
    fi['file']=filename
    fi['zfile']=zfile
    sqlstr="insert into book_history values ('"+unicode(filename)+"','"+ftype+"','"+unicode(zfile)+"',"+str(time.time())+");"
    try:
        SqlCon.execute(sqlstr)
        SqlCon.commit()
    except:
        return
    for x in OpenedFileList:
        if x['file']==filename:
            if x['type']=='normal':
                OpenedFileList.remove(x)
                OpenedFileList.insert(0,x)
                return
            else:
                if x['zfile']==zfile:
                    OpenedFileList.remove(x)
                    OpenedFileList.insert(0,x)
                    return
    OpenedFileList.insert(0,fi)
    if OpenedFileList.__len__()>GlobalConfig['MaxOpenedFiles']:
        i=0
        delta=OpenedFileList.__len__()-GlobalConfig['MaxOpenedFiles']
        while i<delta:
            OpenedFileList.pop()
            i+=1


def VersionCheck():
    """
    Get latest version from offical website
    return (internal_ver(float),text_ver(unicode),whatsnew(unicode)
    """
    try:
        f=urllib2.urlopen('http://code.google.com/p/litebook-project/wiki/LatestVer')
    except:
        return (False,False,False)
    iver=False
    tver=False
    wtsnew=False
    p1=re.compile('##########(.+)##########')
    p2=re.compile('----------(.+)----------')
    p3=re.compile('@@@@@@@@(.+)@@@@@@@@')
    for line in f:
        if line.find('##########') != -1:
            iver=float(p1.search(line).group(1))
            tver=p2.search(line).group(1).decode('utf-8')
            wtsnew=p3.search(line).group(1).decode('utf-8')
            wtsnew=wtsnew.replace('\\n','\n')
            break
    return (iver,tver,wtsnew)

##def VersionCheck(os):
##    try:
##        f=urllib.urlopen("http://code.google.com/p/litebook-project/wiki/UrlChecking")
##    except:
##        return False
##    for line in f:
##        if line.find('litebookwin')<>-1:
##            line=line.strip()
##            p=re.compile('<.*?>',re.S)
##            line=p.sub('',line)
##            info=line.split(' ')
##            found_1=False
##            found_2=False
##            for word in info:
##                if word.find('litebook'+os+'latestversion')<>-1:
##                    latest_ver=word.split('----')[1]
##                    found_1=True
##                if word.find('litebook'+os+'downloadurl')<>-1 :
##                    download_url=word.split('----')[1]
##                    found_2=True
##            if found_1==False or found_2==False:
##                f.close()
##                return False
##            else:
##                f.close()
##                return (latest_ver,'http://'+download_url)

def htmname2uni(htm):
    if htm[1]=='#':
        try:
            uc=unichr(int(htm[2:-1]))
            return uc
        except:
            return htm
    else:
        try:
            uc=unichr(htmlentitydefs.name2codepoint[htm[1:-1]])

            return uc
        except:
            return htm


def htm2txt(inf):
    """ filter out all html tags/JS script in input string, return a clean string"""
    f_str=inf
    #conver <p> to "\n"
    p=re.compile('<\s*p\s*>',re.I)
    f_str=p.sub('\n',f_str)


    #conver <br> to "\n"
    p=re.compile('<br.*?>',re.I)
    f_str=p.sub('\n',f_str)

    #conver "\n\r" to "\n"
    p=re.compile('\n\r',re.S)
    f_str=p.sub('\n',f_str)

    #this is used to remove protection of http://www.jjwxc.net
    p=re.compile('<font color=.*?>.*?</font>',re.I|re.S)
    f_str=p.sub('',f_str)

    #this is used to remove protection of HJSM
    p=re.compile("<\s*span\s*class='transparent'\s*>.*?<\s*/span\s*>",re.I|re.S)
    f_str=p.sub('',f_str)

    #remove <script xxxx>xxxx</script>
    p=re.compile('<script.*?>.*?</script>',re.I|re.S)
    f_str=p.sub('',f_str)
    #remove <style></style>
    p=re.compile('<style>.*?</style>',re.I|re.S)
    f_str=p.sub('',f_str)

    #remove <option>
    p=re.compile('<option.*?>.*?</option>',re.I|re.S)
    f_str=p.sub('',f_str)

    #remove <xxx>
    p=re.compile('<.*?>',re.S)
    f_str=p.sub('',f_str)

    #remove <!-- -->
    p=re.compile('<!--.*?-->',re.S)
    f_str=p.sub('',f_str)


    #conver &nbsp; into space
    p=re.compile('&nbsp;',re.I)
    f_str=p.sub(' ',f_str)

    #convert html codename like "&quot;" into real character
    p=re.compile("&#?\w{1,9};")
    str_list=p.findall(f_str)
    e_list=[]
    for x in str_list:
        if x not in e_list:
            e_list.append(x)
    for x in e_list:
        f_str=f_str.replace(x,htmname2uni(x))

    #convert more than 5 newline in a row into one newline
    f_str=f_str.replace("\r\n","\n")
    p=re.compile('\n{5,}')
    f_str=p.sub('\n',f_str)


    return f_str

def jarfile_decode(infile):
    global MYOS
    if not zipfile.is_zipfile(infile):
        return False
    zfile=zipfile.ZipFile(infile)
    if MYOS == 'Windows':
        cache_dir=os.environ['USERPROFILE'].decode('gbk')+u"\\litebook\\cache"
    else:
        cache_dir=unicode(os.environ['HOME'],'utf-8')+u"/litebook/cache"
    fp=open(infile,'rb')
    s=fp.read()
    m=hashlib.md5()
    m.update(s)
    c_name=m.hexdigest()
    if os.path.isfile(cache_dir+os.sep+c_name):
        ffp=codecs.open(cache_dir+os.sep+c_name,encoding='gbk',mode='r')
        try:
            s=ffp.read()
            if s<>'' and s<>None and s<>False:
                ffp.close()
                return s
            else:
                ffp.close()
        except:
            ffp.close()

    i=1
    content=u''
    while True:
        try:
            txt=zfile.read(str(i))
        except:
            break
        content+=txt.decode('utf-16','ignore')
        i+=1
    s=content
    s=s.encode('gbk','ignore')
    s=s.decode('gbk')
    CFile=codecs.open(cache_dir+os.sep+c_name,encoding='gbk',mode='w')
    CFile.write(s)
    CFile.close()
    return s

def epubfile_decode(infile):
    #decode epub file,return unicode
    global lb_hash
    if not zipfile.is_zipfile(infile):return False
    zfile=zipfile.ZipFile(infile)
    if MYOS == 'Windows':
        cache_dir=os.environ['USERPROFILE'].decode('gbk')+u"\\litebook\\cache"
    else:
        cache_dir=unicode(os.environ['HOME'],'utf-8')+u"/litebook/cache"
    fp=open(infile,'rb')
    s=fp.read()
    m=hashlib.md5()
    m.update(s)
    c_name=m.hexdigest()
    if os.path.isfile(cache_dir+os.sep+c_name):
        ffp=codecs.open(cache_dir+os.sep+c_name,encoding='gbk',mode='r')
        try:
            s=ffp.read()
            if s<>'' and s<>None and s<>False:
                ffp.close()
                return s
            else:
                ffp.close()
        except:
            ffp.close()



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
    #print "opfpath is ",opfpath
    opf_file = zfile.open(opfpath)
    context = etree.iterparse(opf_file)
    toc_path = None
    for action, elem in context:
        #print elem.tag,'---',elem.attrib
        attr_list={}
        for k,v in elem.attrib.items():
            attr_list[k.lower()]=v
        if 'media-type' in attr_list and attr_list['media-type'].lower()=='application/x-dtbncx+xml':
            toc_path = attr_list['href']
            break
    #print "toc_path is ",toc_path
    if toc_path == None:
        return False
    toc_path = os.path.dirname(opfpath)+'/'+toc_path
    #print "toc_path is ",toc_path
    if toc_path[0]=='/':
        toc_path=toc_path[1:]
    #print "toc_path is ",toc_path
    toc_file = zfile.open(toc_path)
    context = etree.iterparse(toc_file)
    clist=[]
    for action, elem in context:
        if elem.tag.split('}')[1].lower()=='content':
            attr_list={}
            for k,v in elem.attrib.items():
                attr_list[k.lower()]=v
            if 'src' in attr_list:
                clist.append(os.path.dirname(toc_path)+'/'+attr_list['src'])

##    i=1
    #print "clist is ",clist
    content=u''
##    clist=[]
##    for fname in zfile.namelist():
##        fext=os.path.splitext(fname)[1].lower()
##        if fext=='.ncx':
##            dirfile=fname
##        if fext in ['.xml','.html','.htm','.xhtml']:
##            if fname<>'META-INF/container.xml':
##                clist.append(fname)
##    fp=zfile.open(dirfile)
    toc_file = zfile.open(toc_path)
    instr=toc_file.read()
    gc=gcepub.GCEPUB(instr)
    gc.parser()
    rlist=gc.GetRList()
    clist.sort(cmp=cmp_filename)
    for fname in clist:
        if fname[0]=='/':
            fname=fname[1:]
        try:
            fp=zfile.open(fname,"r")
        except:break
        txt=fp.read()
        if not isinstance(fname,unicode):fname=fname.decode('gbk')
        try:
            chapter=rlist[os.path.basename(fname)]
        except:
            chapter='LiteBook'
        content+=lb_hash+chapter+'\n'
        try:
            content+=txt.decode('utf-8','ignore')
        except:
            content+=txt.decode('utf-16','ignore')


    s=htm2txt(content)
    s=s.encode('gbk','ignore')
    s=s.decode('gbk')
    CFile=codecs.open(cache_dir+os.sep+c_name,encoding='gbk',mode='w')
    CFile.write(s)
    CFile.close()
    return s


import struct
import zlib
import sys
def umd_field_decode(fp,pos):
    """" This function is to decode each field inside umd file"""
    fp.seek(pos)
    field_type_list={2:'title',3:'author',4:'year',5:'month',6:'day',7:'gender',8:'publisher',9:'vendor'}
    dtype=struct.unpack('H',fp.read(2))
    if dtype[0]<>11:
        field_type=field_type_list[dtype[0]]
        field_value=u''
        i=pos+3
        fp.seek(i,0)
        field_len=int(ord(fp.read(1)))
        field_len=field_len-5
        i+=1
        fp.seek(i,0)
        m=i
        while m<i+field_len:
            onechar=unichr(struct.unpack('H',fp.read(2))[0])
            field_value+=onechar
            m+=2
            fp.seek(m)
    else:
        field_type='content'
        pos+=4
        fp.seek(pos,0)
        field_len=struct.unpack('I',fp.read(4))[0]
        pos+=5
        fp.seek(pos,0)
##        print field_len
        chapter_type=struct.unpack('H',fp.read(2))[0]
##        print hex(chapter_type)

        pos+=4
        fp.seek(pos,0)
        r1=struct.unpack('I',fp.read(4))[0]
##        print "random-1 is "+str(hex(r1))

        pos+=5
        fp.seek(pos,0)
        r2=struct.unpack('I',fp.read(4))[0]
##        print "random-2 is "+str(hex(r2))

        pos+=4
        fp.seek(pos,0)
        offset_len=struct.unpack('I',fp.read(4))[0]-9
##        print "offset_len is "+str(offset_len)

        i=0
        pos+=4
        fp.seek(pos,0)
        chapter_offset=[]
        while i<offset_len:
            chapter_offset.append(struct.unpack('I',fp.read(4))[0])
            i+=4
            fp.seek(pos+i,0)
##        print "chapter offsets are:"
##        print chapter_offset

        pos+=offset_len+1
        fp.seek(pos,0)
        ch_t_type=struct.unpack('H',fp.read(2))[0]
##        print "ch_title_type is "+str(hex(ch_t_type))

        pos+=4
        fp.seek(pos,0)
        r3=struct.unpack('I',fp.read(4))[0]
##        print "random-3 is "+str(hex(r3))

        pos+=5
        fp.seek(pos,0)
        r4=struct.unpack('I',fp.read(4))[0]
##        print "random-4 is "+str(hex(r4))

        pos+=4
        fp.seek(pos,0)
        ch_title_len=struct.unpack('I',fp.read(4))[0]-9
        m=0
        pos+=4
        fp.seek(pos,0)
        while m<ch_title_len:
            t_len=ord(struct.unpack('c',fp.read(1))[0])
            pos+=1
            fp.seek(pos,0)
            n=pos
            t_val=u''
            while n<pos+t_len:
                onechar=unichr(struct.unpack('H',fp.read(2))[0])
                t_val+=onechar
                n+=2
                fp.seek(n)
##            print t_val.encode('gbk',"replace")
            m+=1+t_len
            pos+=t_len
            fp.seek(pos,0)
##        print "chapter title len is "+str(ch_title_len)

        fp.seek(pos,0)
        t_tag=fp.read(1)
        content=u''
        while t_tag=='$':
            pos+=5
            fp.seek(pos,0)
            content_len=struct.unpack(GetPint(),fp.read(4))[0]-9
##            print "content_len is:"+str(content_len)
            #content_len=192450

            pos+=4
            fp.seek(pos,0)
            x=content_len/65535
            y=content_len%65535
            n=0
            zstr=''
            while n<x:
                xx=fp.read(65535)
                zstr+=xx
                pos+=65535
                fp.seek(pos,0)
                n+=1
            zstr+=fp.read(y)
            pos+=y
            z_len=zstr.__len__()
##            print "z_len is "+str(z_len)
            ystr=zlib.decompress(zstr)
            y_len=ystr.__len__()
##            print "y_len is "+str(y_len)
            ystr=ystr.replace('\x29\x20','\n\x00')
            content+=ystr.decode('utf-16','ignore')
##            sys.exit()
##            n=0
##            while n<y_len:
##                onechar=unichr(struct.unpack('H',ystr[n:n+2])[0])
##                if onechar==u'\u2029':
##                    onechar=u'\n'
##                content+=onechar
##                n+=2
            #print content.encode('GBK','replace')
            fp.seek(pos,0)
            t_tag=fp.read(1)
##            print t_tag
        #print content.encode('GBK','ignore')

        fp.seek(pos,0)
        if fp.read(1)=='#':
            pos+=1
            fp.seek(pos,0)
            m_tag=struct.unpack('H',fp.read(2))[0]
        else:
            m_tag=0

        while m_tag<>0xc:
            if m_tag==0xf1:
                pos+=20
            else:
                if m_tag==0xa:
                    pos+=4
                    fp.seek(pos,0)
                    R1=struct.unpack('I',fp.read(4))[0]
##                    print "Random-1 is "+str(hex(R1))
                    pos+=4
                else:
                    if m_tag==0x81:
                        pos+=8
                        fp.seek(pos,0)
##                        print fp.read(1)
                        pos+=5
                        fp.seek(pos,0)
                        page_count=struct.unpack('I',fp.read(4))[0]-9
                        pos+=page_count+4

                    else:
                        if m_tag==0x87:
                            pos+=15
                            fp.seek(pos,0)
                            offset_len=struct.unpack('I',fp.read(4))[0]-9
##                            print "offset_len is "+str(offset_len)
##                            i=0
                            pos+=4+offset_len
##                            fp.seek(pos,0)
##                            chapter_offset=[]
##                            while i<offset_len:
##                                chapter_offset.append(struct.unpack('I',fp.read(4))[0])
##                                i+=4
##                                fp.seek(pos+i,0)
##                            print "chapter offsets are:"
##                            print chapter_offset

                        else:
                            if m_tag==0x82:
                                pos+=14
                                fp.seek(pos,0)
                                cover_len=struct.unpack(GetPint(),fp.read(4))[0]-9
                                pos+=cover_len+4
                            else:
                                if m_tag==0xb:
                                    pos+=8
                                else:
                                    fp.seek(pos,0)
                                    t_tag=fp.read(1)
                                    while t_tag=='$':
                                         pos+=5
                                         fp.seek(pos,0)
                                         content_len=struct.unpack(GetPint(),fp.read(4))[0]-9
        ##                                 print "content_len is:"+str(content_len)
                                         pos+=4
                                         fp.seek(pos,0)
                                         x=content_len/65535
                                         y=content_len%65535
                                         n=0
                                         zstr=''
                                         while n<x:
                                             xx=fp.read(65535)
                                             zstr+=xx
                                             pos+=65535
                                             fp.seek(pos,0)
                                             n+=1
                                         zstr+=fp.read(y)
                                         pos+=y
                                         z_len=zstr.__len__()
        ##                                 print "z_len is "+str(z_len)
                                         ystr=zlib.decompress(zstr)
                                         y_len=ystr.__len__()
        ##                                 print "y_len is "+str(y_len)
                                         ystr=ystr.replace('\x29\x20','\n\x00')
                                         content+=ystr.decode('utf-16','ignore')
                                         fp.seek(pos,0)
                                         t_tag=fp.read(1)
        ##                                 print t_tag

                    #print content.encode('GBK','ignore')
            fp.seek(pos,0)
            xxx=fp.read(1)
            if xxx=='#':
                pos+=1
                fp.seek(pos,0)
                m_tag=struct.unpack('H',fp.read(2))[0]
            else:
                m_tag=0
##        print type(content)
        return ('Content',content,pos,True)

    return (field_type,field_value,m,False)





def umd_decode(infile):
    """This function will decode a umd file, and return a dict include all the fields"""
    umdinfo={}
    f=open(infile,'rb')
    bytes=f.read(4)
    tag=struct.unpack('cccc',bytes)
    if tag<>('\x89', '\x9b', '\x9a', '\xde'): return False # check if the file is the umd file
    f.seek(9)
    ftype=ord(f.read(1))
    if ftype<>0x1: return False #0x1 means txt,0x2 mean picture
    (u_type,u_value,pos,end)=umd_field_decode(f,13)
    umdinfo[u_type]=u_value
    i=1
    end=False
    while end<>True:
        (u_type,u_value,pos,end)=umd_field_decode(f,pos+1)
        umdinfo[u_type]=u_value
##    print umdinfo['author']
##    print umdinfo['title']
##    print umdinfo['publisher']
##    print umdinfo['vendor']
    return umdinfo


def HumanSize(ffsize):
    fsize=float(ffsize)
    if fsize>=1000000000.0:
        r=float(fsize)/1000000000.0
        return '%(#).2f' % {'#':r}+' GB'
    else:
        if fsize>=1000000.0:
            r=float(fsize)/1000000.0
            return '%(#).2f' % {'#':r}+' MB'
        else:
            if fsize>=1000.0:
                r=float(fsize)/1000.0
                return '%(#).2f' % {'#':r}+' KB'
            else:
                return '< 1KB'


def unrar(rfile,filename):
    ###This funtion will use unrar command line to extract file from rar file"""
    global GlobalConfig

    cmd_line=[]
    cmd_line.append(u"unrar")
    cmd_line.append('x')
    cmd_line.append('-y')
    cmd_line.append('-inul')
    cmd_line.append(rfile)
    cmd_line.append(filename)
    cmd_line.append(GlobalConfig['ConfigDir']+"/litebook_tmp/")
    if subprocess.call(cmd_line)==0:
        if isinstance(filename,str):
            filename=filename.decode('gbk')

        fp=open(GlobalConfig['ConfigDir']+u"/litebook_tmp/"+filename,'r')
        txt=fp.read()
        fp.close()
        return txt
    else:
        return False


def ch2num(ch):
    if not isinstance(ch,unicode):
        ch=ch.decode("gbk")
    chnum_str=u'(零|一|二|三|四|五|六|七|八|九|十|百|千|万|0|1|2|3|4|5|6|7|8|9)'
    ch_ten_str=u'(十|百|千|万)'
    ch_ten_dict={u'十':u'0',u'百':u'00',u'千':u'000',u'万':u'0000',}
    ch_dict={u'零':u'0',u'一':u'1',u'二':u'2',u'三':u'3',u'四':u'4',u'五':u'5',u'六':u'6',u'七':u'7',u'八':u'8',u'九':u'9',}
    p=re.compile(u'第'+chnum_str+u'+(章|节|部|卷)',re.L|re.U)
    m_list=p.finditer(ch)
#    mid_str=m.string[m.start():m.end()]
    rr=[]
    #print m_list
    for pr in m_list:
        mid_str=pr.string[pr.start():pr.end()]
        mid_str=mid_str[1:-1]
        if mid_str[0]==u'十':
            if len(mid_str)<>1:
                mid_str=mid_str.replace(u'十',u'1',1)
            else:
                rr.append(10)
                break
        if mid_str[-1:]==u'万':
            try:
                mid_str+=ch_ten_dict[mid_str[-2:-1]]+u'0000'
            except:
                mid_str+=u'0000'
        else:
            try:
                mid_str+=ch_ten_dict[mid_str[-1:]]
            except:
                pass
        p=re.compile(ch_ten_str,re.L|re.U)
        mid_str=p.sub('',mid_str)
        for key,val in ch_dict.items():
            mid_str=mid_str.replace(key,val)
        rr.append(long(mid_str))
    i=0
    x=0
    while i<len(rr):
       x+=rr[i]*math.pow(10,5*(3-i))
       i+=1
    return long(x)


class ZipFileDialog(wx.Dialog):
    """ZIP/RAR file list dialog, using TreeCtrl"""
    selected_files=[]
    openmethod='load'
    def __init__(self,parent,zipfilename):
        #begin wxGlade: ZipFileDialog.__init__
        #kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        self.file_icon_list={}
        self.selected_files=[]
        wx.Dialog.__init__(self, parent,-1,'')
        self.tree_ctrl_1 = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_MULTIPLE|wx.TR_MULTIPLE|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.button_2 = wx.Button(self, -1, u"打开")
        self.button_3 = wx.Button(self, -1, u"取消")
        self.button_4 = wx.Button(self, -1, u"添加")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnOpen, self.tree_ctrl_1)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_3)
        self.Bind(wx.EVT_BUTTON, self.OnAppend, self.button_4)
        # end wxGlade
        self.tree_ctrl_1.Bind(wx.EVT_CHAR,self.OnKey)
        self.Bind(wx.EVT_ACTIVATE,self.OnWinActive)
        root=self.tree_ctrl_1.AddRoot(zipfilename)
        self.tree_ctrl_1.SetItemImage(root,0,wx.TreeItemIcon_Normal)
        if os.path.splitext(zipfilename)[1].lower()== ".zip":
            try:
                zfile=zipfile.ZipFile(zipfilename)
            except:
                dlg = wx.MessageDialog(None, zipfilename+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            for zz in zfile.namelist():
                self.AddLeaf(zz,self.tree_ctrl_1)
        else:
            try:
                rfile=rarfile.RarFile(zipfilename)
            except:
                dlg = wx.MessageDialog(None, zipfilename+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            rarfile_list=[]
            rname_list=[]
            for line in rfile.namelist():
                line=line.replace('\\','/')
                #line=line.decode('GBK')
#                if isinstance(line,unicode):
#                    line=line.encode('gbk')
                if rfile.getinfo(line).isdir():
#                    if isinstance(line,str):
#                        line=line.decode('gbk')
                    line+="/"
                rarfile_list.append((line.replace("plugi","/")))
            for rr in rarfile_list:
                self.AddLeaf(rr,self.tree_ctrl_1)
        self.image_list=wx.ImageList(16,16,mask=False,initialCount=5)
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/ClosedFolder.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["closedfolder"]=0
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/OpenFolder.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["openfolder"]=1
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/file.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["file"]=2
        self.tree_ctrl_1.SetImageList(self.image_list)





    def __set_properties(self):
        # begin wxGlade: ZipFileDialog.__set_properties
        self.SetTitle(u"打开压缩包中的文件")
        self.SetSize((400, 400))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ZipFileDialog.__do_layout
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(self.tree_ctrl_1, 1, wx.EXPAND, 0)
        sizer_6.Add((20, 20), 1, 0, 0)
        sizer_6.Add(self.button_4, 0, 0, 0)
        sizer_6.Add((20, 20), 1, 0, 0)
        sizer_6.Add(self.button_2, 0, 0, 0)
        sizer_6.Add((20, 20), 1, 0, 0)
        sizer_6.Add(self.button_3, 0, 0, 0)
        sizer_6.Add((20, 20), 1, 0, 0)
        sizer_5.Add(sizer_6, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_5)
        self.Layout()
        # end wxGlade


    def OnOpen(self, event): # wxGlade: ZipFileDialog.<event_handler>
        item_selected=self.tree_ctrl_1.GetSelections()
        for item in item_selected:
            if self.tree_ctrl_1.GetChildrenCount(item)==0:
                if isinstance(self.tree_ctrl_1.GetPyData(item),str):
                    s_item=self.tree_ctrl_1.GetPyData(item).decode('gbk')
                else:
                    s_item=self.tree_ctrl_1.GetPyData(item)
                self.selected_files.append(s_item)
        if self.selected_files==[]:
            event.Skip()
            return False
        else:
            self.Close()


    def OnCancell(self, event): # wxGlade: ZipFileDialog.<event_handler>
        self.Destroy()

    def OnAppend(self, event): # wxGlade: ZipFileDialog.<event_handler>
        item_selected=self.tree_ctrl_1.GetSelections()
        for item in item_selected:
            full_name=''
            while item<>self.tree_ctrl_1.GetRootItem():
                full_name=self.tree_ctrl_1.GetItemText(item)+full_name
                item=self.tree_ctrl_1.GetItemParent(item)
                self.selected_files.append(full_name)
        self.openmethod='append'
        self.Close()




    def AddLeaf(self,tree_item,tree):
        try:
            tree_item=tree_item.decode("gbk")
        except:
            pass
        i_list=tree_item.split(u"/")
        field_count=len(i_list)
        m=1
        if i_list[len(i_list)-1]=='':
            i_list=i_list[:-1]
        rt=tree.GetRootItem()
        for i in i_list:
            item,cookie=tree.GetFirstChild(rt)
            found_r=False
            while item:
                if tree.GetItemText(item)==i:
                    rt=item
                    found_r=True
                    break
                else:
                    item,cookie=tree.GetNextChild(rt,cookie)
            if not found_r:
                child_id=tree.AppendItem(rt,i)
                if m<>field_count:
                    tree.SetItemImage(child_id,1,wx.TreeItemIcon_Normal)
                else:
                    tree.SetItemImage(child_id,2,wx.TreeItemIcon_Normal)
                    tree.SetPyData(child_id,tree_item)

                rt=child_id
            m+=1
        return

    def OnKey(self,event):
        key=event.GetKeyCode()
        if key==wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()


    def OnWinActive(self,event):
        if event.GetActive():self.tree_ctrl_1.SetFocus()


class MyFrame(wx.Frame,wx.lib.mixins.listctrl.ColumnSorterMixin):
    buff=u''
    currentTextAttr=wx.TextAttr()
    search_str=''
    search_flg=1
    last_search_pos=0
    showfullscr=False
    autoscroll=False
    Clock=True
    current_pos=0
    last_pos=0
    slider=None
    mousedelta=0
    last_mouse_event=None
    UpdateSidebar=False
    SidebarPos=300 # inital postion value for dir sidebar
    Formated=False
    cur_catalog=None
    func_list={
    u'向上翻行':'self.text_ctrl_1.ScrollLine(-1)',
    u'向下翻行':'self.text_ctrl_1.ScrollLine(1)',
    u'向上翻页':'self.text_ctrl_1.ScrollP(-1)',
    u'向下翻页':'self.text_ctrl_1.ScrollP(1)',
    u'向上翻半页':'self.text_ctrl_1.ScrollHalfP(-1)',
    u'向下翻半页':'self.text_ctrl_1.ScrollHalfP(1)',
    u'前进10%':'self.text_ctrl_1.ScrollPercent(10,1)',
    u'后退10%':'self.text_ctrl_1.ScrollPercent(10,-1)',
    u'前进1%':'self.text_ctrl_1.ScrollPercent(1,1)',
    u'后退1%':'self.text_ctrl_1.ScrollPercent(1,-1)',

    u'跳到首页':'self.text_ctrl_1.ScrollTop()',
    u'跳到结尾':'self.text_ctrl_1.ScrollBottom()',
    u'文件列表':'self.Menu101(None)',
    u'打开文件':'self.Menu102(None)',
    u'另存为':'self.Menu108(None)',
    u'关闭':'self.Menu103(None)',
    u'上一个文件':'self.Menu104(None)',
    u'下一个文件':'self.Menu105(None)',
    u'搜索小说网站':'self.Menu110(None)',
    u'重新载入插件':'self.Menu111(None)',
    u'选项':'self.Menu106(None)',
    u'退出':'self.Menu107(None)',
    u'拷贝':'self.Menu202(None)',
    u'查找':'self.Menu203(None)',
    u'替换':'self.Menu206(None)',
    u'查找下一个':'self.Menu204(None)',
    u'查找上一个':'self.Menu205(None)',
    u'纸张显示模式':'self.Menu601(None)',
    u'书本显示模式':'self.Menu602(None)',
    u'竖排书本显示模式':'self.Menu603(None)',
    u'显示工具栏':'self.Menu501(None)',
    u'放大工具栏':'self.Menu512(None)',
    u'缩小工具栏':'self.Menu511(None)',
    u'显示目录':'self.Menu509(None)',
    u'全屏显示':'self.Menu503(None)',
    u'显示文件侧边栏':'self.Menu502(None)',
    u'自动翻页':'self.Menu505(None)',
    u'智能分段':'self.Tool44(None)',
    u'添加到收藏夹':'self.Menu301(None)',
    u'整理收藏夹':'self.Menu302(None)',
    u'简明帮助':'self.Menu401(None)',
    u'版本更新内容':'self.Menu404(None)',
    u'检查更新':'self.Menu403(None)',
    u'关于':'self.Menu402(None)',
    u'过滤HTML标记':'self.Tool41(None)',
    u'切换为简体字':'self.Tool42(None)',
    u'切换为繁体字':'self.Tool43(None)',
    u'显示进度条':'self.ShowSlider()',
    u'增大字体':'self.ChangeFontSize(1)',
    u'减小字体':'self.ChangeFontSize(-1)',
    u'清空缓存':'self.Menu112()',
    u'最小化':'self.OnESC(None)',
    u'生成EPUB文件':'self.Menu704()',
    u'启用WEB服务器':'self.Menu705()',
    u'检测端口是否开启':'self.Menu706()',
    u'使用UPNP添加端口映射':'self.Menu707()',
    u'显示章节侧边栏':'self.Menu510(None)',
    u'搜索LTBNET':'self.Menu113(None)',
    u'下载管理器':'self.Menu114(None)',
    u'管理订阅':'self.Menu115(None)',
    }

    def __init__(self,parent,openfile=None):
        global GlobalConfig, MYOS
        self.buff=u''
        self.currentLine=0
        self.toolbar_visable=True
        self.FileHistoryDiag=None
        self.cnsort=cnsort()
        self.last_search_pos=False
        self.title_str=u'litebook 轻巧读书'

        # begin wxGlade: MyFrame.__init__
        #kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self,parent,-1)
        #display the splash
        bitmap = wx.Bitmap(GlobalConfig['IconDir']+"/l2_splash.gif", wx.BITMAP_TYPE_ANY)
        splash_frame = wx.SplashScreen(bitmap,wx.SPLASH_NO_TIMEOUT |wx.SPLASH_CENTRE_ON_SCREEN,3000,parent=self )


        self.window_1 = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.window_1_pane_2 = wx.Panel(self.window_1, -1)
        self.window_1_pane_1 = wx.Panel(self.window_1, -1)
        self.window_1_pane_mulu = wx.Panel(self.window_1, -1)
        self.list_ctrl_1 = wx.ListCtrl(self.window_1_pane_1, -1, style=wx.LC_REPORT)
        self.list_ctrl_mulu = wx.ListCtrl(self.window_1_pane_mulu, -1, style=wx.LC_REPORT)
        self.list_ctrl_mulu.InsertColumn(0,u"章节名称",width=-1)
        self.text_ctrl_1 = liteview.LiteView(self.window_1_pane_2)
        self.window_1_pane_mulu.Hide()
        self.window_1_pane_1.Hide()

        #set droptarget
        dt = FileDrop(self)
        self.text_ctrl_1.SetDropTarget(dt)

        #load apperance

        if GlobalConfig['backgroundimg']<>'' and GlobalConfig['backgroundimg']<>None:
            self.text_ctrl_1.SetBackgroundColour(GlobalConfig['CurBColor'])
            self.text_ctrl_1.SetImgBackground(GlobalConfig['backgroundimg'],GlobalConfig['backgroundimglayout'])
        else:
            self.text_ctrl_1.SetBackgroundColour(GlobalConfig['CurBColor'])
        self.text_ctrl_1.SetFColor(GlobalConfig['CurFColor'])
        self.text_ctrl_1.SetFont(GlobalConfig['CurFont'])
        self.text_ctrl_1.SetUnderline(GlobalConfig['underline'],GlobalConfig['underlinestyle'],GlobalConfig['underlinecolor'])
        self.text_ctrl_1.SetSpace(GlobalConfig['pagemargin'],GlobalConfig['bookmargin'],GlobalConfig['vbookmargin'],GlobalConfig['centralmargin'],GlobalConfig['linespace'],GlobalConfig['vlinespace'])

        self.text_ctrl_2 = wx.TextCtrl(self.window_1_pane_1, -1, "",style=wx.TE_PROCESS_TAB|wx.TE_PROCESS_ENTER)


        # Menu Bar
        self.frame_1_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(101, u"文件列表(&L)"+KeyMenuList[u'文件列表'], u"打开文件列表", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(102, u"打开文件(&O)"+KeyMenuList[u'打开文件'], u"打开文件", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(108, u"另存为...(&S)"+KeyMenuList[u'另存为'], u"打开文件", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(103, u"关闭(&C)"+KeyMenuList[u'关闭'], u"关闭当前文件", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu_sub = wx.Menu()
        wxglade_tmp_menu_sub.Append(104, u"上一个文件(&P)"+KeyMenuList[u'上一个文件'], u"打开上一个文件", wx.ITEM_NORMAL)
        wxglade_tmp_menu_sub.Append(105, u"下一个文件(&N)"+KeyMenuList[u'下一个文件'], u"打开下一个文件", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendMenu(wx.NewId(), u"按文件序号顺序打开", wxglade_tmp_menu_sub, "")
        wxglade_tmp_menu_sub = wx.Menu()
        i=1000
        for f in OpenedFileList:
            i+=1
            f['MenuID']=i
            if f['type']=='normal':wxglade_tmp_menu_sub.Append(i,f['file'],f['file'],wx.ITEM_NORMAL)
            else:wxglade_tmp_menu_sub.Append(i,f['zfile']+u'|'+f['file'],f['file'],wx.ITEM_NORMAL)
            self.Bind(wx.EVT_MENU, self.OpenLastFile, id=i)
        self.LastFileMenu=wxglade_tmp_menu_sub
        wxglade_tmp_menu.AppendMenu(wx.NewId(), u"曾经打开的文件", wxglade_tmp_menu_sub, "")
        wxglade_tmp_menu.Append(109, u"以往打开文件历史", u"显示曾经打开的所有文件列表", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(110, u"搜索小说网站(&S)"+KeyMenuList[u'搜索小说网站'], u"搜索小说网站", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(115, u"管理订阅"+KeyMenuList[u'管理订阅'], u"管理订阅", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(111, u"重新载入插件"+KeyMenuList[u'重新载入插件'], u"重新载入插件", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()

        wxglade_tmp_menu.Append(113, u"搜索LTBNET"+KeyMenuList[u'搜索LTBNET'], u"搜索LTBNET", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(114, u"下载管理器"+KeyMenuList[u'下载管理器'], u"下载管理器", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(112, u"清空缓存(&O)"+KeyMenuList[u'清空缓存'], u"清空缓存目录", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(106, u"选项(&O)"+KeyMenuList[u'选项'], u"程序的设置选项", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(107, u"退出(&X)"+KeyMenuList[u'退出'], u"退出本程序", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, u"文件(&F)")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(202, u"拷贝(&C)"+KeyMenuList[u'拷贝'], u"将选中的内容拷贝到剪贴板", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(203, u"查找(&S)"+KeyMenuList[u'查找'], u"在打开的文件中查找", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(204, u"查找下一个(&N)"+KeyMenuList[u'查找下一个'], u"查找下一个", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(205, u"查找上一个(&N)"+KeyMenuList[u'查找上一个'], u"查找上一个", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(206, u"替换(&R)"+KeyMenuList[u'替换'], u"在打开的文件中查找并替换", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, u"查找(&S)")
        wxglade_tmp_menu = wx.Menu()
        self.ViewMenu=wxglade_tmp_menu
        wxglade_tmp_menu.AppendRadioItem(601,u'纸张显示模式'+KeyMenuList[u'纸张显示模式'],u'设置当前显示模式为纸张')
        wxglade_tmp_menu.AppendRadioItem(602,u'书本显示模式'+KeyMenuList[u'书本显示模式'],u'设置当前显示模式为书本')
        wxglade_tmp_menu.AppendRadioItem(603,u'竖排书本显示模式'+KeyMenuList[u'竖排书本显示模式'],u'设置当前显示模式为竖排书本')
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(507, u"增大字体"+KeyMenuList[u'增大字体'], u"增大字体", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(508, u"减小字体"+KeyMenuList[u'减小字体'], u"减小字体", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(501, u"显示工具栏"+KeyMenuList[u'显示工具栏'], u"是否显示工具栏", wx.ITEM_CHECK)
        wxglade_tmp_menu.Append(511, u"缩小工具栏"+KeyMenuList[u'缩小工具栏'], u"缩小工具栏", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(512, u"放大工具栏"+KeyMenuList[u'放大工具栏'], u"放大工具栏", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(503, u"全屏显示"+KeyMenuList[u'全屏显示'], u"全屏显示", wx.ITEM_CHECK)
        wxglade_tmp_menu.Append(502, u"显示文件侧边栏"+KeyMenuList[u'显示文件侧边栏'], u"是否显示文件侧边栏", wx.ITEM_CHECK)
        wxglade_tmp_menu.Append(510, u"显示章节侧边栏"+KeyMenuList[u'显示章节侧边栏'], u"是否显示章节侧边栏", wx.ITEM_CHECK)
        wxglade_tmp_menu.Append(505, u"自动翻页"+KeyMenuList[u'自动翻页'], u"是否自动翻页", wx.ITEM_CHECK)
        wxglade_tmp_menu.Append(506, u"显示进度条"+KeyMenuList[u'显示进度条'], u"显示进度条", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(509, u"显示章节"+KeyMenuList[u'显示目录'], u"显示章节", wx.ITEM_NORMAL)
        if GlobalConfig['HideToolbar']:
            wxglade_tmp_menu.Check(501,True)

        self.SidebarMenu=wxglade_tmp_menu
        wxglade_tmp_menu.Append(504, u"智能分段"+KeyMenuList[u'智能分段'], u"智能分段", wx.ITEM_CHECK)
        self.FormatMenu=wxglade_tmp_menu
        self.frame_1_menubar.Append(wxglade_tmp_menu, u"视图(&T)")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(301, u"添加到收藏夹(&A)"+KeyMenuList[u'添加到收藏夹'], u"将当前阅读位置添加到收藏夹", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(302, u"整理收藏夹(&M)"+KeyMenuList[u'整理收藏夹'], u"整理收藏夹", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, u"收藏(&V)")

        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(701, u"过滤HTML标签"+KeyMenuList[u'过滤HTML标记'], u"过滤HTML标签", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(702, u"简体转繁体"+KeyMenuList[u'切换为繁体字'], u"简体转繁体", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(703, u"繁体转简体"+KeyMenuList[u'切换为简体字'], u"繁体转简体", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(704, u"生成EPUB文件"+KeyMenuList[u'生成EPUB文件'], u"生成EPUB文件", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(705, u"启用WEB服务器"+KeyMenuList[u'启用WEB服务器'], u"是否启用WEB服务器", wx.ITEM_CHECK)
        wxglade_tmp_menu.Append(706, u'检测端口是否开启'+KeyMenuList[u'检测端口是否开启'], u'检测端口是否开启', wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(707, u'使用UPNP添加端口映射'+KeyMenuList[u'使用UPNP添加端口映射'], u'使用UPNP添加端口映射', wx.ITEM_NORMAL)

        self.frame_1_menubar.Append(wxglade_tmp_menu, u"工具(&T)")


        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(401, u"简明帮助(&B)"+KeyMenuList[u'简明帮助'], u"简明帮助", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(404, u"版本更新内容"+KeyMenuList[u'版本更新内容'], u"版本更新内容", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(403, u"检查更新(&C)"+KeyMenuList[u'检查更新'], u"在线检查是否有更新的版本", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(402, u"关于(&A)"+KeyMenuList[u'关于'], u"关于本程序", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, u"帮助(&H)")
        self.SetMenuBar(self.frame_1_menubar)
        # Menu Bar end
        self.frame_1_statusbar = self.CreateStatusBar(4, 0)

        # Tool Bar
        self.ResetTool((GlobalConfig['ToolSize'],GlobalConfig['ToolSize']))

        # Tool Bar end
        #self.text_ctrl_1 = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)


        self.Bind(wx.EVT_MENU, self.Menu101, id=101)
        self.Bind(wx.EVT_MENU, self.Menu102, id=102)
        self.Bind(wx.EVT_MENU, self.Menu103, id=103)
        self.Bind(wx.EVT_MENU, self.Menu104, id=104)
        self.Bind(wx.EVT_MENU, self.Menu105, id=105)
        self.Bind(wx.EVT_MENU, self.Menu106, id=106)
        self.Bind(wx.EVT_MENU, self.Menu107, id=107)
        self.Bind(wx.EVT_MENU, self.Menu108, id=108)
        self.Bind(wx.EVT_MENU, self.Menu109, id=109)
        self.Bind(wx.EVT_MENU, self.Menu110, id=110)
        self.Bind(wx.EVT_MENU, self.Menu111, id=111)
        self.Bind(wx.EVT_MENU, self.Menu112, id=112)
        self.Bind(wx.EVT_MENU, self.Menu113, id=113)
        self.Bind(wx.EVT_MENU, self.Menu114, id=114)
        self.Bind(wx.EVT_MENU, self.Menu115, id=115)
        self.Bind(wx.EVT_MENU, self.Menu202, id=202)
        self.Bind(wx.EVT_MENU, self.Menu203, id=203)
        self.Bind(wx.EVT_MENU, self.Menu204, id=204)
        self.Bind(wx.EVT_MENU, self.Menu205, id=205)
        self.Bind(wx.EVT_MENU, self.Menu206, id=206)
        self.Bind(wx.EVT_MENU, self.Menu301, id=301)
        self.Bind(wx.EVT_MENU, self.Menu302, id=302)
        self.Bind(wx.EVT_MENU, self.Menu401, id=401)
        self.Bind(wx.EVT_MENU, self.Menu402, id=402)
        self.Bind(wx.EVT_MENU, self.Menu403, id=403)
        self.Bind(wx.EVT_MENU, self.Menu404, id=404)
        self.Bind(wx.EVT_MENU, self.Menu501, id=501)
        self.Bind(wx.EVT_MENU, self.Menu502, id=502)
        self.Bind(wx.EVT_MENU, self.Menu503, id=503)
        self.Bind(wx.EVT_MENU, self.Menu505, id=505)
        self.Bind(wx.EVT_MENU, self.ShowSlider, id=506)
        self.Bind(wx.EVT_MENU, self.Menu507, id=507)
        self.Bind(wx.EVT_MENU, self.Menu508, id=508)
        self.Bind(wx.EVT_MENU, self.Menu509, id=509)
        self.Bind(wx.EVT_MENU, self.Menu510, id=510)
        self.Bind(wx.EVT_MENU, self.Menu511, id=511)
        self.Bind(wx.EVT_MENU, self.Menu512, id=512)
        self.Bind(wx.EVT_MENU, self.Menu601, id=601)
        self.Bind(wx.EVT_MENU, self.Menu602, id=602)
        self.Bind(wx.EVT_MENU, self.Menu603, id=603)
        self.Bind(wx.EVT_MENU, self.Menu704, id=704)
        self.Bind(wx.EVT_MENU, self.Menu705, id=705)
        self.Bind(wx.EVT_MENU, self.Menu706, id=706)
        self.Bind(wx.EVT_MENU, self.Menu707, id=707)
        self.Bind(wx.EVT_MENU, self.Tool41, id=701)
        self.Bind(wx.EVT_MENU, self.Tool43, id=702)
        self.Bind(wx.EVT_MENU, self.Tool42, id=703)


        self.Bind(wx.EVT_MENU, self.Tool44, id=504)
        self.Bind(wx.EVT_TOOL, self.Menu110, id=110)
        self.Bind(wx.EVT_TOOL, self.Menu101, id=11)
        self.Bind(wx.EVT_TOOL, self.Menu103, id=13)
        self.Bind(wx.EVT_TOOL, self.Menu106, id=16)
        self.Bind(wx.EVT_TOOL, self.Menu105, id=15)
        self.Bind(wx.EVT_TOOL, self.Menu104, id=14)
        self.Bind(wx.EVT_TOOL, self.Menu108, id=18)
        self.Bind(wx.EVT_TOOL, self.Menu203, id=23)
        self.Bind(wx.EVT_TOOL, self.Menu204, id=24)
        self.Bind(wx.EVT_TOOL, self.Menu205, id=25)
        self.Bind(wx.EVT_TOOL, self.Menu301, id=31)
        self.Bind(wx.EVT_TOOL, self.Menu302, id=32)
        self.Bind(wx.EVT_TOOL, self.Tool41, id=41)
        self.Bind(wx.EVT_TOOL, self.Tool42, id=42)
        self.Bind(wx.EVT_TOOL, self.Tool43, id=43)
        self.Bind(wx.EVT_TOOL, self.Tool44, id=44)
        self.Bind(wx.EVT_TOOL, self.Menu601, id=61)
        self.Bind(wx.EVT_TOOL, self.Menu602, id=62)
        self.Bind(wx.EVT_TOOL, self.Menu603, id=63)

        #self.text_ctrl_1.Bind(wx.EVT_MOUSEWHEEL,self.MyMouseMW) end wxGlade
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnActMulu,self.list_ctrl_mulu)
        self.Bind(wx.EVT_TOOL, self.Menu502, id=52)
        self.text_ctrl_1.Bind(wx.EVT_CHAR,self.OnChar)
        self.text_ctrl_2.Bind(wx.EVT_CHAR,self.OnChar3)
        self.list_ctrl_1.Bind(wx.EVT_CHAR,self.OnChar2)
        self.list_ctrl_mulu.Bind(wx.EVT_CHAR,self.OnChar2)
        #self.list_ctrl_1.Bind(wx.EVT_KEY_UP,self.OnCloseSiderbar)
        #self.text_ctrl_2.Bind(wx.EVT_KEY_UP,self.OnCloseSiderbar)
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnReplace)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplace)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_ACTIVATE,self.OnWinActive)
        self.Bind(EVT_UPDATE_STATUSBAR,self.UpdateStatusBar)
        self.Bind(EVT_ReadTimeAlert,self.ReadTimeAlert)
        self.Bind(EVT_DFA,self.DownloadFinished)
        self.Bind(EVT_DUA,self.UpdateStatusBar)
        self.Bind(EVT_AME,self.AlertMsg)
        self.Bind(EVT_ScrollDownPage,self.scrolldownpage)
##        self.Bind(EVT_GetPos,self.getPos)
        self.Bind(EVT_VerCheck,self.DisplayVerCheck)
        self.Bind(wx.EVT_SPLITTER_DCLICK,self.OnSplitterDClick,self.window_1)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected,self.list_ctrl_1)
        self.Bind(wx.EVT_SIZE,self.onSize)
        self.list_ctrl_1.Bind(wx.EVT_CHAR,self.OnDirChar)
        self.Bind(wx.EVT_TEXT,self.SearchSidebar,self.text_ctrl_2)
#        self.text_ctrl_1.Bind(wx.EVT_MIDDLE_DCLICK,self.MyMouseMDC)
#        self.text_ctrl_1.Bind(wx.EVT_RIGHT_DOWN,self.MyMouseRU)
#        self.text_ctrl_1.Bind(wx.EVT_MOUSEWHEEL,self.MyMouseMW)
#        self.text_ctrl_1.Bind(wx.EVT_MIDDLE_DOWN,self.MyMouseMDW)

        #register ESC as system hotkey
        if MYOS == 'Windows':
            if GlobalConfig['EnableESC']:
                self.RegisterHotKey(1,0,wx.WXK_ESCAPE)
                self.Bind(wx.EVT_HOTKEY,self.OnESC)



        self.SetTitle(self.title_str)
        # load last opened file
        if openfile<>None:
            if isinstance(openfile,str):
                enc=chardet.detect(openfile)['encoding']
                openfile=openfile.decode(enc)
            self.LoadFile([openfile],startup=True)
        else:
            if GlobalConfig['LoadLastFile']==True:
                flist=[]
                if GlobalConfig['LastFile'].find('*')==-1: # if there is only one last opened file
                    flist.append(GlobalConfig['LastFile'])
                    if GlobalConfig['LastZipFile']=='':
                        if flist[0].strip()<>'':self.LoadFile(flist,pos=GlobalConfig['LastPos'],startup=True)
                    else:
                        if flist[0].strip()<>'':self.LoadFile(flist,'zip',GlobalConfig['LastZipFile'],pos=GlobalConfig['LastPos'],startup=True)
                else: # if there are multiple last opened files
                    for f in GlobalConfig['LastFile'].split('*'):
                        flist=[]
                        if f.find('|')==-1:
                            flist.append(f)
                            self.LoadFile(flist,openmethod='append',startup=True)
                        else:
                            flist.append(f.split('|')[1])
                            self.LoadFile(flist,'zip',f.split('|')[0].strip(),openmethod='append',startup=True)
                    self.text_ctrl_1.ShowPosition(GlobalConfig['LastPos'])

        self.text_ctrl_1.Bind(wx.EVT_MOUSEWHEEL,self.MyMouseMW)

        #Start Clocking
        self.clk_thread=ClockThread(self)

        #max the window
        self.Maximize(True)

        modes={'paper':601,'book':602,'vbook':603}
        tmodes={'paper':61,'book':62,'vbook':63}
        self.ViewMenu.Check(modes[self.text_ctrl_1.show_mode],True)
        self.frame_1_toolbar.ToggleTool(tmodes[self.text_ctrl_1.show_mode],True)



       #start the display pos thread
        self.display_pos_thread=DisplayPosThread(self)

        #start auto counting thread
        self.auto_count_thread=AutoCountThread(self)

        #start assign images of sidebar
        self.PvFrame=PreviewFrame(self,-1)
        self.image_list=wx.ImageList(16,16,mask=False,initialCount=5)
        self.file_icon_list={}
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/folder.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["folder"]=0
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/txtfile.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["txtfile"]=1
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/zipfile.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["zipfile"]=2
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/htmlfile.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["htmlfile"]=3
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/rarfile.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["rarfile"]=4
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/file.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["file"]=5
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/jar.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["jarfile"]=6
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/umd.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["umdfile"]=7
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/up.png",wx.BITMAP_TYPE_ANY)
        self.up=self.image_list.Add(bmp)
        self.file_icon_list["up"]=8
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/down.png",wx.BITMAP_TYPE_ANY)
        self.dn=self.image_list.Add(bmp)
        self.file_icon_list["down"]=9
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/epub.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["epub"]=10

        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/Driver.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["driver"]=11

        self.list_ctrl_1.AssignImageList(self.image_list,wx.IMAGE_LIST_SMALL)
        self.list_ctrl_1.InsertColumn(0,u'文件名',width=400)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActive, self.list_ctrl_1)
        self.itemDataMap={}
        wx.lib.mixins.listctrl.ColumnSorterMixin.__init__(self,3)
        self.LastDir=''

        #if enabled, check version update
        if GlobalConfig['VerCheckOnStartup']:
            self.version_check_thread=VersionCheckThread(self,False)

            #hide the text_ctrl's cursor
            #self.text_ctrl_1.Bind(wx.EVT_SET_FOCUS, self.TextOnFocus)
            #self.text_ctrl_1.HideNativeCaret()
        self.__set_properties()
        self.__do_layout()
        #add UPNP mapping via thread, otherwise it will block, and it takes long time
        self.upnp_t=None
        if GlobalConfig['RunUPNPAtStartup']:
            self.upnp_t = ThreadAddUPNPMapping(self)
            self.upnp_t.start()
        #starting web server if configured
        self.server=None
        try:
            self.server = ThreadedLBServer(('', GlobalConfig['ServerPort']), LBHTTPRequestHandler)
        except socket.error:
            splash_frame.Close()
            dlg = wx.MessageDialog(self,u'端口'+
                str(GlobalConfig['ServerPort'])+
                u'已被占用，WEB服务器无法启动！或许是因为litebook已经在运行？',
               u'出错了！',
               wx.OK | wx.ICON_ERROR
               )
            dlg.ShowModal()
            dlg.Destroy()
        else:
            # Start a thread with the server -- that thread will then start one
            # more thread for each request
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            # Exit the server thread when the main thread terminates
            self.server_thread.setDaemon(True)
            #GlobalConfig['RunWebserverAtStartup'] = True #always start web service for LTBNET
            if GlobalConfig['RunWebserverAtStartup']:
                try:
                    self.server_thread.start()
                    mbar=self.GetMenuBar()
                    mbar.Check(705,True)
                except:
                    dlg = wx.MessageDialog(self, u'启动WEB服务器失败',
                       u'出错了！',
                       wx.OK | wx.ICON_ERROR
                       )
                    dlg.ShowModal()
                    dlg.Destroy()
        #print "starting mDNS"
        #start mDNS ifconfigured
        self.mDNS=None
        if GlobalConfig['RunWebserverAtStartup']:
            if MYOS == 'Linux':
                host_ip=GetMDNSIP()
            elif MYOS == 'Darwin':
                host_ip=GetMDNSIP_OSX()
            else:
                host_ip=GetMDNSIP_Win()
            if host_ip:
                self.mDNS=Zeroconf.Zeroconf(host_ip)
                self.mDNS_svc=Zeroconf.ServiceInfo("_opds._tcp.local.", "litebook_shared._opds._tcp.local.", socket.inet_aton(host_ip), GlobalConfig['ServerPort'], 0, 0, {'version':'0.10'})
                self.mDNS.registerService(self.mDNS_svc)

        #start KADP
        self.KPUB_thread=None
        self.DownloadManager=None
        self.lsd=None
        if GlobalConfig['EnableLTBNET']:
            kadp_ip='127.0.0.1'
            if MYOS == 'Windows':
                kadp_exe = cur_file_dir()+"\kadp\KADP.exe"
                cmd = [
                    kadp_exe,
                    '-product',
                    str(GlobalConfig['LTBNETPort']),
                    GlobalConfig['LTBNETID'],
                    '0',
                    '1',
                ]
            else:
                cmd = [
                    'python',
                    cur_file_dir()+"/KADP.py",
                    '-product',
                    str(GlobalConfig['LTBNETPort']),
                    GlobalConfig['LTBNETID'],
                    '0',
                    '1',
                ]
                #following is the test code
    ##            kadp_ip='218.21.123.99'
    ##            cmd = [
    ##                'python',
    ##                cur_file_dir()+"/KADP.py",
    ##                '-server',
    ##                kadp_ip,
    ##                '50200',
    ##                '11110111100000009999',
    ##                '/root/kconf-21',
    ##                '0',
    ##            ]
            GlobalConfig['kadp_ctrl'] = xmlrpclib.Server('http://'+kadp_ip+':50201/')
            if hasattr(sys.stderr, 'fileno'):
                childstderr = sys.stderr
            elif hasattr(sys.stderr, '_file') and hasattr(sys.stderr._file, 'fileno'):
                childstderr = sys.stderr._file
            else:
                # Give up and point child stderr at nul
                childStderrPath = 'nul'
                childstderr = file(childStderrPath, 'a')
            #childstderr = file('nul', 'a')
            if MYOS == 'Windows':
                self.KADP_Process = subprocess.Popen(cmd, stdin=childstderr,stdout=childstderr,stderr=childstderr,creationflags = win32process.CREATE_NO_WINDOW)
            else:
                self.KADP_Process = subprocess.Popen(cmd)
            self.KPUB_thread = kpub.KPUB(GlobalConfig['ShareRoot'],rloc_base_url=u'http://SELF:'+str(GlobalConfig['ServerPort'])+'/')
            self.KPUB_thread.start()
            #create download manager
            self.DownloadManager = download_manager.DownloadManager(self,GlobalConfig['ShareRoot'])
            #create LTBNET search dialog
            self.lsd = ltbsearchdiag.LTBSearchDiag(self,self.DownloadManager.addTask,'http://'+kadp_ip+':50201/')
            wx.CallLater(10000,self.chkPort,False)

        splash_frame.Close()
        #print "splash_frame clsoed"
        #set show mode, this has to be here, otherwise system won't load if showmode is book or vbook
        self.text_ctrl_1.SetShowMode(GlobalConfig['showmode'])
        mlist={'paper':601,'book':602,'vbook':603}
        tlist={'paper':61,'book':62,'vbook':63}
        self.ViewMenu.Check(mlist[GlobalConfig['showmode']],True)
        self.frame_1_toolbar.ToggleTool(tlist[GlobalConfig['showmode']],True)

        self.websubscrdlg=None





##        def TextOnFocus(self,event):
##            self.text_ctrl_1.HideNativeCaret()
##            event.Skip()
##





    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(GlobalConfig['IconDir']+u"/litebook-icon_32x32.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        #self.SetTitle(u"轻巧看书 LiteBook")
        self.SetSize((640, 480))
        # statusbar fields
        self.frame_1_statusbar.SetStatusWidths([-2, -1,-1,-3])
        frame_1_statusbar_fields = ["ready."]
        for i in range(len(frame_1_statusbar_fields)):
            self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)


        # end wxGlade

        # load last appearance
##        if str(type(GlobalConfig['CurFont']))=="<class 'wx._gdi.Font'>":
##            self.text_ctrl_1.SetFont(GlobalConfig['CurFont'])
##        if GlobalConfig['CurFColor']<>'':
##            self.text_ctrl_1.SetForegroundColour(GlobalConfig['CurFColor'])
##        if GlobalConfig['CurBColor']<>'':
##            self.text_ctrl_1.SetBackgroundColour(GlobalConfig['CurBColor'])
##        self.text_ctrl_1.Refresh()


    def __do_layout(self):
        global GlobalConfig
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        #Use splitwindow to add dir sidebar
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_mulu=wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.text_ctrl_2, 0, wx.EXPAND, 0)
        sizer_2.Add(self.list_ctrl_1, 1, wx.EXPAND, 0)
        sizer_mulu.Add(self.list_ctrl_mulu,1,wx.EXPAND,1)
        self.window_1_pane_1.SetSizer(sizer_2)
        self.window_1_pane_mulu.SetSizer(sizer_mulu)
        sizer_3.Add(self.text_ctrl_1, 1, wx.EXPAND, 0)
        self.window_1_pane_2.SetSizer(sizer_3)
        #self.window_1.Initialize(self.window_1_pane_2)
        #self.window_1.UpdateSize()
        self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2,self.SidebarPos)
        self.window_1.Unsplit(self.window_1_pane_1)
        sizer_1.Add(self.window_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        #Hide the toolbar if it is hidden when litebook exit last time
        if GlobalConfig['HideToolbar']:
            self.GetToolBar().Hide()
            self.SetToolBar(None)
            self.Refresh()
            self.Layout()
        # end wxGlade

    def onSize(self, event):
        self.text_ctrl_1.SetSize(self.GetClientSize())
        event.Skip()
        return

    def ResetTool(self,newsize=(32,32)):
        global MYOS
        try:
            self.frame_1_toolbar.ClearTools()
            self.frame_1_toolbar.Destroy()
        except:
            pass

        self.frame_1_toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_3DBUTTONS)
        self.SetToolBar(self.frame_1_toolbar)
        self.frame_1_toolbar.SetToolBitmapSize(newsize)
        self.frame_1_toolbar.SetMargins((0,0))
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"Network-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(110, u"搜索并下载", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"搜索并下载", u"搜索并下载")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"DirSideBar.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddCheckLabelTool(52, u"打开文件侧边栏",bmp, wx.NullBitmap, u"打开文件侧边栏", u"打开文件侧边栏")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"file-open-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(11, u"打开", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"打开文件", u"打开文件列表")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"file-close-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(13, u"关闭", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"关闭文件", u"关闭文件")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"savefile-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(18, u"另存为", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"另存为", u"另存为")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"option-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(16, u"选项", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"选项", u"选项")
        self.frame_1_toolbar.AddSeparator()
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"next-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(15, u"下一个", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"下一个文件", u"下一个文件")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"previous-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(14, u"上一个", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"上一个文件", u"上一个文件")
        self.frame_1_toolbar.AddSeparator()
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"paper.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddRadioLabelTool(61,u'纸张显示模式',bmp, wx.NullBitmap,u'纸张显示模式',u'纸张显示模式')
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"openbook.jpg", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddRadioLabelTool(62,u'书本显示模式',bmp, wx.NullBitmap,u'书本显示模式',u'书本显示模式')
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"vbook.jpg", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddRadioLabelTool(63,u'竖排书本显示模式',bmp, wx.NullBitmap,u'竖排书本显示模式',u'竖排书本显示模式')
        self.frame_1_toolbar.AddSeparator()
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"search-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(23, u"查找", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"搜索", u"搜索")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"search-next-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(24, u"查找下一个", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"搜索下一个", u"搜索下一个")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"search-previous-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(25, u"查找上一个", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"搜索上一个", u"搜索上一个")
        self.frame_1_toolbar.AddSeparator()
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"bookmark-add-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(31, u"加入收藏夹", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"将当前阅读位置加入收藏夹", u"将当前阅读位置加入收藏夹")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"bookmark-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(32, u"收藏夹", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"打开收藏夹", u"打开收藏夹")
        self.frame_1_toolbar.AddSeparator()
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"format-32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.FormatTool=self.frame_1_toolbar.AddCheckLabelTool(44, u"智能分段", bmp, wx.NullBitmap, u"智能分段", u"智能分段")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"html--32x32.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(41, "HTML", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"过滤HTML标记", u"过滤HTML标记")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"jian.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(42, u"切换为简体字", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"切换为简体字", u"切换为简体字")
        bmp=wx.Bitmap(GlobalConfig['IconDir']+os.sep+u"fan.png", wx.BITMAP_TYPE_ANY)
        bmp=bmp.ConvertToImage().Rescale(newsize[0],newsize[1],wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.frame_1_toolbar.AddLabelTool(43, u"切换为繁体字", bmp, wx.NullBitmap, wx.ITEM_NORMAL, u"切换为繁体字", u"切换为繁体字")
        self.frame_1_toolbar.AddSeparator()
        if MYOS == 'Linux':
            wid=wx.ScreenDC().GetSize()[0]-1024+50
            if wid<50:wid=50
            if wid>200:wid=200
        if MYOS == 'Linux':
            self.sliderControl=wx.Slider(self.frame_1_toolbar, -1, 0, 0, 100,size=(wid,-1),style=wx.SL_LABELS)
        else:
            self.sliderControl=wx.Slider(self.frame_1_toolbar, -1, 0, 0, 100,style=wx.SL_LABELS)
        self.sliderControl.SetSize((-1,newsize[0]))
        self.frame_1_toolbar.AddControl(self.sliderControl)
        self.sliderControl.Bind(wx.EVT_SCROLL,self.OnSScroll)
        self.frame_1_toolbar.SetToolSeparation(5)
        self.frame_1_toolbar.Realize()


    def ResetMenu(self):
        mbar=self.GetMenuBar()
        mbar.SetLabel(101,u"文件列表(&L)"+KeyMenuList[u'文件列表'])
        mbar.SetLabel(102,u"打开文件(&O)"+KeyMenuList[u'打开文件'])
        mbar.SetLabel(108,u"另存为...(&S)"+KeyMenuList[u'另存为'])
        mbar.SetLabel(103,u"关闭(&C)"+KeyMenuList[u'关闭'])
        mbar.SetLabel(104,u"上一个文件(&P)"+KeyMenuList[u'上一个文件'])
        mbar.SetLabel(105,u"下一个文件(&N)"+KeyMenuList[u'下一个文件'])
        mbar.SetLabel(110,u"搜索小说网站(&S)"+KeyMenuList[u'搜索小说网站'])
        mbar.SetLabel(111,u"重新载入插件"+KeyMenuList[u'重新载入插件'])
        mbar.SetLabel(112,u"清空缓存"+KeyMenuList[u'清空缓存'])
        mbar.SetLabel(113, u"搜索LTBNET"+KeyMenuList[u'搜索LTBNET'])
        mbar.SetLabel(114, u"下载管理器"+KeyMenuList[u'下载管理器'])
        mbar.SetLabel(115, u"管理订阅"+KeyMenuList[u'管理订阅'])
        mbar.SetLabel(106,u"选项(&O)"+KeyMenuList[u'选项'])
        mbar.SetLabel(107,u"退出(&X)"+KeyMenuList[u'退出'])
        mbar.SetLabel(202,u"拷贝(&C)"+KeyMenuList[u'拷贝'])
        mbar.SetLabel(203,u"查找(&S)"+KeyMenuList[u'查找'])
        mbar.SetLabel(204,u"查找下一个(&N)"+KeyMenuList[u'查找下一个'])
        mbar.SetLabel(205,u"查找上一个(&N)"+KeyMenuList[u'查找上一个'])
        mbar.SetLabel(206,u"替换(&R)"+KeyMenuList[u'替换'])
        mbar.SetLabel(601,u'纸张显示模式'+KeyMenuList[u'纸张显示模式'])
        mbar.SetLabel(602,u'书本显示模式'+KeyMenuList[u'书本显示模式'])
        mbar.SetLabel(603,u'竖排书本显示模式'+KeyMenuList[u'竖排书本显示模式'])

        mbar.SetLabel(501,u"显示工具栏"+KeyMenuList[u'显示工具栏'])
        mbar.SetLabel(511,u"缩小工具栏"+KeyMenuList[u'缩小工具栏'])
        mbar.SetLabel(512,u"放大工具栏"+KeyMenuList[u'放大工具栏'])
        mbar.SetLabel(503, u"全屏显示"+KeyMenuList[u'全屏显示'])
        mbar.SetLabel(502,u"显示文件侧边栏"+KeyMenuList[u'显示文件侧边栏'])
        mbar.SetLabel(505,u"自动翻页"+KeyMenuList[u'自动翻页'])
        mbar.SetLabel(506,u"显示进度条"+KeyMenuList[u'显示进度条'])
        mbar.SetLabel(504,u"智能分段"+KeyMenuList[u'智能分段'])
        mbar.SetLabel(507,u"增大字体"+KeyMenuList[u'增大字体'])
        mbar.SetLabel(508,u"减小字体"+KeyMenuList[u'减小字体'])
        mbar.SetLabel(509,u"显示章节"+KeyMenuList[u'显示目录'])
        mbar.SetLabel(510,u'显示章节侧边栏'+KeyMenuList[u'显示章节侧边栏'])
        mbar.SetLabel(301,u"添加到收藏夹(&A)"+KeyMenuList[u'添加到收藏夹'])
        mbar.SetLabel(302,u"整理收藏夹(&M)"+KeyMenuList[u'整理收藏夹'])
        mbar.SetLabel(701,u"过滤HTML标签"+KeyMenuList[u'过滤HTML标记'])
        mbar.SetLabel(702,u"简体转繁体"+KeyMenuList[u'切换为繁体字'])
        mbar.SetLabel(703,u"繁体转简体"+KeyMenuList[u'切换为简体字'])
        mbar.SetLabel(704,u"生成EPUB文件"+KeyMenuList[u'生成EPUB文件'])
        mbar.SetLabel(705,u"启用WEB服务器"+KeyMenuList[u'启用WEB服务器'])
        mbar.SetLabel(706,u'检测端口是否开启'+KeyMenuList[u'检测端口是否开启'])
        mbar.SetLabel(707,u'使用UPNP添加端口映射'+KeyMenuList[u'使用UPNP添加端口映射'])

        mbar.SetLabel(401,u"简明帮助(&B)"+KeyMenuList[u'简明帮助'])
        mbar.SetLabel(404,u"版本更新内容"+KeyMenuList[u'版本更新内容'])
        mbar.SetLabel(403,u"检查更新(&C)"+KeyMenuList[u'检查更新'])
        mbar.SetLabel(402,u"关于(&A)"+KeyMenuList[u'关于'])

        mbar.Refresh()


    def Menu101(self, event=None): # wxGlade: MyFrame.<event_handler>
        dlg=MyOpenFileDialog(self)
        dlg.ShowModal()
        if dlg.zip_file=='':
            if dlg.select_files<>[]:self.LoadFile(dlg.select_files,openmethod=dlg.open_method)
        else:
            self.LoadFile(dlg.select_files,'zip',dlg.zip_file,openmethod=dlg.open_method)
        dlg.Destroy()

    def Menu102(self, event): # wxGlade: MyFrame.<event_handler>
        global GlobalConfig
        wildcard = u"文本文件 (*.txt)|*.txt|"     \
           u"HTML文件 (*.htm;*.html)|*.htm;*.html|" \
           u"电子书 (*.umd;*.jar;*.epub)|*.umd;*.jar;*.epub|" \
           u"所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=GlobalConfig['LastDir'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            flist=dlg.GetPaths()
            #GlobalConfig['LastDir']=os.path.split(flist[0])[0]
            self.LoadFile(flist)

        #event.Skip()

    def Menu103(self, event): # wxGlade: MyFrame.<event_handler>
        global current_file,OnScreenFileList
        if self.text_ctrl_1.GetValue()<>'':self.SaveBookDB()
        self.text_ctrl_1.Clear()
        self.buff=""
        current_file=''
        OnScreenFileList=[]
        self.frame_1_statusbar.SetStatusText('Ready.')
        self.SetTitle(self.title_str)
        self.cur_catalog=None

    def Menu104(self, event): # wxGlade: MyFrame.<event_handler>
        self.LoadNextFile(-1)

    def Menu105(self, event): # wxGlade: MyFrame.<event_handler>
        self.LoadNextFile(1)

    def Menu106(self, event): # wxGlade: MyFrame.<event_handler>
        option_dlg=NewOptionDialog(self)
        option_dlg.ShowModal()
        #option_dlg.Destroy()
        self.ResetMenu()
        self.text_ctrl_1.SetShowMode(GlobalConfig['showmode'])
        if GlobalConfig['backgroundimg']<>'' and GlobalConfig['backgroundimg']<>None:
            self.text_ctrl_1.SetBackgroundColour(GlobalConfig['CurBColor'])
            self.text_ctrl_1.SetImgBackground(GlobalConfig['backgroundimg'],GlobalConfig['backgroundimglayout'])
        else:
            self.text_ctrl_1.SetBackgroundColour(GlobalConfig['CurBColor'])
            self.text_ctrl_1.bg_img=None
        self.text_ctrl_1.SetFColor(GlobalConfig['CurFColor'])
        self.text_ctrl_1.SetFont(GlobalConfig['CurFont'])
        self.text_ctrl_1.SetUnderline(GlobalConfig['underline'],GlobalConfig['underlinestyle'],GlobalConfig['underlinecolor'])
        self.text_ctrl_1.SetSpace(GlobalConfig['pagemargin'],GlobalConfig['bookmargin'],GlobalConfig['vbookmargin'],GlobalConfig['centralmargin'],GlobalConfig['linespace'],GlobalConfig['vlinespace'])
        self.text_ctrl_1.ReDraw()
        modes={'paper':601,'book':602,'vbook':603}
        tmodes={'paper':61,'book':62,'vbook':63}
        self.ViewMenu.Check(modes[self.text_ctrl_1.show_mode],True)
        self.frame_1_toolbar.ToggleTool(tmodes[self.text_ctrl_1.show_mode],True)





    def Menu107(self, event): # wxGlade: MyFrame.<event_handler>
        self.Close()

    def Menu108(self, event): # wxGlade: MyFrame.<event_handler>
        global GlobalConfig
        wildcard = u"文本文件(UTF-8) (*.txt)|*.txt|"     \
           u"文本文件(GBK) (*.txt)|*.txt"
        dlg = wx.FileDialog(
            self, message=u"将当前文件另存为", defaultDir=GlobalConfig['LastDir'],
            defaultFile="", wildcard=wildcard, style=wx.SAVE | wx.FD_OVERWRITE_PROMPT
            )

        if dlg.ShowModal() == wx.ID_OK:
            savefilename=dlg.GetPath()
            if dlg.GetFilterIndex()==0:
                try:
                    fp=codecs.open(savefilename,encoding='utf-8',mode='w')
                    fp.write(self.text_ctrl_1.GetValue())
                    fp.close()
                except:
                    err_dlg = wx.MessageDialog(None, u'写入文件：'+fname+u' 错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    return False
            else:
                try:
                    fp=codecs.open(savefilename,encoding='GBK',mode='w')
                    ut=self.text_ctrl_1.GetValue().encode('GBK', 'ignore')
                    ut=unicode(ut, 'GBK', 'ignore')
                    fp.write(ut)
                    fp.close()
                except:
                    err_dlg = wx.MessageDialog(None, u'写入文件：'+savefilename+u' 错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    return False

        dlg.Destroy()

    def Menu109(self, event): # wxGlade: MyFrame.<event_handler>
        if self.FileHistoryDiag==None:self.FileHistoryDiag=FileHistoryDialog(self)
        #dlg=FileHistoryDialog(self)
        self.FileHistoryDiag.ShowModal()
        self.FileHistoryDiag.Hide()

    def Menu112(self,evt):
        global MYOS
        dlg=wx.MessageDialog(self,u'此操作将清空目前所有的缓存文件，确认继续吗？',u'清空缓存',wx.NO_DEFAULT|wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal()==wx.ID_YES:
            if MYOS == 'Windows':
                flist=glob.glob(os.environ['USERPROFILE'].decode('gbk')+u"\\litebook\\cache\\*")
            else:
                flist=glob.glob(unicode(os.environ['HOME'],'utf-8')+u"/litebook/cache/*")
            suc=True
            for f in flist:
                try:
                    os.remove(f)
                except:
                    suc=False
            dlg.Destroy()
            if suc:
                mstr=u'缓存已经全部清空！'
            else:
                mstr=u'操作结束，过程中发生一些错误'
            dlg=wx.MessageDialog(self,mstr,u'清空缓存的结果',wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()


    def Menu111(self,event):
        readPlugin()

    def Menu110(self,event):
        dlg=Search_Web_Dialog(self)
        dlg.ShowModal()
        try:
            sitename=dlg.sitename
        except:
            sitename=None
        if sitename<>None:
            keyword=dlg.keyword
            try:
                dlg.Destroy()
            except:
                pass
            dlg=web_search_result_dialog(self,sitename,keyword)
            dlg.ShowModal()
            #self.text_ctrl_1.SetValue(dlg.bk)
            try:
                dlg.Destroy()
            except:
                pass

    def Menu113(self,evt):
        """
        search LTBNET
        """
        #lsd = ltbsearchdiag.LTBSearchDiag(self,self.DownloadManager.addTask,'http://127.0.0.1:50201')
        if self.lsd==None:
            dlg=wx.MessageDialog(self,u'LTBNET没有启动，无法搜索！',u'注意',wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.lsd.Show()

    def Menu114(self,evt):
        """
        Download Manager
        """
        #global GlobalConfig
        if self.DownloadManager==None:
            dlg=wx.MessageDialog(self,u'LTBNET没有启动，无法下载！',u'注意',wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.DownloadManager.Show()

    def Menu115(self,evt):
        if self.websubscrdlg==None:
            self.websubscrdlg=WebSubscrDialog(self)
            self.websubscrdlg.ShowModal()
        else:
            self.websubscrdlg.ShowModal()


    def Menu202(self, event): # wxGlade: MyFrame.<event_handler>
        self.text_ctrl_1.CopyText()

    def Menu203(self, event): # wxGlade: MyFrame.<event_handler>
        searchdata = wx.FindReplaceData()
        searchdata.SetFlags(1)
        searchdata.SetFindString(self.search_str)
        searchdlg = wx.FindReplaceDialog(self, searchdata, "Find",wx.FR_NOWHOLEWORD)
        searchdlg.data=searchdata
        searchdlg.Show(True)

    def Menu204(self, event): # wxGlade: MyFrame.<event_handler>
        self.search_flg=wx.FR_DOWN
        self.FindNext()

    def Menu205(self, event): # wxGlade: MyFrame.<event_handler>
        self.search_flg=0
        self.FindNext()
    def Menu206(self,evt):
        searchdata = wx.FindReplaceData()
        searchdata.SetFlags(1)
        searchdata.SetFindString(self.search_str)
        searchdlg = wx.FindReplaceDialog(self, searchdata, u"替换",wx.FR_REPLACEDIALOG| wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD)
        searchdlg.data=searchdata
        searchdlg.Show(True)


    def Menu301(self, event): # wxGlade: MyFrame.<event_handler>
        global OnScreenFileList,BookMarkList
        bookmark={}
        pos=self.GetCurrentPos()
        if self.text_ctrl_1.GetValue()<>'':
            if OnScreenFileList.__len__()==1: # if there is only one current on_screen file
                if not load_zip or current_zip_file=='':
                    bookmark['filename']=current_file
                else:
                    bookmark['filename']=current_zip_file+u"|"+current_file
            else:
                tstr=u''
                for onscrfile in OnScreenFileList:
                    tstr+=onscrfile[0]+u'*'
                tstr=tstr[:-1]
                bookmark['filename']=tstr
            bookmark['pos']=pos
            bookmark['line']=self.text_ctrl_1.GetValue()[pos:pos+30].splitlines()[0]
            BookMarkList.append(bookmark)
            dlg = wx.MessageDialog(self, u'当前阅读位置已加入收藏夹！',u"提示！",wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()



    def Menu302(self, event): # wxGlade: MyFrame.<event_handler>
        bk_dlg=BookMarkDialog(self)
        bk_dlg.ShowModal()
        filename=bk_dlg.filename
        pos=bk_dlg.pos
        bk_dlg.Destroy()
        if filename<>'':self.LoadBookmark(filename,pos)

    def Menu401(self, event): # wxGlade: MyFrame.<event_handler>
        url="file://"+cur_file_dir()+'/helpdoc/litebook.html'
        webbrowser.open_new_tab(url)
    def Menu404(self, event): # wxGlade: MyFrame.<event_handler>
        url="file://"+cur_file_dir()+'/helpdoc/99.html'
        webbrowser.open_new_tab(url)
    def Menu402(self, event): # wxGlade: MyFrame.<event_handler>
        global Version
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = self.title_str
        info.Version = Version
        info.Copyright = "(C) 2012 Hu Jun"
        info.Description = u"轻巧看书，简单好用的看书软件！"

        info.WebSite = (u"http://code.google.com/p/litebook-project/", u"官方网站")

        #info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

    def Menu403(self, event): # wxGlade: MyFrame.<event_handler>
        self.version_check_thread=VersionCheckThread(self)

    def Menu501(self, event):
        mytbar=self.GetToolBar()
        if  mytbar==None or not mytbar.IsShown():
            self.ResetTool((GlobalConfig['ToolSize'],GlobalConfig['ToolSize']))
        else:
            mytbar.Hide()
            self.SetToolBar(None)
            self.Refresh()
            self.Layout()


    def CloseSidebar(self,evt=None):
        """Hide the directory sidebar"""
        if self.window_1.IsSplit():
            self.SidebarPos=self.window_1.GetSashPosition()
            self.PvFrame.Hide()
            self.window_1.Unsplit(self.window_1_pane_1)
            self.frame_1_toolbar.ToggleTool(52,False)
            self.SidebarMenu.Check(502,False)
            self.text_ctrl_1.SetFocus()



    def Menu502(self, event=None):
        """Show/Hide the directory sidebar"""
        mbar=self.GetMenuBar()
        if self.window_1.IsSplit():
            if self.window_1_pane_1.IsShown():
                self.SidebarPos=self.window_1.GetSashPosition()
                self.PvFrame.Hide()
                self.window_1.Unsplit(self.window_1_pane_1)
                self.frame_1_toolbar.ToggleTool(52,False)
                self.SidebarMenu.Check(502,False)
                self.text_ctrl_1.SetFocus()
            else:
                self.window_1.Unsplit(self.window_1_pane_mulu)
                mbar.Check(510,False)
                self.DirSideBarReload()
                self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2,self.SidebarPos)
                self.frame_1_toolbar.ToggleTool(52,True)
                self.SidebarMenu.Check(502,True)
                self.list_ctrl_1.SetFocus()

        else:
            self.DirSideBarReload()
            self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2,self.SidebarPos)
            self.frame_1_toolbar.ToggleTool(52,True)
            self.SidebarMenu.Check(502,True)
            self.list_ctrl_1.SetFocus()

    def OnActMulu(self,evt):
        ind=evt.GetIndex()
        i=self.list_ctrl_mulu.GetItemData(ind)
        if i<len(self.cur_catalog):
            pos=self.cur_catalog[i][1]
            self.text_ctrl_1.JumpTo(pos)






    def Menu510(self, event=None):
        """Show/Hide the mulu sidebar"""
        mbar=self.GetMenuBar()
        if self.window_1.IsSplit():
            if self.window_1_pane_mulu.IsShown():
                self.SidebarPos=self.window_1.GetSashPosition()
                self.window_1.Unsplit(self.window_1_pane_mulu)
                mbar.Check(510,False)
                self.text_ctrl_1.SetFocus()
            else:
                self.window_1.Unsplit(self.window_1_pane_1)
                mbar.Check(502,False)
                self.reloadMulu()
                self.window_1.SplitVertically(self.window_1_pane_mulu, self.window_1_pane_2,self.SidebarPos)
                mbar.Check(510,True)
                self.list_ctrl_mulu.SetFocus()
        else:
            self.reloadMulu()
            self.window_1.SplitVertically(self.window_1_pane_mulu, self.window_1_pane_2,self.SidebarPos)
            mbar.Check(510,True)
            self.list_ctrl_mulu.SetFocus()

    def Menu511(self,evt):
        global GlobalConfig
        GlobalConfig['ToolSize']-=1
        self.ResetTool((GlobalConfig['ToolSize'],GlobalConfig['ToolSize']))

    def Menu512(self,evt):
        global GlobalConfig
        GlobalConfig['ToolSize']+=1
        self.ResetTool((GlobalConfig['ToolSize'],GlobalConfig['ToolSize']))


    def Menu503(self, event):
        self.showfullscr=not self.showfullscr
        self.ShowFullScreen(self.showfullscr,wx.FULLSCREEN_ALL)
        if self.showfullscr:
            self.text_ctrl_1.Bind(wx.EVT_CONTEXT_MENU, self.ShowFullScrMenu)
        else:
            self.text_ctrl_1.Bind(wx.EVT_CONTEXT_MENU, None)

    def Menu505(self,event):

        self.autoscroll=not self.autoscroll

    def Menu507(self,evt):
        self.ChangeFontSize(1)

    def Menu508(self,evt):
        self.ChangeFontSize(-1)

    def reloadMulu(self):
        if self.cur_catalog==None:
            rlist=GenCatalog(self.text_ctrl_1.GetValue())
            self.cur_catalog=rlist
        else:
            rlist=self.cur_catalog
        self.list_ctrl_mulu.DeleteAllItems()
        i=0
        for c in rlist:
            ind=self.list_ctrl_mulu.InsertStringItem(sys.maxint,c[0])
            self.list_ctrl_mulu.SetItemData(ind,i)
            i+=1
        c_pos=self.text_ctrl_1.GetStartPos()
        i=0
        for cc in rlist:
            if c_pos<cc[1]:
                break
            else:
                i+=1
        self.list_ctrl_mulu.Select(i-1)
        self.list_ctrl_mulu.Focus(i-1)
        self.list_ctrl_mulu.SetColumnWidth(0,-1)
        self.list_ctrl_mulu.EnsureVisible(i-1)


    def GetChapter(self):
        """
        return following:
            - rlist from GenCatalog
            - clist from GenCatalog
            - current chapter name
            - current index in rlist
        """
        if self.cur_catalog==None:
            rlist=GenCatalog(self.text_ctrl_1.GetValue())
            self.cur_catalog=rlist
        else:
            rlist=self.cur_catalog
        c_pos=self.text_ctrl_1.GetStartPos()
        i=0
        for cc in rlist:
            if c_pos<cc[1]:
                break
            else:
                i+=1
        return (rlist,i,rlist[i-1][0].strip())



    def Menu509(self,evt):
##        if self.cur_catalog==None:
##            rlist,c_list=GenCatalog(self.text_ctrl_1.GetValue())
##            self.cur_catalog=(rlist,c_list)
##        else:
##            rlist=self.cur_catalog[0]
##            c_list=self.cur_catalog[1]
        (rlist,i,cname)=self.GetChapter()
        c_list=[]
        for c in rlist:
            c_list.append(c[0])
        dlg = wx.SingleChoiceDialog(
                self, u'选择章节并跳转', u'章节选择',
                choices=c_list,
                style=wx.CHOICEDLG_STYLE
                )
##        c_pos=self.text_ctrl_1.GetStartPos()
##        i=0
##        for cc in c_list:
##            if c_pos<rlist[cc]:
##                break
##            else:
##                i+=1
        dlg.SetSelection(i-1)
        if dlg.ShowModal() == wx.ID_OK:
            i=dlg.GetSelection()
            pos=rlist[i][1]
            self.text_ctrl_1.JumpTo(pos)
        dlg.Destroy()


    def Menu601(self,event):
        global GlobalConfig
        self.text_ctrl_1.SetShowMode('paper')
        self.text_ctrl_1.ReDraw()
        self.ViewMenu.Check(601,True)
        self.frame_1_toolbar.ToggleTool(61,True)
        GlobalConfig['showmode']='paper'

    def Menu602(self,event):
        global GlobalConfig
        self.text_ctrl_1.SetShowMode('book')
        self.text_ctrl_1.ReDraw()
        self.ViewMenu.Check(602,True)
        self.frame_1_toolbar.ToggleTool(62,True)
        GlobalConfig['showmode']='book'

    def Menu603(self,event):
        global GlobalConfig
        self.text_ctrl_1.SetShowMode('vbook')
        self.text_ctrl_1.ReDraw()
        self.ViewMenu.Check(603,True)
        self.frame_1_toolbar.ToggleTool(63,True)
        GlobalConfig['showmode']='vbook'

    def Menu704(self,evt):
        global OnScreenFileList
        if self.text_ctrl_1.GetValue()=="":
            return
        nlist=OnScreenFileList[0][0].split("|")
        if len(nlist)>1:
            curfile=nlist[1]
        else:
            curfile=nlist[0]
        curfile=os.path.basename(curfile)
        curfile=os.path.splitext(curfile)[0]
        dlg=Convert_EPUB_Dialog(self,curfile,curfile,'')
        dlg.ShowModal()
        if dlg.id=='OK':
            ldlg = GMD.GenericMessageDialog(self, u' 正在生成EPUB文件。。。',u"生成中...",wx.ICON_INFORMATION)
            ldlg.Show()
            ldlg.Update()
            txt2epub(self.text_ctrl_1.GetValue(),dlg.outfile,dlg.title,[dlg.author,],dlg.divide_method,dlg.zishu)
            ldlg.Destroy()


        dlg.Destroy()


    def Menu705(self,evt):
        global MYOS
        mbar=self.GetMenuBar()
        if not mbar.IsChecked(705):
            self.server.shutdown()
            if self.mDNS<>None:
                self.mDNS.unregisterService(self.mDNS_svc)
#            self.mDNS.close()

        else:
            if self.server==None:
                try:
                    self.server = ThreadedLBServer(('', GlobalConfig['ServerPort']), LBHTTPRequestHandler)
                except socket.error:
                    dlg = wx.MessageDialog(self,u'端口'+
                        str(GlobalConfig['ServerPort'])+
                        u'已被占用，WEB服务器无法启动！或许是因为litebook已经在运行？',
                       u'出错了！',
                       wx.OK | wx.ICON_ERROR
                       )
                    dlg.ShowModal()
                    dlg.Destroy()
                    mbar.Check(705,False)
                    return
            try:
                self.server_thread = threading.Thread(target=self.server.serve_forever)
                self.server_thread.setDaemon(True)
                self.server_thread.start()
            except Exception as inst:
                dlg = wx.MessageDialog(self, u'WEB服务器启动错误!\n'+str(inst),u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                mbar.Check(705,False)
            try:
                if MYOS == 'Linux':
                    host_ip=GetMDNSIP()
                elif MYOS == 'Darwin':
                    host_ip=GetMDNSIP_OSX()
                else:
                    host_ip=GetMDNSIP_Win()

                if host_ip:
                    self.mDNS=Zeroconf.Zeroconf(host_ip)
            ##        print host_ip
                    self.mDNS_svc=Zeroconf.ServiceInfo("_opds._tcp.local.", "litebook_shared._opds._tcp.local.", socket.inet_aton(host_ip), GlobalConfig['ServerPort'], 0, 0, {'version':'0.10'})
                    self.mDNS.registerService(self.mDNS_svc)
            except Exception as inst:
                print traceback.format_exc()
                dlg = wx.MessageDialog(self, u'mDNS服务启动错误!\n'+str(inst),u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

    def chkPort(self,AlertOnOpen=True):
        global GlobalConfig
        if not 'kadp_ctrl' in GlobalConfig:
            dlg=wx.MessageDialog(self,u'LTBNET没有启动，无法检测！',u'注意',wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if AlertOnOpen==True:
            evt = UpdateStatusBarEvent(FieldNum = 3, Value =u'正在检测端口是否开启...')
            wx.PostEvent(self, evt)
        GlobalConfig['kadp_ctrl'].checkPort(False)
        Tchkreport=ThreadChkPort(self,AlertOnOpen)
        Tchkreport.start()

    def Menu706(self,evt):
        self.chkPort()

    def Menu707(self,evt):
        if self.upnp_t != None and self.upnp_t.isAlive():
            return
        else:
            evt = UpdateStatusBarEvent(FieldNum = 3, Value =u'正在通过UPNP添加端口映射...')
            wx.PostEvent(self, evt)
            self.upnp_t = ThreadAddUPNPMapping(self)
            self.upnp_t.start()


    def AlertMsg(self,evt):
        dlg = wx.MessageDialog(self, evt.txt,u"注意！",wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def ChangeFontSize(self,delta):
        global GlobalConfig
        cur_size=GlobalConfig['CurFont'].GetPointSize()
        cur_size+=delta
        if cur_size<4:cur_size=4
        if cur_size>64:cur_size=64
        GlobalConfig['CurFont'].SetPointSize(cur_size)
        self.text_ctrl_1.SetFont(GlobalConfig['CurFont'])
        self.text_ctrl_1.ReDraw()

    def MyMouseMW(self,event):
        delta=event.GetWheelRotation()
        if delta>0:
            self.text_ctrl_1.ScrollLine(-1,1)
        elif delta<0:
            self.text_ctrl_1.ScrollLine(1,1)

##    def MyMouseMDC(self,event):
##        #self.last_mouse_event=1
##        if event.RightIsDown():
##            self.LoadNextFile(-1)
##        else:
##            self.LoadNextFile(1)
##        event.Skip(False)
##        event.StopPropagation()
##        clickEvent = wx.CommandEvent(wx.wxEVT_COMMAND_LEFT_CLICK, self.text_ctrl_1.GetId())
##        self.text_ctrl_1.ProcessEvent(clickEvent)


    def ShowPopMenu(self,event):
        if not self.showfullscr:
            if not hasattr(self,"popupID_1"):
                self.popupID_1=wx.NewId()
                self.popupID_2=wx.NewId()
                self.popupID_3=wx.NewId()
                self.popupID_4=wx.NewId()
                self.popupID_5=wx.NewId()
                self.text_ctrl_1.Bind(wx.EVT_MENU, self.OnFullScrMenu, id=self.popupID1)
            menu = wx.Menu()
            item = wx.MenuItem(menu, self.popupID1,u"拷贝")
            menu.Append(self.popupID_2, u"全选")
            menu.Break()
            menu.Append(self.popupID_3,u"切换工具栏")
            menu.Append(self.popupID_4,u"切换全屏显示")
            menu.Append(self.popupID_5,u"切换文件侧边栏")
            menu.AppendItem(item)
            self.text_ctrl_1.PopupMenu(menu)
            menu.Destroy()
        else:
            event.Skip()

    def ShowFullScrMenu(self,event):
        if self.showfullscr:
            if not hasattr(self,"popupID1"):
                self.popupID1=wx.NewId()
                self.text_ctrl_1.Bind(wx.EVT_MENU, self.OnFullScrMenu, id=self.popupID1)
            menu = wx.Menu()
            item = wx.MenuItem(menu, self.popupID1,u"关闭全屏")
            menu.AppendItem(item)
            self.text_ctrl_1.PopupMenu(menu)
            menu.Destroy()
        else:
            event.Skip()

    def OnFullScrMenu(self,event):
        self.ShowFullScreen(False,wx.FULLSCREEN_ALL)
        self.text_ctrl_1.Bind(wx.EVT_CONTEXT_MENU, None)
        self.showfullscr=False
        self.ViewMenu.Check(503,False)


    def OnSScroll(self,evt):
        tval=self.sliderControl.GetValue()
        if tval<>100:
            tpos=int(float(self.text_ctrl_1.ValueCharCount)*(float(tval)/100.0))
            self.text_ctrl_1.JumpTo(tpos)
        else:
            self.text_ctrl_1.ScrollBottom()
        self.text_ctrl_1.SetFocus()


    def Tool41(self, event): # wxGlade: MyFrame.<event_handler>
        txt=self.text_ctrl_1.GetValue()
        txt=htm2txt(txt)
##        of=codecs.open(u'1.txt',encoding='gbk',mode='w')
##        of.write(txt)
##        of.close()
        self.text_ctrl_1.SetValue(txt)



    def Tool42(self, event): # wxGlade: MyFrame.<event_handler>
        txt=self.text_ctrl_1.GetValue()
        txt=txt.encode('utf-8')
#        txt=jft.f2j('utf-8','utf-8',txt)
        txt=FtoJ(txt)
        txt=txt.decode('utf-8')
        pos=self.GetCurrentPos()
        self.text_ctrl_1.SetValue(txt)
        self.text_ctrl_1.JumpTo(pos)

    def Tool43(self, event): # wxGlade: MyFrame.<event_handler>
        txt=self.text_ctrl_1.GetValue()
        txt=txt.encode('utf-8')
#        txt=jft.j2f('utf-8','utf-8',txt)
        txt=JtoF(txt)
        txt=txt.decode('utf-8')
        pos=self.GetCurrentPos()
        self.text_ctrl_1.SetValue(txt)
        self.text_ctrl_1.JumpTo(pos)


    def fenduan(self):  #HJ: auto optimize the paragraph layout
        self.BackupValue=self.text_ctrl_1.GetValue()
        istr=self.text_ctrl_1.GetValue()
        #convert more than 3 newlines in a row into one newline
        p=re.compile('([ \t\f\v]*\n){2,}',re.S)
        istr=p.sub("\n",istr)
        #find out how much words can current line hold
        mmm=self.text_ctrl_1.GetClientSizeTuple()
        f=self.text_ctrl_1.GetFont()
        dc=wx.WindowDC(self.text_ctrl_1)
        dc.SetFont(f)
        nnn,hhh=dc.GetTextExtent(u"国")
        line_capacity=mmm[0]/nnn
        #combile short-lines together
        p=re.compile(".*\n")
        line_list=p.findall(istr)
        i2=[]
        last_len=0
        #cc=0
        line_start=True
        for line in line_list:
            cur_len=len(line)
            if cur_len<line_capacity-2:
                if cur_len>last_len-3:
                    if not line_start:
                        line=line.strip()
                    else:
                        line=line.rstrip()
                        line_start=False
                    #line=line[:-1]
                    #cc+=1
                else:
                    line_start=True
            i2.append(line)
            last_len=cur_len
        self.text_ctrl_1.SetValue("".join(i2))

    def Tool44(self,event):
        if self.Formated:
            self.text_ctrl_1.SetValue(self.BackupValue)
            self.FormatMenu.Check(504,False)
            self.frame_1_toolbar.ToggleTool(44,False)
        else:
            self.fenduan()
            self.FormatMenu.Check(504,True)
            self.frame_1_toolbar.ToggleTool(44,True)
        self.Formated=not self.Formated


# end of class MyFrame



    def LoadFile(self, filepath,type='file',zipfilepath='',openmethod='load',pos=0,startup=False):
        global GlobalConfig,current_file,current_file_list,current_zip_file,load_zip,OnScreenFileList,CurOnScreenFileIndex, MYOS
        utext=u''
        ii=0#this is used increase randombility of LiteBook-ID
        if self.text_ctrl_1.GetValue()<>'':self.SaveBookDB()
        if openmethod=='load':
            self.buff=""
            OnScreenFileList=[]
        if startup==False:
            ldlg = GMD.GenericMessageDialog(self, u' 正在载入。。。',u"载入中...",wx.ICON_INFORMATION)
            ldlg.Show()
            ldlg.Refresh()
            ldlg.Update()

        else:
            ldlg=GMD.GenericMessageDialog(self, u' 正在载入。。。',u"载入中...",wx.ICON_INFORMATION)

        if type=='file':
            if os.path.isfile(filepath[0])==False:
                ldlg.Destroy()
                return False
            if filepath[0].strip()<>'':GlobalConfig['LastDir']=os.path.split(filepath[0])[0]
            else:
                ldlg.Destroy()
                return
            load_zip=False
            self.GenList('file')
            for eachfile in filepath:
                ii+=1
                if os.path.isfile(eachfile):
                    file_ext=os.path.splitext(eachfile)[1].lower()
                    if file_ext==".jar":
                        utext=jarfile_decode(eachfile)
                        if utext==False:
                            dlg = wx.MessageDialog(self, eachfile+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                            dlg.ShowModal()
                            dlg.Destroy()
                            ldlg.Destroy()
                            return False
                        m=hashlib.md5()
                        eachfile=eachfile.encode('gbk')
                        if GlobalConfig['HashTitle']==False:
                            m.update(utext.encode('gbk','ignore'))
                        else:
                            m.update(os.path.split(eachfile)[1])
                        eachfile=eachfile.decode('gbk')
                        hashresult=m.hexdigest()
                        fsize=utext.__len__()
                    else:
                        if file_ext==".umd":
                            umdinfo=umd_decode(eachfile)
                            if umdinfo==False:
                                dlg = wx.MessageDialog(self, eachfile+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                                dlg.ShowModal()
                                dlg.Destroy()
                                ldlg.Destroy()
                                return False
                            utext=umdinfo['Content']
                            m=hashlib.md5()
                            eachfile=eachfile.encode('gbk')
                            if GlobalConfig['HashTitle']==False:
                                m.update(utext.encode('gbk','ignore'))
                            else:
                                m.update(os.path.split(eachfile)[1])
                            eachfile=eachfile.decode('gbk')
                            hashresult=m.hexdigest()
                            fsize=utext.__len__()
                        else:
                            if file_ext==".epub":
                                utext=epubfile_decode(eachfile)
                                if utext==False:
                                    dlg = wx.MessageDialog(self, eachfile+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                                    dlg.ShowModal()
                                    dlg.Destroy()
                                    ldlg.Destroy()
                                    return False
                                m=hashlib.md5()
                                eachfile=eachfile.encode('gbk')
                                if GlobalConfig['HashTitle']==False:
                                    m.update(utext.encode('gbk','ignore'))
                                else:
                                    m.update(os.path.split(eachfile)[1])
                                eachfile=eachfile.decode('gbk')
                                hashresult=m.hexdigest()
                                fsize=utext.__len__()
                            else:
                                coding=DetectFileCoding(eachfile)
                                if coding=='error':
                                    ldlg.Destroy()
                                    return False
                                try:
                                    file_handler=open(eachfile,'rb')
                                    t_buff=file_handler.read()
                                except:
                                    dlg = wx.MessageDialog(self, eachfile+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                                    dlg.ShowModal()
                                    dlg.Destroy()
                                    ldlg.Destroy()
                                    return False
                                m=hashlib.md5()
                                if GlobalConfig['HashTitle']==False:
                                    m.update(t_buff)
                                else:
                                    eachfile=eachfile.encode('gbk')
                                    m.update(os.path.split(eachfile)[1])
                                    eachfile=eachfile.decode('gbk')
                                hashresult=m.hexdigest()
                                utext=AnyToUnicode(t_buff,coding)
                                fsize=utext.__len__()
                                if file_ext=='.htm' or file_ext=='.html':utext=htm2txt(utext)

                    id=utext.__len__()+ii
                    OnScreenFileList.append((eachfile,id,fsize,hashresult))
                    self.text_ctrl_1.Clear()
                    if self.buff<>'': self.buff+="\n\n"
                    self.buff+="--------------"+eachfile+"--------------LiteBook-ID:"+unicode(id)+u"\n\n"
                    self.buff+=utext
                    self.text_ctrl_1.SetValue(self.buff)
                    UpdateOpenedFileList(eachfile,'normal')
                    self.UpdateLastFileMenu()
                    self.frame_1_statusbar.SetStatusText(os.path.split(eachfile)[1])
                    current_file=eachfile
                    current_zip_file=''




        else:
            if os.path.isfile(zipfilepath)==False:
                ldlg.Destroy()
                return False
            if type=='zip':
                if os.path.isfile(zipfilepath):
                    file_ext=os.path.splitext(zipfilepath)[1].lower()
                    if file_ext=='.zip':
                        load_zip=True
                        current_zip_file=zipfilepath
                        try:
                            if isinstance(zipfilepath, str):
                                zipfilepath=zipfilepath.decode('gbk')
                            zfile=zipfile.ZipFile(zipfilepath)
                        except:
                            dlg = wx.MessageDialog(self, zipfilepath+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                            dlg.ShowModal()
                            dlg.Destroy()
                            ldlg.Destroy()
                            return False

                        for eachfile in filepath:
                            ii+=1
                            each_ext=os.path.splitext(eachfile)[1].lower()
##                            if each_ext in ('.txt','.html','.htm'):
                                #print chardet.detect(eachfile)['encoding']
                            #eachfile=eachfile.encode('gbk')
                            coding=DetectFileCoding(eachfile,'zip',zipfilepath)
                            if coding=='error':
                                ldlg.Destroy()
                                return False
                            try:
                                if isinstance(eachfile, unicode):
                                    eachfile=eachfile.encode('gbk')
                                t_buff=zfile.read(eachfile)
#                                t_buff=file_handler.read()
                            except:
                                dlg = wx.MessageDialog(self, eachfile+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                                dlg.ShowModal()
                                dlg.Destroy()
                                ldlg.Destroy()
                                return False
                            m=hashlib.md5()
                            if GlobalConfig['HashTitle']==False:
                                m.update(t_buff)
                            else:
                                m.update(os.path.split(eachfile)[1])
                            hashresult=m.hexdigest()

                            utext=AnyToUnicode(t_buff,coding)
                            fsize=utext.__len__()
                            if each_ext in ('.htm','.html'): utext=htm2txt(utext)

                            id=utext.__len__()+ii
                            OnScreenFileList.append((zipfilepath+u'|'+eachfile.decode('gbk'),id,fsize,hashresult))

                            self.text_ctrl_1.Clear()
                            if self.buff<>'': self.buff+="\n\n"
                            self.buff+=u"--------------"+zipfilepath+u' | '+eachfile.decode('gbk')+u"--------------LiteBook-ID:"+unicode(id)+u"\n\n"
                            self.buff+=utext
                            self.text_ctrl_1.SetValue(self.buff)
##                            GlobalConfig['CurFont'].SetPointSize(GlobalConfig['CurFont'].GetPointSize()+2)
##                            self.text_ctrl_1.SetFont(GlobalConfig['CurFont'])
##                            GlobalConfig['CurFont'].SetPointSize(GlobalConfig['CurFont'].GetPointSize()-2)
##                            self.text_ctrl_1.SetFont(GlobalConfig['CurFont'])
##                            self.text_ctrl_1.SetForegroundColour(GlobalConfig['CurFColor'])
##                            self.text_ctrl_1.SetBackgroundColour(GlobalConfig['CurBColor'])
##                            self.text_ctrl_1.Refresh()
##                            self.text_ctrl_1.Update()

                            UpdateOpenedFileList(eachfile.decode('gbk'),'zip',zipfilepath)
                            current_file=eachfile.decode('gbk')
                        self.GenList(zipfilepath)
                    else:
                        if file_ext=='.rar':
                            load_zip=True
                            current_zip_file=zipfilepath
                            for eachfile in filepath:
                                ii+=1
                                if MYOS == 'Windows':
                                    try:
                                        rfile=UnRAR2.RarFile(zipfilepath)
                                    except:
                                        dlg = wx.MessageDialog(self, zipfilepath+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                                        dlg.ShowModal()
                                        dlg.Destroy()
                                        ldlg.Destroy()
                                        return False
                                    each_ext=os.path.splitext(eachfile)[1].lower()
                                    if isinstance(eachfile,unicode):
                                        eachfile=eachfile.encode('gbk')
                                    coding=DetectFileCoding(eachfile,'rar',zipfilepath)
                                    if coding=='error':
                                        ldlg.Destroy()
                                        return False
                                    try:
                                        file_handler=rfile.read_files(eachfile)
                                    except:
                                        dlg = wx.MessageDialog(self, eachfile+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                                        dlg.ShowModal()
                                        dlg.Destroy()
                                        ldlg.Destroy()
                                        return False
                                    t_buff=file_handler[0][1]
                                else:
                                    t_buff=unrar(zipfilepath,eachfile)
                                    if t_buff==False:
                                        dlg = wx.MessageDialog(self, zipfilepath+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                                        dlg.ShowModal()
                                        dlg.Destroy()
                                        ldlg.Destroy()
                                        return False
                                    each_ext=os.path.splitext(eachfile)[1].lower()
                                    if isinstance(eachfile,unicode):
                                        eachfile=eachfile.encode('gbk')
                                    #eachfile=eachfile.encode('gbk')
                                    coding=DetectFileCoding(eachfile,'rar',zipfilepath)
                                    if coding=='error':
                                        ldlg.Destroy()
                                        return False
                                m=hashlib.md5()
                                if GlobalConfig['HashTitle']==False:
                                    m.update(t_buff)
                                else:
                                    m.update(os.path.split(eachfile)[1])
                                if isinstance(eachfile,str):
                                    eachfile=eachfile.decode('gbk')
                                hashresult=m.hexdigest()
                                utext=AnyToUnicode(t_buff,coding)
                                fsize=utext.__len__()
                                if each_ext in ('.htm','.html'): utext=htm2txt(utext)
                                id=utext.__len__()+ii
                                OnScreenFileList.append((zipfilepath+u'|'+eachfile,id,fsize,hashresult))

                                self.text_ctrl_1.Clear()
                                if self.buff<>'': self.buff+="\n\n"
                                self.buff+=u"--------------"+zipfilepath+u'|'+eachfile+u"--------------LiteBook-ID:"+unicode(id)+u"\n\n"
                                self.buff+=utext
                                self.text_ctrl_1.SetValue(self.buff)

                                UpdateOpenedFileList(eachfile,'rar',zipfilepath)
                                current_file=eachfile
                            self.GenList(zipfilepath)
        tpos=0
        if pos<>0:
            tpos=pos
        else:
            if openmethod=='load':
                for bk in BookDB:
                    if bk['key']==unicode(hashresult):
                        tpos=bk['pos']
                        break

        if tpos<>0:self.text_ctrl_1.JumpTo(tpos)

        #Auto Format the paragraph if it is enabled
        if self.FormatMenu.IsChecked(504):
            self.fenduan()
            self.Formated=not self.Formated

        #fresh sth
        self.SetTitle(self.title_str+filepath[0])
        self.cur_catalog=None
        self.text_ctrl_1.SetFocus()
        ldlg.Destroy()







    def LoadNextFile(self, next):
        global current_file,GlobalConfig,current_file_list,current_zip_file,load_zip,MYOS
        #print "curen file is ",current_file_list
        load_file=[]
        if current_file=='' or current_file_list==[]:
            dlg = wx.MessageDialog(self, u'请先打开一个文件！',u"提示！",wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if str(type(current_file))=="<type 'str'>":
            try:
                current_file=unicode(current_file,'gbk')
            except:
                current_file=unicode(current_file,'big5')
        current_file_list=sorted(current_file_list,cmp=lambda x,y:cmp(ch2num(x),ch2num(y)))
        try:
            id=current_file_list.index(current_file)
        except:
            if MYOS == 'Windows':
                xf=current_file.replace("/","\\")
            id=current_file_list.index(current_file)


        id+=next
        if id<0 or id>=current_file_list.__len__():
            dlg = wx.MessageDialog(self, u'到头了！',u"提示！",wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            if not load_zip:
                load_file.append(current_file_list[id])
                self.LoadFile(load_file)
            else:
                load_file.append(current_file_list[id])
                self.LoadFile(load_file,'zip',current_zip_file)


    def GenList(self, zip):
        global current_file,GlobalConfig,current_file_list,current_zip_file,load_zip
        current_file_list=[]
        if zip=='file':
            flist=os.listdir(GlobalConfig['LastDir'])
            for eachfile in flist:

                cur_path=GlobalConfig['LastDir']+os.sep+eachfile
                if not os.path.isdir(cur_path):
                    file_ext=os.path.splitext(cur_path)[1].lower()
                    if file_ext in ('.txt','.htm','.html','.umd','.jar'):

                        current_file_list.append(cur_path)
        else:
            prefix=os.path.dirname(current_file)
            cur_ext=os.path.splitext(zip)[1].lower()
            if cur_ext=='.zip':
                zfile=zipfile.ZipFile(zip)
                flist=zfile.namelist()
            else:
                if cur_ext=='.rar':
                    rfile=rarfile.RarFile(zip)
                    flist=rfile.namelist()
                    #print flist
            for eachfile in flist:
                if os.path.split(eachfile)[1]<>'':
                    file_ext=os.path.splitext(eachfile)[1].lower()
                    if file_ext in ('.txt','.htm','.html'):
                        if not isinstance(eachfile, unicode):
                            try:
                                utext=eachfile.decode('gbk')
                            except:
                                utext=eachfile.decode('big5')
                        else:
                            utext=eachfile
                        utext=utext.replace("\\","/")
                        myprefix=os.path.dirname(utext)
                        if myprefix==prefix or myprefix.replace("\\","/")==prefix:
                            current_file_list.append(utext)






    def OnChar3(self, event):
        global KeyConfigList
        key=event.GetKeyCode()
        if key==wx.WXK_RETURN or key==wx.WXK_TAB:
            self.list_ctrl_1.SetFocus()
##            self.list_ctrl_1.Select(self.list_ctrl_1.GetNextItem(-1))
        else:
            if key==wx.WXK_ESCAPE:
                self.Menu502(None)
            else:
                event.Skip()

##    def OnCloseSiderbar(self,evt):
##        global KeyConfigList
##        kstr=keygrid.key2str(evt)
##        for kconfig in KeyConfigList:
##            if kconfig[0]=='last':
##                break
##        i=1
##        tl=len(kconfig)
##        while i<tl:
##            if kconfig[i][0]==u'显示文件侧边栏':
##                break
##            i+=1
##        if kstr==kconfig[i][1]:
##            self.CloseSidebar()



    def OnChar2(self, event):
        key=event.GetKeyCode()
        if key==wx.WXK_TAB:
            if self.window_1_pane_1.IsShown():
                self.text_ctrl_2.SetFocus()
        else:
            if key==wx.WXK_ESCAPE:
                if self.window_1_pane_mulu.IsShown():
                    self.window_1.Unsplit(self.window_1_pane_mulu)
                elif self.window_1_pane_1.IsShown():
                    self.window_1.Unsplit(self.window_1_pane_1)
                self.text_ctrl_1.SetFocus()
            else:
                event.Skip()



    def OnChar(self,evt):
        global KeyConfigList
        keystr=keygrid.key2str(evt)
        for kconfig in KeyConfigList:
            if kconfig[0]=='last':
                break
        i=1
        tl=len(kconfig)
        while i<tl:
            if keystr==kconfig[i][1]:break
            i+=1
        if i>=tl:
            evt.Skip()
            return
        else:
            eval(self.func_list[kconfig[i][0]])


##    def OnChar(self, event):
##        usedKeys=(wx.WXK_HOME,wx.WXK_END,wx.WXK_PAGEDOWN,wx.WXK_PAGEUP,wx.WXK_LEFT,wx.WXK_SPACE,wx.WXK_RIGHT,15,70,72,74,wx.WXK_ESCAPE,wx.WXK_TAB,wx.WXK_RETURN)
##        CTRL=2
##        ALT=1
##        SHIFT=4
##        key=event.GetKeyCode()
##        Mod=event.GetModifiers()
##        if key == wx.WXK_PAGEDOWN or key==wx.WXK_SPACE:
##            self.text_ctrl_1.ScrollP(1)
##            return
##        if key==wx.WXK_RIGHT:
##            if Mod==0:
##                self.text_ctrl_1.ScrollP(1)
##                return
##            else:
##                if Mod==2:
##                    self.LoadNextFile(1)
##                    return
##        if key==wx.WXK_LEFT:
##            if Mod==0:
##                self.text_ctrl_1.ScrollP(-1)
##                return
##            else:
##                if Mod==2:
##                    self.LoadNextFile(-1)
##                    return
##        if key == wx.WXK_PAGEUP:
##            self.text_ctrl_1.ScrollP(-1)
##            return
##        if key == wx.WXK_HOME :
##            self.text_ctrl_1.ScrollTop()
##            return
##        if key == wx.WXK_END :
##            self.text_ctrl_1.ScrollBottom()
##            return
##        if key == 12: # Ctrl+L to pop up OnScreenFileList dialog
##           self.ChoseOnScreenFile()
##        if key == 15: # Ctrl+O to open files
##            self.Menu101(self)
####        if key==wx.WXK_ESCAPE:
####            self.Iconize()
##        if key==wx.WXK_RETURN:
##            self.autoscroll=not self.autoscroll
##        if key==72: #ALT+H, filter out HTML tag
##            self.Tool41(None)
##
##        if key==74: #ALT+J, Fan to Jian
##            self.Tool42(None)
##
##        if key==70: #ALT+F, Jian to Fan
##            self.Tool43(None)
##
##        if key not in usedKeys:
##            #print key
##            event.Skip()

    def OnFind(self, event):
        fstr=event.GetFindString()
        flag=event.GetFlags()
        fstr=fstr.strip()
        if self.last_search_pos==False: self.last_search_pos=self.text_ctrl_1.start_pos
        if fstr<>'':
            if fstr<>self.search_str:
                self.search_str=fstr
                pos=self.text_ctrl_1.Find(fstr,self.text_ctrl_1.start_pos)
            else:
                if flag&wx.FR_DOWN:
                    pos=self.text_ctrl_1.Find(fstr,self.last_search_pos+1)
                else:
                    pos=self.text_ctrl_1.Find(fstr,self.last_search_pos-1,-1)
            if pos==False:
                dlg = wx.MessageDialog(self, u'没有找到"'+fstr+u'"',u"查找失败！",wx.OK|wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
##                self.text_ctrl_1.SetSelection(pos,pos+fstr.__len__())
##                self.text_ctrl_1.ShowPosition(pos)
                self.last_search_pos=pos
        self.search_str=fstr
        self.search_flg=flag
        #event.GetDialog().Destroy()



    def OnFindClose(self, event):
        event.GetDialog().Destroy()

    def FindNext(self):
        if self.search_str=='': return
        if self.last_search_pos==False: self.last_search_pos=self.text_ctrl_1.start_pos
        if self.search_flg&wx.FR_DOWN:
            pos=self.text_ctrl_1.Find(self.search_str,self.last_search_pos+1)
        else:
            pos=self.text_ctrl_1.Find(self.search_str,self.last_search_pos-1,-1)
        if pos==False:
            dlg = wx.MessageDialog(self, u'没有找到"'+self.search_str+u'"',u"查找失败！",wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
##        self.text_ctrl_1.SetSelection(pos,pos+self.search_str.__len__())
##        self.text_ctrl_1.ShowPosition(pos)
        self.last_search_pos=pos

    def OnReplace(self,evt):
        fstr=evt.GetFindString()
        rstr=evt.GetReplaceString()
        flag=evt.GetFlags()
        buf=self.text_ctrl_1.GetValue()
        if evt.GetEventType()==wx.wxEVT_COMMAND_FIND_REPLACE:
            pos=self.text_ctrl_1.GetValue().find(fstr,self.text_ctrl_1.start_pos)
            #self.text_ctrl_1.JumpTo(pos)
            buf=buf[:pos]+buf[pos:].replace(fstr,rstr,1)
            self.text_ctrl_1.SetValue(buf)
            self.last_search_pos=pos
            self.text_ctrl_1.JumpTo(pos)
        else:
            buf=buf.replace(fstr,rstr)
            self.text_ctrl_1.SetValue(buf)
            evt.GetDialog().Destroy()

    def OpenLastFile(self, event):
        global OpenedFileList
        id=event.GetId()
        for f in OpenedFileList:
            if f['MenuID']==id:
                flist=[]
                flist.append(f['file'])
                if f['type']=='normal':
                    self.LoadFile(flist)
                else:
                    self.LoadFile(flist,'zip',f['zfile'])
                break

    def OnESC(self,event):
        if self.IsIconized():
            self.Iconize(False)
        else:
            self.Iconize()

    def OnClose(self, event):
        global OnDirectSeenPage,GlobalConfig,writeKeyConfig,MYOS,SqlCon
        try:
            SqlCon.commit()
            SqlCon.close()
        except:
            pass
        self.Hide()
        if MYOS == 'Linux':
            print "closing..."
        SqlCon.close()
        self.clk_thread.stop()
        self.display_pos_thread.stop()
        self.auto_count_thread.stop()
        if self.KPUB_thread != None: self.KPUB_thread.stop()
        time.sleep(1)
        GlobalConfig['CurFontData']=self.text_ctrl_1.GetFont()
        GlobalConfig['CurFColor']=self.text_ctrl_1.GetFColor()
        GlobalConfig['CurBColor']=self.text_ctrl_1.GetBackgroundColour()
        if self.GetToolBar()==None:
            GlobalConfig['HideToolbar']=True
        else:
            GlobalConfig['HideToolbar']=not self.GetToolBar().IsShown()


        if OnDirectSeenPage:
            writeConfigFile(GlobalConfig['LastPos'])
        else:
            writeConfigFile(self.GetCurrentPos())
        mbar=self.GetMenuBar()
        if mbar.IsChecked(705):
            self.server.shutdown()
        if self.mDNS<>None:
            self.mDNS.close()
        #stop KADP
##        print "start to stop KADP"
        if 'kadp_ctrl' in GlobalConfig:
            kadp_ctrl = GlobalConfig['kadp_ctrl']
    ##        kadp_ctrl.preparestop(False)
    ##        print "start to kill KADP"
    ##        self.KADP_Process.kill()
    ##        print "finish stop KADP"

            try:
                kadp_ctrl.stopall(False)
            except:
                try:
                    self.KADP_Process.kill()
                except:
                    pass

    ##            if MYOS != 'Windows':
    ##                os.kill(self.KADP_Process.pid, signal.SIGKILL)
    ##            else:
    ##                os.kill(self.KADP_Process.pid, signal.CTRL_C_EVENT)
        writeKeyConfig()
        event.Skip()



    def GetCurrentPos(self):
        return self.text_ctrl_1.GetStartPos()


    def ChoseOnScreenFile(self):
        global OnScreenFileList
        fl=[]
        for f in OnScreenFileList:
           fl.append(f[0])
        dlg=wx.SingleChoiceDialog(
            self, u'当前已经打开的文件列表', u'选择当前已打开的文件',
            fl,
            wx.CHOICEDLG_STYLE
            )
        if dlg.ShowModal() == wx.ID_OK:
           selected=dlg.GetStringSelection()
           for f in OnScreenFileList:
               if f[0]==selected:
                   selected_id=f[1]
                   break
           pos=self.text_ctrl_1.GetValue().find(u"LiteBook-ID:"+unicode(selected_id))
           self.text_ctrl_1.ShowPosition(pos)
        dlg.Destroy()

    def LoadBookmark(self,filename,tpos):
        global OnScreenFileList
        self.text_ctrl_1.Clear()
        self.buff=""
        current_file=''
        OnScreenFileList=[]
        flist=[]
        if filename.find('*')==-1:
            if filename.find("|")==-1:
                flist.append(filename)
                self.LoadFile(flist,pos=tpos)
            else:
                (zfile,file)=filename.split("|")
                flist.append(file)
                self.LoadFile(flist,'zip',zfile,pos=tpos)
        else:
            for f in filename.split('*'):
                flist=[]
                if f.find('|')==-1:
                    flist.append(f)
                    self.LoadFile(flist,openmethod='append')
                else:
                    flist.append(f.split('|')[1])
                    self.LoadFile(flist,'zip',f.split('|')[0].strip(),openmethod='append')
            self.text_ctrl_1.ShowPosition(tpos)


    def OnWinActive(self,event):
        global Ticking
        if event.GetActive():
            if self.window_1.IsSplit():
                self.list_ctrl_1.SetFocus()
            else:
                self.text_ctrl_1.SetFocus()
            Ticking=True
        else:
            Ticking=False


    def SaveBookDB(self):
        global OnScreenFileList,BookDB,OnDirectSeenPage,GlobalConfig
        pos=self.GetCurrentPos()
##        tsize=0
##        i=0
##        for f in OnScreenFileList:
##            tsize+=f[2]
##            if pos<tsize: break
##            i+=1
##        id=i-1
##        hash_id=OnScreenFileList[id][3]
##        i=0
##        tsize=0
##        while i<id:
##            pos-=OnScreenFileList[i][2]
        if OnScreenFileList.__len__()>1: return #if there is multiple on scrren file, the the pos will not be remembered
        try:
            hash_id=OnScreenFileList[0][3]
        except:
            return
        for bk in BookDB:
            if bk['key']==hash_id:
                if OnDirectSeenPage: GlobalConfig['LastPos']=pos
                bk['pos']=pos
                return
        BookDB.insert(0,{'key':hash_id,'pos':pos})
        if BookDB.__len__()>GlobalConfig['MaxBookDB']:
            BookDB.pop()

##    def DisplayPos(self,event):
##        global OnScreenFileList
##        while(True):
##            try:
##                pos=self.GetCurrentPos()[0]
##                last_pos=self.text_ctrl_1.GetLastPosition()
##            except:
##                return
##            if last_pos<>0:
##                percent=int((float(pos)/float(last_pos))*100)
##                allsize=0
##                i=0
##                pos+=2700
##                for f in OnScreenFileList:
##                    allsize+=f[2]
##                    if pos<allsize: break
##                    i+=1
##                if i>=OnScreenFileList.__len__():
##                    i=OnScreenFileList.__len__()-1
##                fname=OnScreenFileList[i][0]
##                try:
##                    self.frame_1_statusbar.SetStatusText(fname+u' , '+unicode(percent)+u'%',0)
##                except:
##                    return
##            time.sleep(0.5)

    def UpdateStatusBar(self,event):
        if event.FieldNum<>0:
            self.frame_1_statusbar.SetStatusText(event.Value,event.FieldNum)
        else:
            self.frame_1_statusbar.SetStatusText(event.Value,event.FieldNum)
##            dc=wx.ClientDC(self.frame_1_statusbar)
##            field=self.frame_1_statusbar.GetFieldRect(0)
##            field_len=field[2]-field[0]
##            txt=event.Value
##            txt_len=dc.GetTextExtent(txt)[0]
##            if txt_len>field_len:
##                tlist=txt.split(os.sep)
##                print tlist
##                m=len(tlist)
##                txt=txt[:6]+u'.../'+tlist[m-2]+u"/"+tlist[m-1]

##            self.frame_1_statusbar.SetStatusText(txt,0)
            pos=int(self.text_ctrl_1.GetPosPercent())
            self.sliderControl.SetValue(pos)
    def ReadTimeAlert(self,event):
        ttxt=u'现在是'+time.strftime("%H:%M:%S",time.localtime())+"\n"
        ttxt+=u'你已经连续阅读了'+event.ReadTime
        dlg = wx.MessageDialog(self, ttxt,u"友情提示！",wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def scrolldownpage(self,event):
        self.text_ctrl_1.ScrollP(1)
        self.text_ctrl_1.ReDraw()


##    def getPos(self,event):
##        try:
##            self.current_pos=self.GetCurrentPos()
##            self.last_pos=self.text_ctrl_1.GetLastPosition()
##        except:
##            self.current_pos=0
##            self.last_pos=0

#    def MyMouseMDC(self,event):
#        self.last_mouse_event=1
#        if event.LeftIsDown():
#            self.LoadNextFile(-1)
#        else:
#            self.LoadNextFile(1)
#        event.Skip(False)
#        event.StopPropagation()
#        clickEvent = wx.CommandEvent(wx.wxEVT_COMMAND_LEFT_CLICK, self.text_ctrl_1.GetId())
#        self.text_ctrl_1.ProcessEvent(clickEvent)
#
#
#    def MyMouseRU(self,event):
#        if self.last_mouse_event==1:
#            self.last_mouse_event=0
#            return
#        else:
#            event.Skip()
#
#    def MyMouseMW(self,event):
#        delta=event.GetWheelRotation()
#        if event.RightIsDown():
#            self.last_mouse_event=1
#            if delta>0:
#                self.text_ctrl_1.ScrollPages(-1)
#            else:
#                self.text_ctrl_1.ScrollPages(1)
#        else:
#            event.Skip()
#
#    def MyMouseMDW(self,event):
#        if self.last_mouse_event==1:
#            self.last_mouse_event=0
#            return
#        else:
#            event.Skip()


    def DirSideBarReload(self):
        """"This function is to reload directory sidebar with GlobalConfig['LastDir']"""
        global GlobalConfig, MYOS
        if GlobalConfig['LastDir']==self.LastDir and not self.UpdateSidebar:
            return
        else:
            self.UpdateSidebar=False
            if MYOS == 'Windows':
                if ((self.LastDir.__len__()>GlobalConfig['LastDir'].__len__() and not (self.LastDir=='ROOT' and GlobalConfig['LastDir'][1:]==u':\\')))or GlobalConfig['LastDir']==u'ROOT':
                    RestorPos=True
                    if GlobalConfig['LastDir']=='ROOT':
                        RestorPosName=self.LastDir
                    else:
                        RestorPosName=self.LastDir.rsplit('\\',1)[1]
                else:
                    RestorPos=False
            else:
                if self.LastDir=='':
                    RestorPos=False
                else:
                    RestorPos=True
                    if GlobalConfig['LastDir']==u'/':
                        RestorPosName=self.LastDir
                        RestorPosName=self.LastDir[1:]
                    else:
                        RestorPosName=self.LastDir.rsplit(u'/',1)[1]
            self.LastDir=GlobalConfig['LastDir']

        #current_ext=os.path.splitext(GlobalConfig['LastDir'])[1].lower()
        self.sideitemlist=[]
        sideitem={}
        newitem=wx.ListItem()
        newitem.SetText(GlobalConfig['LastDir'])
        self.list_ctrl_1.SetColumn(0,newitem)

        self.list_ctrl_1.DeleteAllItems()
        if str(type(GlobalConfig['LastDir']))=='<type \'str\'>':
            GlobalConfig['LastDir']=unicode(GlobalConfig['LastDir'],'GBK','ignore')
        if MYOS == 'Windows':
            if GlobalConfig['LastDir']<>u'ROOT' and os.path.exists(GlobalConfig['LastDir']):
                current_ext=os.path.splitext(GlobalConfig['LastDir'])[1].lower()
                self.list_ctrl_1.DeleteAllItems()
                try:
                    tlist=os.listdir(GlobalConfig['LastDir'])

                except:
                    dlg = wx.MessageDialog(None, GlobalConfig['LastDir']+u' 目录打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,"..",self.file_icon_list['folder'])
                    self.list_ctrl_1.SetItemData(index,index)
                    self.itemDataMap[index]=('\x01'+u"..",)
                    self.sideitemlist.append({'py':u'..','item':self.list_ctrl_1.GetItem(index)})
                    self.window_1_pane_1.SetFocus()
                    self.list_ctrl_1.SetFocus()
                    self.list_ctrl_1.Focus(0)
                    return
                file_list=[]
                for m in tlist:
                    if not isinstance(m,unicode):
                        m=m.decode('gbk')
                    file_list.append(m)
            else:
                #List all windows drives
                i=0
                RPos=0
                self.list_ctrl_1.DeleteAllItems()
                drive_list=[]
                drive_str = win32api.GetLogicalDriveStrings()
                drive_list=drive_str.split('\x00')
                drive_list.pop()
                for drive in drive_list:
                    index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,drive,self.file_icon_list['driver'])
                    if drive==RestorPosName:RPos=i
                    self.list_ctrl_1.SetItemData(index,index)
                    self.itemDataMap[index]=('\x01'+drive,)
                    self.sideitemlist.append({'py':self.cnsort.strToPYS(drive.lower()),'item':self.list_ctrl_1.GetItem(index)})
                    i+=1


                key=self.text_ctrl_2.GetValue()
                self.UpdateSearchSidebar(key)
                self.list_ctrl_1.Focus(RPos)
                self.list_ctrl_1.Select(RPos)
                self.list_ctrl_1.Refresh()
                self.list_ctrl_1.Update()


                return


        else:
            try:
                file_list=os.listdir(GlobalConfig['LastDir'])
            except:
                dlg = wx.MessageDialog(None, GlobalConfig['LastDir']+u' 目录打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,"..",self.file_icon_list['folder'])
    #            Date_str=u""
    #            self.list_ctrl_1.SetStringItem(index,2,Date_str)
                self.list_ctrl_1.SetItemData(index,index)
                self.itemDataMap[index]=('\x01'+u"..",)
                self.sideitemlist.append({'py':u'..','item':self.list_ctrl_1.GetItem(index)})
                self.window_1_pane_1.SetFocus()
                self.list_ctrl_1.SetFocus()
                self.list_ctrl_1.Focus(0)
                return

        file_list.sort(key=unicode.lower)
        i=0
        index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,"..",self.file_icon_list['folder'])
        self.list_ctrl_1.SetItemData(index,index)
        self.itemDataMap[index]=('\x01'+u"..",)
        self.sideitemlist.append({'py':u'..','item':self.list_ctrl_1.GetItem(index)})

        i=0
        RPos=0
        bflist=[]
        for n in file_list:
            bflist.append(n)
        for filename in file_list:
            current_path=GlobalConfig['LastDir']+os.sep+filename+os.sep
            current_path=os.path.normpath(current_path)
            if os.path.isdir(current_path)== True:
                if RestorPos:
                    if filename==RestorPosName:
                        RPos=i
                index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['folder'])
#                statinfo = os.stat(current_path)
#                Date_str=unicode(datetime.fromtimestamp(statinfo.st_mtime))[:19]
#                self.list_ctrl_1.SetStringItem(index,2,Date_str)

                self.list_ctrl_1.SetItemData(index,index)
                self.sideitemlist.append({'py':self.cnsort.strToPYS(filename).lower(),'item':self.list_ctrl_1.GetItem(index)})
#                Date_str=''
                self.itemDataMap[index]=('\x01'+filename,)
                bflist.remove(filename)
                i+=1
        RPos+=1
        for filename in bflist:
            current_path=GlobalConfig['LastDir']+u"/"+filename
            rr=filename.rsplit('.',1)
            not_visable=False
            if rr.__len__()==1:
                file_ext=''
            else:
                file_ext=rr[1]
            if os.path.isdir(current_path)== False:
                if file_ext=='txt' :
                    index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['txtfile'])
                else:
                    if (file_ext=='htm' or file_ext=='html'):
                        index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['htmlfile'])
                    else:
                        if file_ext=='zip' :
                            index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['zipfile'])
                        else:
                            if file_ext=='rar':
                                index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['rarfile'])
                            else:
                                 if file_ext=='jar' :
                                     index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['jarfile'])
                                 else:
                                     if file_ext=='umd':
                                         index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['umdfile'])
                                     else:
                                         if file_ext=='epub':
                                             index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['epub'])
                                         else:
                                             if GlobalConfig['ShowAllFileInSidebar']:
                                                 index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['file'])
                                             else:
                                                 not_visable=True
#            self.list_ctrl_1.SetStringItem(index,1,file_size)
#            self.list_ctrl_1.SetStringItem(index,2,Date_str)
            if not_visable==False:
                self.list_ctrl_1.SetItemData(index,index)
                self.itemDataMap[index]=(filename,)
                self.sideitemlist.append({'py':self.cnsort.strToPYS(filename.lower()),'item':self.list_ctrl_1.GetItem(index)})

        key=self.text_ctrl_2.GetValue()
        self.UpdateSearchSidebar(key)
        self.list_ctrl_1.Focus(RPos)
        self.list_ctrl_1.Select(RPos)
        self.list_ctrl_1.Refresh()
        self.list_ctrl_1.Update()

    def OnItemActive(self,event):
        """Called when dir sidebar item was activated"""
        global MYOS
        self.PvFrame.Hide()
        global GlobalConfig
        item=event.GetItem()
        filename=item.GetText()
        if MYOS == 'Windows':
            if filename[1:]==":\\" and not os.path.isdir(filename):
                return False #means this driver is not ready
            if GlobalConfig['LastDir']<>"ROOT":
                current_path=GlobalConfig['LastDir']+u"\\"+filename
            else:
                current_path=filename
        else:
            if GlobalConfig['LastDir']<>'/':
                current_path=GlobalConfig['LastDir']+u"/"+filename
            else:
                current_path=GlobalConfig['LastDir']+filename
            current_path=os.path.normpath(current_path)

        current_ext=os.path.splitext(current_path)[1].lower()
        if os.path.isdir(current_path)== True:
            if MYOS == 'Windows':
                if current_path.find(":\\\\..")<>-1:
                    GlobalConfig['LastDir']=u"ROOT"
                else:
                    GlobalConfig['LastDir']=os.path.normpath(current_path)
            else:
                GlobalConfig['LastDir']=os.path.normpath(current_path)
            self.DirSideBarReload()
        else:
            if current_ext==".zip" or current_ext==".rar":
                dlg=ZipFileDialog(self,current_path)
                dlg.ShowModal()
                if dlg.selected_files<>[]:
                    self.LoadFile(dlg.selected_files,'zip',current_path,openmethod=dlg.openmethod)
                    dlg.Destroy()
                else:
                    dlg.Destroy()
            else:
                self.LoadFile([current_path,])

    def ActiveItem(self,filename):
        """manually active an item"""
        global MYOS
        self.PvFrame.Hide()
        if MYOS == 'Windows':
            if filename[1:]==":\\" and not os.path.isdir(filename):
                return False #means this driver is not ready
            if GlobalConfig['LastDir']<>"ROOT":
                current_path=GlobalConfig['LastDir']+u"\\"+filename
            else:
                current_path=filename
        else:
            if GlobalConfig['LastDir']<>'/':
                current_path=GlobalConfig['LastDir']+u"/"+filename
            else:
                current_path=GlobalConfig['LastDir']+filename
            current_path=os.path.normpath(current_path)

        current_ext=os.path.splitext(current_path)[1].lower()
        if os.path.isdir(current_path)== True:
            if MYOS == 'Windows':
                if current_path.find(":\\\\..")<>-1:
                    GlobalConfig['LastDir']=u"ROOT"
                else:
                    GlobalConfig['LastDir']=os.path.normpath(current_path)
            else:
                GlobalConfig['LastDir']=os.path.normpath(current_path)
            self.DirSideBarReload()
        else:
            if current_ext==".zip" or current_ext==".rar":
                dlg=ZipFileDialog(self,current_path)
                dlg.ShowModal()
                if dlg.selected_files<>[]:
                    self.LoadFile(dlg.selected_files,'zip',current_path,openmethod=dlg.openmethod)
                    dlg.Destroy()
                else:
                    dlg.Destroy()
            else:
                self.LoadFile([current_path,])



    def OnSplitterDClick(self,event):
        self.window_1.Unsplit(self.window_1_pane_1)


    def GetListCtrl(self):
        return self.list_ctrl_1

    def GetSortImages(self):
        return (self.dn,self.up)

    def OnItemSelected(self,event):
        global GlobalConfig
        if not GlobalConfig['EnableSidebarPreview']: return
        filename=unicode(self.list_ctrl_1.GetItemText(event.GetIndex()))
        current_path=GlobalConfig['LastDir']+u"/"+filename
        current_ext=os.path.splitext(current_path)[1].lower()
        if current_ext=='.txt'  or current_ext=='.htm' or current_ext=='.html':
            coding=DetectFileCoding(current_path)
            if coding=='error':return False
            try:
                file=open(current_path,'r')
            except:
                dlg = wx.MessageDialog(self, current_path+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            i=0
            istr=''
            while i<20:
                try:
                    istr+=file.readline(500)
                except:
                    dlg = wx.MessageDialog(self, current_path+u' 文件读取错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                i+=1
            preview_buff=AnyToUnicode(istr,coding)
            if current_ext=='.htm' or current_ext=='.html':
                preview_buff=htm2txt(preview_buff)
            #self.text_ctrl_3.SetValue(preview_buff)
            (x,y)=self.list_ctrl_1.GetItemPosition(event.GetIndex())
            #rect=self.list_ctrl_1.GetItemRect(event.GetIndex())
            #print str(x)+" "+str(self.GetPosition())
            self.PvFrame.SetPosition((self.GetPosition()[0]+self.window_1.GetSashPosition(),y))
            self.PvFrame.SetText(preview_buff)
            self.PvFrame.SetSize((400,200))
            self.PvFrame.Hide()
            self.PvFrame.Show()
            self.list_ctrl_1.SetFocus()
            file.close()
        else:
            self.PvFrame.Hide()



    def OnDirChar(self,event):
        global GlobalConfig, MYOS
        key=event.GetKeyCode()
        if key==wx.WXK_RIGHT:#Active Selected Item
            i=self.list_ctrl_1.GetFocusedItem()
            self.ActiveItem(self.list_ctrl_1.GetItemText(i))
            return
        if key==wx.WXK_LEFT:#Up dir
            if MYOS == 'Windows':
                current_path=GlobalConfig['LastDir']+u"\\.."
                if GlobalConfig['LastDir']==u'ROOT':
                    return
                if current_path.find(":\\\\..")<>-1:
                    GlobalConfig['LastDir']=u"ROOT"
                else:
                    GlobalConfig['LastDir']=os.path.normpath(current_path)
            else:
                if GlobalConfig['LastDir']==u'/':return
                current_path=GlobalConfig['LastDir']+u"/.."
                GlobalConfig['LastDir']=os.path.normpath(current_path)
            self.DirSideBarReload()
            return
        event.Skip()

    def DisplayVerCheck(self,event):
        dlg=VerCheckDialog(self,event.imsg)
        #event.imsg,event.iurl
        dlg.ShowModal()

    def UpdateLastFileMenu(self):
        global OpenedFileList
        i=1000
        total=2000
        while i<total:
            i+=1
            try:
                self.LastFileMenu.Remove(i) # the number of last opened files may less than maxopenedfiles, so need to try first
            except:
                pass
        i=1000
        for f in OpenedFileList:
            i+=1
            f['MenuID']=i
            if f['type']=='normal':self.LastFileMenu.Append(i,f['file'],f['file'],wx.ITEM_NORMAL)
            else:self.LastFileMenu.Append(i,f['zfile']+u'|'+f['file'],f['file'],wx.ITEM_NORMAL)
            self.Bind(wx.EVT_MENU, self.OpenLastFile, id=i)

    def DownloadFinished(self,event):
        global OnScreenFileList,GlobalConfig,OnDirectSeenPage,SqlCur,SqlCon
        if event.status=='nok':
            dlg = wx.MessageDialog(self, event.name+u'下载失败！',
                               u'出错了！',
                               wx.OK | wx.ICON_ERROR
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return None
        if GlobalConfig['DAUDF']==2:
            savefilename=GlobalConfig['defaultsavedir']+"/"+event.name.strip()+".txt"
            try:
                fp=codecs.open(savefilename,encoding='GBK',mode='w')
                ut=event.bk.encode('GBK', 'ignore')
                ut=unicode(ut, 'GBK', 'ignore')
                fp.write(ut)
                fp.close()
            except:
                err_dlg = wx.MessageDialog(None, u'写入文件：'+savefilename+u' 错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
                return False
            dlg = wx.MessageDialog(self, event.name+u'下载完毕，已保存在'+savefilename,
                               u'下载结束',
                               wx.OK | wx.ICON_INFORMATION
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = MyChoiceDialog(self, event.name+u'下载完毕。我想：',u'下载结束',
                              [u'直接观看',u'另存为...'],GlobalConfig['DAUDF']
                               )
        dlg.ShowModal()
        try:
            rr=dlg.chosen
            subscr=dlg.subscr
        except:
            rr=None
            subscr=False
        dlg.Destroy()
        if rr==u'直接观看':
            OnDirectSeenPage=True
            self.SaveBookDB()
            self.text_ctrl_1.SetValue(event.bk)
            OnScreenFileList=[]
            OnScreenFileList.append((event.name,'',event.bk.__len__()))
            #change the title
            self.SetTitle(self.title_str+' --- '+event.name)
            self.cur_catalog=None
        else:
            if rr==u'另存为...':
                wildcard = u"文本文件(UTF-8) (*.txt)|*.txt|"     \
                        u"文本文件(GBK) (*.txt)|*.txt"
                dlg = wx.FileDialog(
                    self, message=u"将当前文件另存为", defaultDir=GlobalConfig['LastDir'],
                    defaultFile=event.name+u".txt", wildcard=wildcard, style=wx.SAVE | wx.FD_OVERWRITE_PROMPT
                    )

                if dlg.ShowModal() == wx.ID_OK:
                    savefilename=dlg.GetPath()
                    if dlg.GetFilterIndex()==0:
                        try:
                            fp=codecs.open(savefilename,encoding='utf-8',mode='w')
                            fp.write(event.bk)
                            fp.close()
                        except:
                            err_dlg = wx.MessageDialog(None, u'写入文件：'+fname+u' 错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                            err_dlg.ShowModal()
                            err_dlg.Destroy()
                            return False
                    else:
                        try:
                            fp=codecs.open(savefilename,encoding='GBK',mode='w')
                            ut=event.bk.encode('GBK', 'ignore')
                            ut=unicode(ut, 'GBK', 'ignore')
                            fp.write(ut)
                            fp.close()
                        except:
                            err_dlg = wx.MessageDialog(None, u'写入文件：'+savefilename+u' 错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                            err_dlg.ShowModal()
                            err_dlg.Destroy()
                            return False
        dlg.Destroy()
        if subscr and event.bookstate != None:
            bkstate=event.bookstate
            sqlstr="insert into subscr values('%s','%s','%s','%s',%s,'%s','%s')" % (
                      bkstate['bookname'],bkstate['index_url'],
                      bkstate['last_chapter_name'],bkstate['last_update'],
                      bkstate['chapter_count'],
                      savefilename,
                      event.plugin_name
                      )
            SqlCur.execute(sqlstr)
            SqlCon.commit()
        self.text_ctrl_1.SetFocus()


    def SearchSidebar(self,evt):
        self.UpdateSearchSidebar(evt.GetString().strip())


    def UpdateSearchSidebar(self,key):

        py_key=key.strip()
        rlist=[]
        self.list_ctrl_1.DeleteAllItems()
        if py_key<>'':
            #print self.sideitemlist
            for m in self.sideitemlist:

                if m['py'].find(py_key)<>-1:
                    rlist.append(m['item'])
        else:
            for m in self.sideitemlist:
                rlist.append(m['item'])
        for m in rlist:
            self.list_ctrl_1.InsertItem(m)

    def ShowSlider(self,evt=None):
        (x,y)=self.GetClientSize()

        if self.slider==None:
            try:
                pos=int(self.text_ctrl_1.GetPosPercent())
            except:
                pos=0
            self.slider=SliderDialog(self,pos,(x/2,y/2))
            self.slider.Show()
        else:
            self.slider.Closeme()



class MyOpenFileDialog(wx.Dialog,wx.lib.mixins.listctrl.ColumnSorterMixin):
    global GlobalConfig
    select_files=[]
    zip_file=''
    file_icon_list={}
    open_method="load"
    def __init__(self, *args, **kwds):
        global GlobalConfig, MYOS
        self.select_files=[]
        # begin wxGlade: MyOpenFileDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.WANTS_CHARS
        wx.Dialog.__init__(self, *args, **kwds)
        self.bitmap_button_3 = wx.BitmapButton(self, -1, wx.Bitmap(GlobalConfig['IconDir']+u"/reload-16x16.png", wx.BITMAP_TYPE_ANY))
        self.text_ctrl_2 = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
        self.bitmap_button_1 = wx.BitmapButton(self, -1, wx.Bitmap(GlobalConfig['IconDir']+u"/folder-up-16x16.png", wx.BITMAP_TYPE_ANY))
        self.bitmap_button_2 = wx.BitmapButton(self, -1, wx.Bitmap(GlobalConfig['IconDir']+u"/dir-tree-16x16.png", wx.BITMAP_TYPE_ANY))
        self.list_ctrl_1 = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.choice_1 = wx.Choice(self, -1, choices=[u"所有支持的文件格式(*.txt,*.htm,*.html,*.zip,*.rar,*.umd,*.jar)", u"文本文件(*.txt,*.htm,*.html)", u"压缩文件(*.rar,*.zip,*.umd,*.jar,*.epub)", u"所有文件(*.*)"])
        self.button_4 = wx.Button(self, -1, u"添加")
        self.button_5 = wx.Button(self, -1, u" 打开")
        self.button_6 = wx.Button(self, -1, u"取消")
        self.text_ctrl_3 = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnReload, self.bitmap_button_3)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.text_ctrl_2)
        self.Bind(wx.EVT_BUTTON, self.OnUpDir, self.bitmap_button_1)
        self.Bind(wx.EVT_BUTTON, self.OnSelectDir, self.bitmap_button_2)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceSelected, self.choice_1)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_6)
        # end wxGlade
        self.Bind(wx.EVT_BUTTON, self.OnOpenFiles, self.button_5)
        self.Bind(wx.EVT_BUTTON, self.OnAppendFiles, self.button_4)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected,self.list_ctrl_1)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActive, self.list_ctrl_1)
        if MYOS == 'Windows':
            self.list_ctrl_1.Bind(wx.EVT_CHAR,self.OnKey_Win)
        else:
            self.list_ctrl_1.Bind(wx.EVT_CHAR,self.OnKey)
        self.Bind(wx.EVT_ACTIVATE,self.OnWinActive)
        if MYOS != 'Windows':
            self.list_ctrl_1.Bind(wx.EVT_CHAR,self.OnDirChar)
        self.image_list=wx.ImageList(16,16,mask=False,initialCount=5)
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/folder.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["folder"]=0
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/txtfile.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["txtfile"]=1
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/zipfile.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["zipfile"]=2
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/htmlfile.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["htmlfile"]=3
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/rarfile.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["rarfile"]=4
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/file.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["file"]=5
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/jar.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["jarfile"]=6
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/umd.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["umdfile"]=7
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/up.png",wx.BITMAP_TYPE_ANY)
        self.up=self.image_list.Add(bmp)
        self.file_icon_list["up"]=8
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/down.png",wx.BITMAP_TYPE_ANY)
        self.dn=self.image_list.Add(bmp)
        self.file_icon_list["down"]=9
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/epub.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["epub"]=10
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/Driver.png",wx.BITMAP_TYPE_ANY)
        self.image_list.Add(bmp)
        self.file_icon_list["driver"]=11

        self.list_ctrl_1.AssignImageList(self.image_list,wx.IMAGE_LIST_SMALL)
        self.list_ctrl_1.InsertColumn(0,u'文件名',width=220)
        self.list_ctrl_1.InsertColumn(1,u'长度')
        self.list_ctrl_1.InsertColumn(2,u'日期',width=120)
        self.text_ctrl_2.SetValue(GlobalConfig['LastDir'])
        self.itemDataMap={}
        wx.lib.mixins.listctrl.ColumnSorterMixin.__init__(self,3)
        self.LastDir=''
        self.Reload()



    def __set_properties(self):
        # begin wxGlade: MyOpenFileDialog.__set_properties
        self.SetTitle("Open File")
        self.SetSize((466, 491))
        self.bitmap_button_3.SetSize(self.bitmap_button_3.GetBestSize())
        self.text_ctrl_2.SetMinSize((350, -1))
        self.bitmap_button_1.SetSize(self.bitmap_button_1.GetBestSize())
        self.bitmap_button_2.SetSize(self.bitmap_button_2.GetBestSize())
        self.choice_1.SetMinSize((220, 21))
        self.choice_1.SetSelection(0)
        self.button_6.SetDefault()
        self.text_ctrl_3.SetMinSize((392, 120))
        # end wxGlade


    def __do_layout(self):
        # begin wxGlade: MyOpenFileDialog.__do_layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.bitmap_button_3, 0, 0, 0)
        sizer_3.Add(self.text_ctrl_2, 0, 0, 0)
        sizer_3.Add(self.bitmap_button_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.bitmap_button_2, 0, 0, 0)
        sizer_2.Add(sizer_3, 0, wx.EXPAND, 2)
        sizer_2.Add(self.list_ctrl_1, 1, wx.EXPAND, 0)
        sizer_4.Add(self.choice_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_4.Add(self.button_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_4.Add(self.button_5, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_4.Add(self.button_6, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_2.Add(sizer_4, 0, wx.EXPAND, 1)
        sizer_2.Add(self.text_ctrl_3, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_2)
        self.Layout()
        # end wxGlade

    def Reload(self):
        """"This function is to reload MyOpenFileDialog with GlobalConfig['LastDir']"""
        global GlobalConfig, MYOS
        if MYOS != 'Windows':
            if self.LastDir=='':
                RestorPos=False
            else:
                RestorPos=True
                if GlobalConfig['LastDir']==u'/':
                    RestorPosName=self.LastDir
                    RestorPosName=self.LastDir[1:]
                else:
                    RestorPosName=self.LastDir.rsplit(u'/',1)[1]
        else:
            if ((self.LastDir.__len__()>GlobalConfig['LastDir'].__len__() and not (self.LastDir=='ROOT' and GlobalConfig['LastDir'][1:]==u':\\')))or GlobalConfig['LastDir']==u'ROOT':
                RestorPos=True
                if GlobalConfig['LastDir']=='ROOT':
                    RestorPosName=self.LastDir
                else:
                    RestorPosName=self.LastDir.rsplit('\\',1)[1]
            else:
                RestorPos=False

        self.LastDir=GlobalConfig['LastDir']
        if MYOS != 'Windows':
            current_ext=os.path.splitext(GlobalConfig['LastDir'])[1].lower()
            self.list_ctrl_1.DeleteAllItems()
            if str(type(GlobalConfig['LastDir']))=='<type \'str\'>':
                GlobalConfig['LastDir']=unicode(GlobalConfig['LastDir'],'GBK','ignore')
            try:
                file_list=os.listdir(GlobalConfig['LastDir'])
            except:
                dlg = wx.MessageDialog(None, GlobalConfig['LastDir']+u' 目录打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,"..",self.file_icon_list['folder'])
                Date_str=u""
                self.list_ctrl_1.SetStringItem(index,2,Date_str)
                self.list_ctrl_1.SetItemData(index,index)
                self.itemDataMap[index]=('\x01'+u"..",0,Date_str)
                return False
        else:
            if GlobalConfig['LastDir']<>u'ROOT':
                current_ext=os.path.splitext(GlobalConfig['LastDir'])[1].lower()
                self.list_ctrl_1.DeleteAllItems()
                try:
                    tlist=os.listdir(GlobalConfig['LastDir'])
                except:
                    dlg = wx.MessageDialog(None, GlobalConfig['LastDir']+u' 目录打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,"..",self.file_icon_list['folder'])
                    Date_str=u""
                    self.list_ctrl_1.SetStringItem(index,2,Date_str)
                    self.list_ctrl_1.SetItemData(index,index)
                    self.itemDataMap[index]=('\x01'+u"..",0,Date_str)
                    #self.window_1_pane_1.SetFocus()
                    self.list_ctrl_1.SetFocus()
                    self.list_ctrl_1.Focus(0)
                    return
                file_list=[]
                for m in tlist:
                    m=AnyToUnicode(m,None)
                    file_list.append(m)
            else:
                #List all windows drives
                i=0
                RPos=0
                self.list_ctrl_1.DeleteAllItems()
                drive_list=[]
                drive_str = win32api.GetLogicalDriveStrings()
                drive_list=drive_str.split('\x00')
                drive_list.pop()
                for drive in drive_list:
                    index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,drive,self.file_icon_list['driver'])
                    if drive==RestorPosName:RPos=i
                    Date_str=''
                    self.list_ctrl_1.SetStringItem(index,2,Date_str)
                    self.list_ctrl_1.SetItemData(index,index)
                    self.itemDataMap[index]=('\x01'+drive,0,Date_str)
                    i+=1
                self.text_ctrl_2.SetValue(GlobalConfig['LastDir'])
                self.list_ctrl_1.Focus(RPos)
                self.list_ctrl_1.Select(RPos)
                self.list_ctrl_1.Refresh()
                return

                file_list=[]
                for m in tlist:
                    m=AnyToUnicode(m,None)
                    file_list.append(m)
        file_list.sort(key=unicode.lower)
        index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,"..",self.file_icon_list['folder'])
        Date_str=u""
        self.list_ctrl_1.SetStringItem(index,2,Date_str)
        self.list_ctrl_1.SetItemData(index,index)
        self.itemDataMap[index]=('\x01'+u"..",0,Date_str)
        i=0
        RPos=0
        bflist=[]
        for n in file_list:
            bflist.append(n)
        for filename in file_list:
#            if str(type(filename))=='<type \'str\'>':
#                filename=unicode(filename,'GBK','ignore')
            current_path=GlobalConfig['LastDir']+u"/"+filename+u"/"
            current_path=os.path.normpath(current_path)
            if os.path.isdir(current_path)== True:
                if RestorPos:
                    if filename==RestorPosName:
                        RPos=i
                index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['folder'])
                Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                self.list_ctrl_1.SetStringItem(index,2,Date_str)
                self.list_ctrl_1.SetItemData(index,index)
                self.itemDataMap[index]=('\x01'+filename,0,Date_str)
                bflist.remove(filename)
                i+=1
        RPos+=1
        for filename in bflist:
            current_path=GlobalConfig['LastDir']+u"/"+filename
            #if os.path.isdir(current_path)== False:
            if os.path.splitext(current_path)[1].lower()=='.txt' and self.choice_1.GetSelection()<>2:
                index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['txtfile'])
                Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                file_size=HumanSize(os.path.getsize(current_path))
                self.list_ctrl_1.SetStringItem(index,1,file_size)
                self.list_ctrl_1.SetStringItem(index,2,Date_str)
                self.list_ctrl_1.SetItemData(index,index)
                self.itemDataMap[index]=(filename,os.path.getsize(current_path),Date_str)
                i+=1
            else:
                if (os.path.splitext(current_path)[1].lower()=='.htm' or os.path.splitext(current_path)[1].lower()=='.html') and self.choice_1.GetSelection()<>2:
                    index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['htmlfile'])
                    Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                    file_size=HumanSize(os.path.getsize(current_path))
                    self.list_ctrl_1.SetStringItem(index,1,file_size)
                    self.list_ctrl_1.SetStringItem(index,2,Date_str)
                    self.list_ctrl_1.SetItemData(index,index)
                    self.itemDataMap[index]=(filename,os.path.getsize(current_path),Date_str)
                else:
                    if os.path.splitext(current_path)[1].lower()=='.zip' and self.choice_1.GetSelection()<>1:
                        index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['zipfile'])
                        Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                        #file_size=str(os.path.getsize(current_path))
                        file_size=HumanSize(os.path.getsize(current_path))
                        self.list_ctrl_1.SetStringItem(index,1,file_size)
                        self.list_ctrl_1.SetStringItem(index,2,Date_str)
                        self.list_ctrl_1.SetItemData(index,index)
                        self.itemDataMap[index]=(filename,os.path.getsize(current_path),Date_str)
                    else:
                        if os.path.splitext(current_path)[1].lower()=='.rar' and self.choice_1.GetSelection()<>1:
                            index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['rarfile'])
                            Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                            file_size=HumanSize(os.path.getsize(current_path))
                            self.list_ctrl_1.SetStringItem(index,1,file_size)
                            self.list_ctrl_1.SetStringItem(index,2,Date_str)
                            self.list_ctrl_1.SetItemData(index,index)
                            self.itemDataMap[index]=(filename,os.path.getsize(current_path),Date_str)
                        else:
                             if os.path.splitext(current_path)[1].lower()=='.jar' and self.choice_1.GetSelection()<>1:
                                 index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['jarfile'])
                                 Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                                 file_size=HumanSize(os.path.getsize(current_path))
                                 self.list_ctrl_1.SetStringItem(index,1,file_size)
                                 self.list_ctrl_1.SetStringItem(index,2,Date_str)
                                 self.list_ctrl_1.SetItemData(index,index)
                                 self.itemDataMap[index]=(filename,os.path.getsize(current_path),Date_str)
                             else:
                                 if os.path.splitext(current_path)[1].lower()=='.umd' and self.choice_1.GetSelection()<>1:
                                     index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['umdfile'])
                                     Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                                     file_size=HumanSize(os.path.getsize(current_path))
                                     self.list_ctrl_1.SetStringItem(index,1,file_size)
                                     self.list_ctrl_1.SetStringItem(index,2,Date_str)
                                     self.list_ctrl_1.SetItemData(index,index)
                                     self.itemDataMap[index]=(filename,os.path.getsize(current_path),Date_str)
                                 else:
                                     if os.path.splitext(current_path)[1].lower()=='.epub' and self.choice_1.GetSelection()<>1:
                                         index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['epub'])
                                         Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                                         file_size=HumanSize(os.path.getsize(current_path))
                                         self.list_ctrl_1.SetStringItem(index,1,file_size)
                                         self.list_ctrl_1.SetStringItem(index,2,Date_str)
                                         self.list_ctrl_1.SetItemData(index,index)
                                         self.itemDataMap[index]=(filename,os.path.getsize(current_path),Date_str)

                                     else:
                                         if self.choice_1.GetSelection()==3:
                                            index=self.list_ctrl_1.InsertImageStringItem(sys.maxint,filename,self.file_icon_list['file'])
                                            Date_str=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getctime(current_path)))
                                            file_size=HumanSize(os.path.getsize(current_path))
                                            self.list_ctrl_1.SetStringItem(index,1,file_size)
                                            self.list_ctrl_1.SetStringItem(index,2,Date_str)
                                            self.list_ctrl_1.SetItemData(index,index)
                                            self.itemDataMap[index]=(filename,os.path.getsize(current_path),Date_str)
        self.text_ctrl_2.SetValue(GlobalConfig['LastDir'])
        self.list_ctrl_1.Focus(RPos)
        self.list_ctrl_1.Select(RPos)
        self.list_ctrl_1.Refresh()







    def OnDirChar(self,event):
        global GlobalConfig
        key=event.GetKeyCode()
        if key==wx.WXK_RIGHT:#Active Selected Item
            i=self.list_ctrl_1.GetFocusedItem()
            self.ActiveItem(self.list_ctrl_1.GetItemText(i))
            return
        if key==wx.WXK_LEFT:#Up dir
            if GlobalConfig['LastDir']==u'/':return
            current_path=GlobalConfig['LastDir']+u"/.."
            GlobalConfig['LastDir']=os.path.normpath(current_path)
            self.Reload()
            return
        event.Skip()






    def OnReload(self, event): # wxGlade: MyOpenFileDialog.<event_handler>
        global GlobalConfig
        if os.path.isdir(self.text_ctrl_2.GetValue())== True:
            GlobalConfig['LastDir']=self.text_ctrl_2.GetValue()
            self.Reload()
        else:
             dlg = wx.MessageDialog(self, u'目录输入有误！',u"错误！",wx.OK|wx.ICON_ERROR)
             dlg.ShowModal()
             dlg.Destroy()

    def OnEnter(self, event): # wxGlade: MyOpenFileDialog.<event_handler>
         global GlobalConfig
         if os.path.isdir(self.text_ctrl_2.GetValue())== True:
            GlobalConfig['LastDir']=self.text_ctrl_2.GetValue()
            self.Reload()
         else:
            dlg = wx.MessageDialog(self, u'目录输入有误！',u"错误！",wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def OnUpDir(self, event): # wxGlade: MyOpenFileDialog.<event_handler>
        global GlobalConfig
        GlobalConfig['LastDir']=GlobalConfig['LastDir'].rpartition(u'/')[0]
        if GlobalConfig['LastDir'].find('/')==-1:
            GlobalConfig['LastDir']+=u'/'
        self.text_ctrl_2.SetValue(GlobalConfig['LastDir'])
        self.Reload()


    def OnSelectDir(self, event): # wxGlade: MyOpenFileDialog.<event_handler>
        global GlobalConfig
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            GlobalConfig['LastDir']=dlg.GetPath()
            self.text_ctrl_2.SetValue(dlg.GetPath())
            self.Reload()
        dlg.Destroy()

    def OnItemSelected(self,event):
        global GlobalConfig
        self.text_ctrl_3.SetValue('')
        item=event.GetItem()
        preview_buff=u''
        filename=item.GetText()
        current_path=GlobalConfig['LastDir']+u"/"+filename
        current_ext=os.path.splitext(current_path)[1].lower()
        if current_ext=='.txt'  or current_ext=='.htm' or current_ext=='.html':
            coding=DetectFileCoding(current_path)
            if coding=='error':return False
            try:
                file=open(current_path,'r')
            except:
                dlg = wx.MessageDialog(self, current_path+u' 文件打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            i=0
            istr=''
            while i<20:
                try:
                    istr+=file.readline(500)
                except:
                    dlg = wx.MessageDialog(self, current_path+u' 文件读取错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                i+=1
            preview_buff=AnyToUnicode(istr,coding)
            if current_ext=='.htm' or current_ext=='.html':
                preview_buff=htm2txt(preview_buff)
            self.text_ctrl_3.SetValue(preview_buff)
            file.close()

    def OnItemActive(self,event):
        global GlobalConfig, MYOS
        item=event.GetItem()
        filename=item.GetText()
        if MYOS != 'Windows':
            if GlobalConfig['LastDir']<>'/':
                current_path=GlobalConfig['LastDir']+u"/"+filename
            else:
                current_path=GlobalConfig['LastDir']+filename
            current_path=os.path.normpath(current_path)
        else:
            if filename[1:]==":\\" and not os.path.isdir(filename):
                return False #means this driver is not ready
            if GlobalConfig['LastDir']<>"ROOT":
                current_path=GlobalConfig['LastDir']+u"\\"+filename
            else:
                current_path=filename
        current_ext=os.path.splitext(current_path)[1].lower()
        if os.path.isdir(current_path)== True:
            if MYOS != 'Windows':
                GlobalConfig['LastDir']=os.path.normpath(current_path)
                self.text_ctrl_2.SetValue(GlobalConfig['LastDir'])
            else:
                if current_path.find(":\\\\..")<>-1:
                    GlobalConfig['LastDir']=u"ROOT"
                else:
                    GlobalConfig['LastDir']=os.path.normpath(current_path)
            self.Reload()
        else:
            if current_ext==".zip" or current_ext==".rar":
                dlg=ZipFileDialog(self,current_path)
                dlg.ShowModal()
                if dlg.selected_files<>[]:
                    self.zip_file=current_path
                    self.select_files=dlg.selected_files
                    self.open_method=dlg.openmethod
                    dlg.Destroy()
                    #self.Destroy()
                    self.Close()
                else:
                    dlg.Destroy()
            else:
                self.select_files.append(current_path)
                #self.Destroy()
                self.Close()



    def ActiveItem(self,filename):
        global GlobalConfig, MYOS
        if MYOS != 'Windows':
            if GlobalConfig['LastDir']<>'/':
                current_path=GlobalConfig['LastDir']+u"/"+filename
            else:
                current_path=GlobalConfig['LastDir']+filename
            current_path=os.path.normpath(current_path)
        else:
            if filename[1:]==":\\" and not os.path.isdir(filename):
                return False #means this driver is not ready
            if GlobalConfig['LastDir']<>"ROOT":
                current_path=GlobalConfig['LastDir']+u"\\"+filename
            else:
                current_path=filename

        current_ext=os.path.splitext(current_path)[1].lower()
        if os.path.isdir(current_path)== True:
            if MYOS != 'Windows':
                GlobalConfig['LastDir']=os.path.normpath(current_path)
                self.text_ctrl_2.SetValue(GlobalConfig['LastDir'])
            else:
                if current_path.find(":\\\\..")<>-1:
                    GlobalConfig['LastDir']=u"ROOT"
                else:
                    GlobalConfig['LastDir']=os.path.normpath(current_path)
            self.Reload()
        else:
            if current_ext==".zip" or current_ext==".rar":
                dlg=ZipFileDialog(self,current_path)
                dlg.ShowModal()
                if dlg.selected_files<>[]:
                    self.zip_file=current_path
                    self.select_files=dlg.selected_files
                    self.open_method=dlg.openmethod
                    dlg.Destroy()
                    #self.Destroy()
                    self.Close()
                else:
                    dlg.Destroy()
            else:
                self.select_files.append(current_path)
                #self.Destroy()
                self.Close()




    def OnCancell(self, event): # wxGlade: MyOpenFileDialog.<event_handler>
        self.Destroy()

    def OnChoiceSelected(self, event): # wxGlade: MyOpenFileDialog.<event_handler>
        self.Reload()

    def OnKey(self,event):
        key=event.GetKeyCode()
        if key==wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()

    def OnKey_Win(self,event): #windows version
        key=event.GetKeyCode()
        if key==wx.WXK_RIGHT:#Active Selected Item
            i=self.list_ctrl_1.GetFocusedItem()
            self.ActiveItem(self.list_ctrl_1.GetItemText(i))
            return
        if key==wx.WXK_LEFT:#Up dir
            current_path=GlobalConfig['LastDir']+u"\\.."
            if GlobalConfig['LastDir']==u'ROOT':
                return
            if current_path.find(":\\\\..")<>-1:
                GlobalConfig['LastDir']=u"ROOT"
            else:
                GlobalConfig['LastDir']=os.path.normpath(current_path)
            self.Reload()
            return
        if key==wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()


    def OnOpenFiles(self,event):
        global GlobalConfig
        item=self.list_ctrl_1.GetNextSelected(-1)
        while item<>-1:
            filename=self.list_ctrl_1.GetItemText(item)
            current_path=GlobalConfig['LastDir']+u"/"+filename
            self.select_files.append(current_path)
            item=self.list_ctrl_1.GetNextSelected(item)
        self.open_method="load"
        self.Close()


    def OnAppendFiles(self,event):
        global GlobalConfig
        item=self.list_ctrl_1.GetNextSelected(-1)
        while item<>-1:
            filename=self.list_ctrl_1.GetItemText(item)
            current_path=GlobalConfig['LastDir']+u"/"+filename
            self.select_files.append(current_path)
            item=self.list_ctrl_1.GetNextSelected(item)
        self.open_method="append"
        self.Close()

    def OnWinActive(self,event):
        if event.GetActive():self.list_ctrl_1.SetFocus()


    def GetListCtrl(self):
        return self.list_ctrl_1

    def GetSortImages(self):
        return (self.dn,self.up)

# end of class MyOpenFileDialog


class BookMarkDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        self.filename=''
        self.pos=0
        # begin wxGlade: BookMarkDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_3 = wx.StaticText(self, -1, u"文件名：", style=wx.ALIGN_CENTRE)
        self.text_ctrl_3 = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        self.button_3 = wx.Button(self, -1, u"打开")
        self.label_4 = wx.StaticText(self, -1, u"预览：    ")
        self.text_ctrl_4 = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        self.button_4 = wx.Button(self, -1, u"删除")
        self.list_box_1 = wx.ListBox(self, -1, choices=[], style=wx.LB_SINGLE)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.Bind(wx.EVT_LISTBOX,self.OnSelected,self.list_box_1)
        self.Bind(wx.EVT_LISTBOX_DCLICK,self.OnActive,self.list_box_1)
        self.Bind(wx.EVT_BUTTON,self.OnActive,self.button_3)
        self.Bind(wx.EVT_BUTTON,self.OnDel,self.button_4)
        self.list_box_1.Bind(wx.EVT_CHAR,self.OnKey)
        self.Bind(wx.EVT_ACTIVATE,self.OnWinActive)

        self.ReDo()


    def __set_properties(self):
        # begin wxGlade: BookMarkDialog.__set_properties
        self.SetTitle(u"收藏夹")
        self.SetSize((500, 500))
        self.text_ctrl_3.SetMinSize((350, -1))
        self.text_ctrl_4.SetMinSize((350, -1))
        self.list_box_1.SetMinSize((500,500))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: BookMarkDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add((10, 20), 0, 0, 0)
        sizer_3.Add(self.label_3, 0, 0, 0)
        sizer_3.Add(self.text_ctrl_3, 0, 0, 0)
        sizer_3.Add((10, 20), 0, 0, 0)
        sizer_3.Add(self.button_3, 0, 0, 0)
        sizer_3.Add((10, 20), 0, 0, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_4.Add((10, 20), 0, 0, 0)
        sizer_4.Add(self.label_4, 0, wx.ALIGN_RIGHT, 0)
        sizer_4.Add(self.text_ctrl_4, 0, 0, 0)
        sizer_4.Add((10, 20), 0, 0, 0)
        sizer_4.Add(self.button_4, 0, 0, 0)
        sizer_4.Add((10, 20), 0, 0, 0)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_1.Add(self.list_box_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def ReDo(self):
        global BookMarkList
        bk_name_list=[]
        self.list_box_1.Clear()
        if BookMarkList.__len__()==0:return
        for bk in BookMarkList:
            bk_name_list.append(bk['filename'])
        self.list_box_1.InsertItems(bk_name_list,0)
        self.list_box_1.SetSelection(0)
        self.text_ctrl_3.SetValue(BookMarkList[0]['filename'])
        self.text_ctrl_4.SetValue(BookMarkList[0]['line'])


    def OnSelected(self,event):
        global BookMarkList
        i=0
        while not self.list_box_1.IsSelected(i):
            i+=1
            if i>=self.list_box_1.GetCount(): return
        self.text_ctrl_3.SetValue(BookMarkList[i]['filename'])
        self.text_ctrl_4.SetValue(BookMarkList[i]['line'])

    def OnActive(self,event):
        global BookMarkList
        if BookMarkList.__len__()==0:return
        i=0
        while not self.list_box_1.IsSelected(i):
            i+=1
            if i>=self.list_box_1.GetCount(): return
        self.filename=BookMarkList[i]['filename']
        self.pos=BookMarkList[i]['pos']
        self.Close()

    def OnDel(self,event):
        global BookMarkList
        if BookMarkList.__len__()==0:return
        i=0
        while not self.list_box_1.IsSelected(i):
            i+=1
            if i>=self.list_box_1.GetCount(): return
        BookMarkList.__delitem__(i)
        self.ReDo()
        if i>0:
            i-=1
            self.list_box_1.SetSelection(i)
            self.text_ctrl_3.SetValue(BookMarkList[i]['filename'])
            self.text_ctrl_4.SetValue(BookMarkList[i]['line'])
        else:
            self.text_ctrl_3.SetValue('')
            self.text_ctrl_4.SetValue('')

# end of class BookMarkDialog

    def OnKey(self,event):
        key=event.GetKeyCode()
        if key==wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()


    def OnWinActive(self,event):
        if event.GetActive():self.list_box_1.SetFocus()

##class OptionDialog(wx.Dialog):
##    def __init__(self, *args, **kwds):
##        # begin wxGlade: OptionDialog.__init__
##        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
##        wx.Dialog.__init__(self, *args, **kwds)
##        self.notebook_1 = wx.Notebook(self, -1, style=0)
##        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, -1)
##        self.notebook_1_pane_1 = wx.Panel(self.notebook_1, -1)
##        self.notebook_1_pane_3 = wx.Panel(self.notebook_1, -1)
##        self.sizer_3_staticbox = wx.StaticBox(self.notebook_1_pane_3, -1, u"下载")
##        self.sizer_4_staticbox = wx.StaticBox(self.notebook_1_pane_3, -1, u"代理服务器")
##
##        self.text_ctrl_4 = wx.TextCtrl(self.notebook_1_pane_1, -1, u"《老子》八十一章\n\n　1.道可道，非常道。名可名，非常名。无名天地之始。有名万物之母。故常无欲以观其妙。常有欲以观其徼。此两者同出而异名，同谓之玄。玄之又玄，众妙之门。\n\n　2.天下皆知美之为美，斯恶矣；皆知善之为善，斯不善已。故有无相生，难易相成，长短相形，高下相倾，音声相和，前後相随。是以圣人处无为之事，行不言之教。万物作焉而不辞。生而不有，为而不恃，功成而弗居。夫唯弗居，是以不去。\n\n　3.不尚贤， 使民不争。不贵难得之货，使民不为盗。不见可欲，使民心不乱。是以圣人之治，虚其心，实其腹，弱其志，强其骨；常使民无知、无欲，使夫智者不敢为也。为无为，则无不治。\n\n　4.道冲而用之，或不盈。渊兮似万物之宗。解其纷，和其光，同其尘，湛兮似或存。吾不知谁之子，象帝之先。\n\n　5.天地不仁，以万物为刍狗。圣人不仁，以百姓为刍狗。天地之间，其犹橐迭乎？虚而不屈，动而愈出。多言数穷，不如守中。", style=wx.TE_MULTILINE|wx.TE_READONLY)
##        self.label_4 = wx.StaticText(self.notebook_1_pane_1, -1, u"显示方案：")
##        self.combo_box_1 = wx.ComboBox(self.notebook_1_pane_1, -1, choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
##        self.button_6 = wx.Button(self.notebook_1_pane_1, -1, u"另存为")
##        self.button_7 = wx.Button(self.notebook_1_pane_1, -1, u"删除")
##        self.static_line_1 = wx.StaticLine(self.notebook_1_pane_1, -1)
##        self.button_9 = wx.Button(self.notebook_1_pane_1, -1, u"字体")
##        self.button_10 = wx.Button(self.notebook_1_pane_1, -1, u"字体颜色")
##        self.button_11 = wx.Button(self.notebook_1_pane_1, -1, u"背景颜色")
##        self.label_5 = wx.StaticText(self.notebook_1_pane_2, -1, u"启动：")
##        self.checkbox_1 = wx.CheckBox(self.notebook_1_pane_2, -1, u"自动载入上次阅读的文件")
##        self.label_5_copy = wx.StaticText(self.notebook_1_pane_2, -1, u"启动：")
##        self.checkbox_VerCheck = wx.CheckBox(self.notebook_1_pane_2, -1, u"检查更新")
##        self.label_1 = wx.StaticText(self.notebook_1_pane_2, -1, u"自动翻页间隔（秒）：")
##        self.text_ctrl_1 = wx.TextCtrl(self.notebook_1_pane_2, -1, "")
##        self.label_mof = wx.StaticText(self.notebook_1_pane_2, -1, u"最大曾经打开文件菜单数：")
##        self.text_ctrl_mof = wx.TextCtrl(self.notebook_1_pane_2, -1, "")
##
##        self.label_1_copy = wx.StaticText(self.notebook_1_pane_2, -1, u"连续阅读提醒时间（分钟）：")
##        self.text_ctrl_1_copy = wx.TextCtrl(self.notebook_1_pane_2, -1, "")
##        self.label_1_copy_copy_copy = wx.StaticText(self.notebook_1_pane_2, -1, u"文件选择栏预览：")
##        self.checkbox_Preview = wx.CheckBox(self.notebook_1_pane_2, -1, u"是否在文件选择侧边栏中预览文件内容")
##        self.label_7 = wx.StaticText(self.notebook_1_pane_2, -1, u"文件选择栏显示")
##        self.checkbox_5 = wx.CheckBox(self.notebook_1_pane_2, -1, u"是否在文件选择侧边栏中只显示支持的文件格式")
##
##        self.label_2 = wx.StaticText(self.notebook_1_pane_3, -1, u"下载完毕后的缺省动作：")
##        self.choice_1 = wx.Choice(self.notebook_1_pane_3, -1, choices=[u"直接阅读", u"另存为文件",u'直接保存在缺省目录'])
##        self.label_12 = wx.StaticText(self.notebook_1_pane_3, -1, u"另存为的缺省目录：")
##        self.text_ctrl_8 = wx.TextCtrl(self.notebook_1_pane_3, -1, "")
##        self.button_1 = wx.Button(self.notebook_1_pane_3, -1, u"选择")
##        self.label_11 = wx.StaticText(self.notebook_1_pane_3, -1, u"同时下载的线程个数（需插件支持；不能超过50）：")
##        self.text_ctrl_7 = wx.TextCtrl(self.notebook_1_pane_3, -1, "10")
##        self.label_3 = wx.StaticText(self.notebook_1_pane_3, -1, u"启用代理服务器：")
##        self.checkbox_2 = wx.CheckBox(self.notebook_1_pane_3, -1, "")
##        self.label_6 = wx.StaticText(self.notebook_1_pane_3, -1, u"代理服务器地址：")
##        self.text_ctrl_2 = wx.TextCtrl(self.notebook_1_pane_3, -1, "")
##        self.label_8 = wx.StaticText(self.notebook_1_pane_3, -1, u"代理服务器端口：")
##        self.text_ctrl_3 = wx.TextCtrl(self.notebook_1_pane_3, -1, "")
##        self.label_9 = wx.StaticText(self.notebook_1_pane_3, -1, u"用户名：")
##        self.text_ctrl_5 = wx.TextCtrl(self.notebook_1_pane_3, -1, "")
##        self.label_10 = wx.StaticText(self.notebook_1_pane_3, -1, u"密码：")
##        self.text_ctrl_6 = wx.TextCtrl(self.notebook_1_pane_3, -1, "")
##
##
##        self.button_4 = wx.Button(self, -1, u"确定")
##        self.button_5 = wx.Button(self, -1, u"取消")
##
##        self.__set_properties()
##        self.__do_layout()
##        # end wxGlade
##
##
##        #self.Bind(wx.EVT_BUTTON,self.OnOK,self.button_4)
##        self.Bind(wx.EVT_BUTTON,self.OnSelFont,self.button_9)
##        self.Bind(wx.EVT_BUTTON,self.OnSelFColor,self.button_10)
##        self.Bind(wx.EVT_BUTTON,self.OnSelBColor,self.button_11)
##        self.Bind(wx.EVT_BUTTON,self.OnSaveTheme,self.button_6)
##        self.Bind(wx.EVT_BUTTON,self.OnDelTheme,self.button_7)
##        self.Bind(wx.EVT_BUTTON,self.SelectDir,self.button_1)
##        self.Bind(wx.EVT_COMBOBOX,self.OnSel,self.combo_box_1)
##        self.Bind(wx.EVT_BUTTON,self.OnOk,self.button_4)
##        self.Bind(wx.EVT_BUTTON,self.OnCancell,self.button_5)
##        self.text_ctrl_4.Bind(wx.EVT_CHAR,self.OnKey)
##        self.Bind(wx.EVT_ACTIVATE,self.OnWinActive)
##
##    def __set_properties(self):
##        global GlobalConfig,ThemeList
##        # begin wxGlade: OptionDialog.__set_properties
##        self.SetTitle(u"选项设置")
##        self.combo_box_1.SetMinSize((150,-1))
##        self.text_ctrl_4.SetMinSize((384, 189))
##        self.text_ctrl_1.SetMinSize((30,-1))
##        self.text_ctrl_8.SetMinSize((180, -1))
##        self.text_ctrl_7.SetMinSize((40, -1))
##        self.label_1_copy.SetToolTipString(u"0代表不提醒")
##        self.text_ctrl_1_copy.SetMinSize((40, -1))
##        self.text_ctrl_1_copy.SetToolTipString(u"0代表不提醒")
##        self.text_ctrl_4.SetFont(GlobalConfig['CurFont'])
##        self.text_ctrl_4.SetForegroundColour(GlobalConfig['CurFColor'])
##        self.text_ctrl_4.SetBackgroundColour(GlobalConfig['CurBColor'])
##        self.text_ctrl_4.Refresh()
##        txt=self.text_ctrl_4.GetValue()
##        self.text_ctrl_4.SetValue(txt)
##        self.checkbox_VerCheck.SetValue(GlobalConfig['VerCheckOnStartup'])
##        #append drop down list
##        for t in ThemeList:
##            self.combo_box_1.Append(t['name'])
##        #seting load last file check box
##        self.checkbox_1.SetValue(GlobalConfig['LoadLastFile'])
##        self.checkbox_Preview.SetValue(GlobalConfig['EnableSidebarPreview'])
##        self.text_ctrl_1.SetValue(unicode(GlobalConfig['AutoScrollInterval']/1000))
##        self.text_ctrl_1_copy.SetValue(unicode(GlobalConfig['RemindInterval']))
##        self.checkbox_5.SetValue(not GlobalConfig['ShowAllFileInSidebar'])
##        self.text_ctrl_mof.SetMinSize((30, -1))
##        self.text_ctrl_mof.SetValue(unicode(GlobalConfig['MaxOpenedFiles']))
##
##        self.text_ctrl_2.SetMinSize((200, -1))
##        self.text_ctrl_3.SetMinSize((50, -1))
##        self.choice_1.Select(GlobalConfig['DAUDF'])
##        self.checkbox_2.SetValue(GlobalConfig['useproxy'])
##        self.text_ctrl_2.SetValue(unicode(GlobalConfig['proxyserver']))
##        self.text_ctrl_3.SetValue(unicode(GlobalConfig['proxyport']))
##        self.text_ctrl_5.SetValue(unicode(GlobalConfig['proxyuser']))
##        self.text_ctrl_6.SetValue(unicode(GlobalConfig['proxypass']))
##        self.text_ctrl_7.SetValue(unicode(GlobalConfig['numberofthreads']))
##        self.text_ctrl_8.SetValue(unicode(GlobalConfig['defaultsavedir']))
##
##        # end wxGlade
##
##    def __do_layout(self):
##        # begin wxGlade: OptionDialog.__do_layout
##        sizer_5 = wx.BoxSizer(wx.VERTICAL)
##        grid_sizer_1 = wx.GridSizer(1, 5, 0, 0)
##
##        sizer_2 = wx.BoxSizer(wx.VERTICAL)
##        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
##        sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox,  wx.VERTICAL)
##
##        sizer_17 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
##
##
##        sizer_9 = wx.BoxSizer(wx.VERTICAL)
##        sizer_20 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_1_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_1_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_1_copy = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_mof = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_10_copy = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_10_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_6 = wx.BoxSizer(wx.VERTICAL)
##        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_6.Add(self.text_ctrl_4, 1, wx.EXPAND, 0)
##        sizer_7.Add(self.label_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        sizer_7.Add((10, 20), 0, 0, 0)
##        sizer_7.Add(self.combo_box_1, 0, 0, 0)
##        sizer_7.Add((10, 20), 0, 0, 0)
##        sizer_7.Add(self.button_6, 0, 0, 0)
##        sizer_7.Add((10, 20), 0, 0, 0)
##        sizer_7.Add(self.button_7, 0, 0, 0)
##        sizer_6.Add(sizer_7, 0, wx.EXPAND, 0)
##        sizer_6.Add(self.static_line_1, 0, wx.EXPAND, 0)
##        sizer_11.Add((20, 20), 0, 0, 0)
##        sizer_11.Add(self.button_9, 0, 0, 0)
##        sizer_11.Add((60, 20), 0, 0, 0)
##        sizer_11.Add(self.button_10, 0, 0, 0)
##        sizer_11.Add((60, 20), 0, 0, 0)
##        sizer_11.Add(self.button_11, 0, 0, 0)
##        sizer_11.Add((20, 20), 0, 0, 0)
##        sizer_6.Add(sizer_11, 0, wx.EXPAND, 0)
##        self.notebook_1_pane_1.SetSizer(sizer_6)
##        sizer_10.Add(self.label_5, 0, 0, 0)
##        sizer_10.Add(self.checkbox_1, 0, 0, 0)
##        sizer_9.Add(sizer_10, 0, wx.EXPAND, 0)
##        sizer_9.Add((20, 20), 0, 0, 0)
##        sizer_10_copy_1.Add(self.label_5_copy, 0, 0, 0)
##        sizer_10_copy_1.Add(self.checkbox_VerCheck, 0, 0, 0)
##        sizer_10_copy.Add(sizer_10_copy_1, 0, wx.EXPAND, 0)
##        sizer_9.Add(sizer_10_copy, 0, wx.EXPAND, 0)
##        sizer_9.Add((20, 20), 0, 0, 0)
##        sizer_1.Add(self.label_1, 0, wx.ALIGN_BOTTOM, 0)
##        sizer_1.Add(self.text_ctrl_1, 0, 0, 0)
##        sizer_9.Add(sizer_1, 0, wx.EXPAND, 0)
##        sizer_9.Add((20, 20), 0, 0, 0)
##        sizer_1_copy.Add(self.label_1_copy, 0, wx.ALIGN_BOTTOM, 0)
##        sizer_1_copy.Add(self.text_ctrl_1_copy, 0, 0, 0)
##        sizer_9.Add(sizer_1_copy, 0, wx.EXPAND, 0)
##        sizer_9.Add((20, 20), 0, 0, 0)
##        sizer_1_copy_copy_copy.Add(self.label_1_copy_copy_copy, 0, wx.ALIGN_BOTTOM, 0)
##        sizer_1_copy_copy_copy.Add(self.checkbox_Preview, 0, 0, 0)
##        sizer_9.Add(sizer_1_copy_copy_copy, 0, wx.EXPAND, 0)
##        sizer_9.Add((20, 20), 0, 0, 0)
##        sizer_20.Add(self.label_7, 0, wx.ALIGN_BOTTOM, 0)
##        sizer_20.Add(self.checkbox_5, 0, 0, 0)
##        sizer_9.Add(sizer_20, 0, wx.EXPAND, 0)
##        sizer_9.Add((20, 20), 0, 0, 0)
##        sizer_mof.Add(self.label_mof, 0, wx.ALIGN_BOTTOM, 0)
##        sizer_mof.Add(self.text_ctrl_mof, 0, 0, 0)
##        sizer_9.Add(sizer_mof, 0, wx.EXPAND, 0)
##        self.notebook_1_pane_2.SetSizer(sizer_9)
##
##        sizer_16.Add(self.label_2, 0, wx.ALL, 5)
##        sizer_16.Add(self.choice_1, 0, 0, 0)
##        sizer_3.Add(sizer_16, 1, wx.EXPAND, 0)
##        sizer_18.Add(self.label_12, 0, wx.ALL, 5)
##        sizer_18.Add(self.text_ctrl_8, 0, 0, 0)
##        sizer_18.Add(self.button_1, 0, 0, 0)
##        sizer_3.Add(sizer_18, 1, wx.EXPAND, 0)
##        sizer_17.Add(self.label_11, 0, wx.ALL, 5)
##        sizer_17.Add(self.text_ctrl_7, 0, 0, 0)
##        sizer_3.Add(sizer_17, 1, wx.EXPAND, 0)
##
##
##        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
##        sizer_8.Add(self.label_3, 0, wx.ALL, 5)
##        sizer_8.Add(self.checkbox_2, 0, wx.ALL, 5)
##        sizer_4.Add(sizer_8, 1, wx.EXPAND, 0)
##        sizer_12.Add(self.label_6, 0, wx.ALL, 5)
##        sizer_12.Add(self.text_ctrl_2, 0, 0, 0)
##        sizer_4.Add(sizer_12, 1, wx.EXPAND, 0)
##        sizer_13.Add(self.label_8, 0, wx.ALL, 5)
##        sizer_13.Add(self.text_ctrl_3, 0, 0, 0)
##        sizer_4.Add(sizer_13, 1, wx.EXPAND, 0)
##        sizer_14.Add(self.label_9, 0, wx.ALL, 5)
##        sizer_14.Add(self.text_ctrl_5, 0, 0, 0)
##        sizer_4.Add(sizer_14, 1, wx.EXPAND, 0)
##        sizer_15.Add(self.label_10, 0, wx.ALL, 5)
##        sizer_15.Add(self.text_ctrl_6, 0, 0, 0)
##        sizer_4.Add(sizer_15, 1, wx.EXPAND, 0)
##        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
##        self.notebook_1_pane_3.SetSizer(sizer_2)
##
##
##        self.notebook_1.AddPage(self.notebook_1_pane_1, u"界面设置")
##        self.notebook_1.AddPage(self.notebook_1_pane_2, u"控制设置")
##        self.notebook_1.AddPage(self.notebook_1_pane_3, u"下载设置")
##        sizer_5.Add(self.notebook_1, 1, wx.EXPAND, 0)
##        grid_sizer_1.Add((20, 20), 0, 0, 0)
##        grid_sizer_1.Add(self.button_4, 0, 0, 0)
##        grid_sizer_1.Add((20, 20), 0, 0, 0)
##        grid_sizer_1.Add(self.button_5, 0, 0, 0)
##        grid_sizer_1.Add((20, 20), 0, 0, 0)
##        sizer_5.Add(grid_sizer_1, 0, wx.EXPAND, 0)
##        self.SetSizer(sizer_5)
##        sizer_5.Fit(self)
##        self.Layout()
##        # end wxGlade
##
##    def OnSelFont(self,event):
##        global GlobalConfig
##        data=wx.FontData()
##        data.SetInitialFont(GlobalConfig['CurFont'])
##        data.SetColour(GlobalConfig['CurFColor'])
##        data.EnableEffects(True)
##        dlg = wx.FontDialog(self, data)
##        if dlg.ShowModal() == wx.ID_OK:
##            ft=dlg.GetFontData().GetChosenFont()
##            self.text_ctrl_4.SetFont(ft)
##            txt=self.text_ctrl_4.GetValue()
##            self.text_ctrl_4.SetValue(txt)
##
##        dlg.Destroy()
##
##    def OnSelFColor(self,event):
##        global GlobalConfig
##        dlg = wx.ColourDialog(self)
##        dlg.GetColourData().SetChooseFull(True)
##        if dlg.ShowModal() == wx.ID_OK:
##            data = dlg.GetColourData()
##            self.text_ctrl_4.SetForegroundColour(data.GetColour())
##            self.Refresh()
##            #self.Update()
##            txt=self.text_ctrl_4.GetValue()
##            self.text_ctrl_4.SetValue(txt)
##        dlg.Destroy()
##
##    def OnSelBColor(self,event):
##        global GlobalConfig
##        dlg = wx.ColourDialog(self)
##        dlg.GetColourData().SetChooseFull(True)
##        if dlg.ShowModal() == wx.ID_OK:
##            data = dlg.GetColourData()
##            self.text_ctrl_4.SetBackgroundColour(data.GetColour())
##            self.text_ctrl_4.Refresh()
##            txt=self.text_ctrl_4.GetValue()
##            self.text_ctrl_4.SetValue(txt)
##
##        dlg.Destroy()
##
##    def OnSaveTheme(self,event):
##        global ThemeList
##        l={}
##        l['name']=''
##        while l['name']=='':
##            dlg = wx.TextEntryDialog(
##                    self, u'请输入新显示方案的名称(不能为空)：',
##                    u'另存为新方案')
##            if dlg.ShowModal() == wx.ID_OK:
##                l['name']=dlg.GetValue().strip()
##                dlg.Destroy()
##            else:
##                dlg.Destroy()
##                return
##        for t in ThemeList:
##            if t['name']==l['name']:
##                dlg = wx.MessageDialog(self, u'已经有叫这个名字的显示方案了，你确定要覆盖原有方案吗？',u"提示！",wx.YES_NO|wx.ICON_QUESTION)
##                if dlg.ShowModal()==wx.ID_NO:
##                    dlg.Destroy()
##                    return
##                else:
##                    ThemeList.remove(t)
##        l['font']=self.text_ctrl_4.GetFont()
##        l['fcolor']=self.text_ctrl_4.GetForegroundColour()
##        l['bcolor']=self.text_ctrl_4.GetBackgroundColour()
##        l['config']=unicode(l['font'].GetPointSize())+u':'+unicode(l['font'].GetFamily())+u':'+unicode(l['font'].GetStyle())+u':'+unicode(l['font'].GetWeight())+u':'+unicode(l['font'].GetUnderlined())+u':'+l['font'].GetFaceName()+u':'+unicode(l['font'].GetDefaultEncoding())+u':'+unicode(l['fcolor'])+u':'+unicode(l['bcolor'])
##        ThemeList.append(l)
##        self.combo_box_1.Clear()
##        for t in ThemeList:
##            self.combo_box_1.Append(t['name'])
##        self.combo_box_1.SetSelection(self.combo_box_1.GetCount()-1)
##
##
##
##
##    def OnDelTheme(self,event):
##        global ThemeList
##        name=self.combo_box_1.GetStringSelection()
##        i=0
##        if name<>u'':
##           for t in ThemeList:
##               if t['name']==name:
##                   ThemeList.remove(t)
##                   break
##               i+=1
##           self.combo_box_1.Clear()
##           self.combo_box_1.SetValue('')
##           for t in ThemeList:
##               self.combo_box_1.Append(t['name'])
##           self.combo_box_1.SetSelection(0)
##
##
##
##    def OnSel(self,event):
##        global ThemeList
##        name=self.combo_box_1.GetStringSelection()
##        if name<>u'':
##           for t in ThemeList:
##               if t['name']==name:
##                   self.text_ctrl_4.SetFont(t['font'])
##                   self.text_ctrl_4.SetForegroundColour(t['fcolor'])
##                   self.text_ctrl_4.SetBackgroundColour(t['bcolor'])
##                   self.text_ctrl_4.Refresh()
##                   txt=self.text_ctrl_4.GetValue()
##                   self.text_ctrl_4.SetValue(txt)
##                   break
##
##    def OnOk(self,event):
##        global ThemeList,GlobalConfig
##        GlobalConfig['CurFont']=self.text_ctrl_4.GetFont()
##        GlobalConfig['CurFColor']=self.text_ctrl_4.GetForegroundColour()
##        GlobalConfig['CurBColor']=self.text_ctrl_4.GetBackgroundColour()
##        GlobalConfig['LoadLastFile']=self.checkbox_1.GetValue()
##        GlobalConfig['EnableSidebarPreview']=self.checkbox_Preview.GetValue()
##        GlobalConfig['VerCheckOnStartup']=self.checkbox_VerCheck.GetValue()
##        if GlobalConfig['ShowAllFileInSidebar']==self.checkbox_5.GetValue():
##            self.GetParent().UpdateSidebar=True
##        GlobalConfig['ShowAllFileInSidebar']=not self.checkbox_5.GetValue()
##
##        try:
##            GlobalConfig['AutoScrollInterval']=float(self.text_ctrl_1.GetValue())*1000
##        except:
##            GlobalConfig['AutoScrollInterval']=12000
##        try:
##            GlobalConfig['MaxOpenedFiles']=abs(int(self.text_ctrl_mof.GetValue()))
##        except:
##            GlobalConfig['MaxOpenedFiles']=5
##        try:
##            GlobalConfig['RemindInterval']=abs(int(self.text_ctrl_1_copy.GetValue()))
##        except:
##            GlobalConfig['RemindInterval']=60
##
##        GlobalConfig['DAUDF']=self.choice_1.GetSelection()
##        GlobalConfig['useproxy']=self.checkbox_2.GetValue()
##        GlobalConfig['proxyserver']=self.text_ctrl_2.GetValue()
##        try:
##            GlobalConfig['proxyport']=int(self.text_ctrl_3.GetValue())
##        except:
##            GlobalConfig['proxyport']=0
##        GlobalConfig['proxyuser']=self.text_ctrl_5.GetValue()
##        GlobalConfig['proxypass']=self.text_ctrl_6.GetValue()
##        try:
##            GlobalConfig['numberofthreads']=int(self.text_ctrl_7.GetValue())
##        except:
##            GlobalConfig['numberofthreads']=1
##        if GlobalConfig['numberofthreads']<=0 or GlobalConfig['numberofthreads']>50:
##            GlobalConfig['numberofthreads']=1
##        if not os.path.exists(self.text_ctrl_8.GetValue()):
##            GlobalConfig['defaultsavedir']=''
##        else:
##            GlobalConfig['defaultsavedir']=self.text_ctrl_8.GetValue()
##        if GlobalConfig['defaultsavedir']=='' and GlobalConfig['DAUDF']==2:
##            dlg = wx.MessageDialog(self, u'请指定正确的缺省保存目录!',
##                               u'出错了！',
##                               wx.OK | wx.ICON_ERROR
##                               )
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
##
##        self.Destroy()
##
##    def OnCancell(self,event):
##        self.Destroy()
##
##    def OnKey(self,event):
##        key=event.GetKeyCode()
##        if key==wx.WXK_ESCAPE:
##            self.Destroy()
##        else:
##            event.Skip()
##
##
##    def OnWinActive(self,event):
##        if event.GetActive():self.text_ctrl_4.SetFocus()
##
##    def SelectDir(self,event):
##        dlg = wx.DirDialog(self, u"请选择目录：",defaultPath=GlobalConfig['LastDir'],
##                          style=wx.DD_DEFAULT_STYLE
##                           )
##        if dlg.ShowModal() == wx.ID_OK:
##            self.text_ctrl_8.SetValue(dlg.GetPath())
##
##        dlg.Destroy()
##


##class HelpDialog(wx.Dialog):
##    def __init__(self, parent,mode="help"):
##        # begin wxGlade: HelpDialog.__init__
##        #kwds["style"] = wx.DEFAULT_DIALOG_STYLE
##        wx.Dialog.__init__(self,parent,id=-1,title="")
##        self.text_ctrl_1 = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)
##        self.button_1 = wx.Button(self, -1, u"确定")
##
##        self.__set_properties(mode)
##        self.__do_layout()
##        # end wxGlade
##        self.Bind(wx.EVT_BUTTON,self.OnOK,self.button_1)
##        self.text_ctrl_1.Bind(wx.EVT_CHAR,self.OnKey)
##        self.Bind(wx.EVT_ACTIVATE,self.OnWinActive)
##
##    def __set_properties(self,mode):
##        # begin wxGlade: HelpDialog.__set_properties
##        self.SetTitle(u"帮助")
##        if mode=="help":self.text_ctrl_1.SetMinSize((500,400))
##        else:
##            self.text_ctrl_1.SetMinSize((700,400))
##        self.text_ctrl_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
##        # end wxGlade
##        if mode=="help":fname=cur_file_dir()+u"/LiteBook_Readme.txt"
##        else:
##            fname=cur_file_dir()+u"/LiteBook_WhatsNew.txt"
###        try:
##        f=open(fname,'r')
##        t_buff=f.read()
###        except:
###            dlg = wx.MessageDialog(self, u'帮助文件LiteBook_Readme.txt打开错误！',u"错误！",wx.OK|wx.ICON_ERROR)
###            dlg.ShowModal()
###            dlg.Destroy()
###            return False
##        coding=DetectFileCoding(GlobalConfig['ConfigDir']+u"/LiteBook_Readme.txt")
##        if coding=='error': return False
##        utext=AnyToUnicode(t_buff,coding)
##        self.text_ctrl_1.SetValue(utext)
##        f.close()
##
##    def __do_layout(self):
##        # begin wxGlade: HelpDialog.__do_layout
##        sizer_1 = wx.BoxSizer(wx.VERTICAL)
##        sizer_1.Add(self.text_ctrl_1, 1, wx.EXPAND, 0)
##        sizer_1.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
##        self.SetSizer(sizer_1)
##        sizer_1.Fit(self)
##        self.Layout()
##        # end wxGlade
##
##    def OnOK(self,event):
##        self.Destroy()
##
##    def OnKey(self,event):
##        key=event.GetKeyCode()
##        if key==wx.WXK_ESCAPE:
##            self.Destroy()
##        else:
##            event.Skip()
##
##
##    def OnWinActive(self,event):
##        if event.GetActive():self.text_ctrl_1.SetFocus()
### end of class HelpDialog
##
####class LiteBookApp(wx.PySimpleApp):
####    def __init__(self, *args, **kwds):
####        appname="litebook-"+wx.GetUserId()
####        m_checker=wx.SingleInstanceChecker(appname)
####        if m_checker.IsAnotherRunning()==True:
####            wx.LogError("已经有一个LiteBook的进程正在运行中")
####            print "error"
####            return False
####        wx.PySimpleApp.__init__(self, *args, **kwds)


class ClockThread:
    def __init__(self,win):
        self.win=win
        self.running=True
        thread.start_new_thread(self.run, ())

    def stop(self):
        self.running=False

    def run(self):
        global GlobalConfig,Ticking
        rt=0
        t=0
        while self.running:
            if Ticking:
                t+=1
                rt+=1
                thour=int(t/3600)
                tmin=int(t%3600/60)
                tsec=int(t%3600%60)
                if rt==GlobalConfig['RemindInterval']*60:
                    evt1=ReadTimeAlert(ReadTime=unicode(thour)+u'小时'+unicode(tmin)+u'分钟')
                    wx.PostEvent(self.win,evt1)
                    rt=0
                evt = UpdateStatusBarEvent(FieldNum = 2, Value =u'你已经阅读了 '+unicode(thour)+u'小时'+unicode(tmin)+u'分钟' )
                wx.PostEvent(self.win, evt)
            time.sleep(1)


class DisplayPosThread():

    def __init__(self,win):
        self.win=win
        self.running=True
        thread.start_new_thread(self.run, ())

    def stop(self):
        self.running=False

    def run(self):
        global OnScreenFileList
        while self.running:
##            evt=GetPosEvent()
            #wx.PostEvent(self.win, evt)
            percent=self.win.text_ctrl_1.GetPosPercent()
            (rlist,i,cname)=self.win.GetChapter()
            if percent<>False:
                percent=int(percent)
                try:
                    txt=unicode(percent)+u'%;'+cname+';'+OnScreenFileList[0][0]
                except:
                    txt=" "
                evt = UpdateStatusBarEvent(FieldNum = 0, Value =txt)
            else:
                evt = UpdateStatusBarEvent(FieldNum = 0, Value ='')
            wx.PostEvent(self.win, evt)
            time.sleep(0.5)


class VersionCheckThread():

    def __init__(self,win,notify=True):
        self.win=win
        self.running=True
        thread.start_new_thread(self.run, (notify,))

    def stop(self):
        self.running=False


    def run(self,notify):
        global I_Version
        upgrade=False
        osd={'Windows':'win','Linux':'linux','Darwin':'mac'}
        (iver,tver,wtsn)=VersionCheck()
        url=''
        if not iver:
            msg=u'版本检查过程中出错！'
        else:
            ver_f=iver
            if ver_f>I_Version:
                msg=u'LiteBook ver'+tver+u' 已经发布！\n'+wtsn
                url='http://code.google.com/p/litebook-project/downloads/list'
                upgrade=True
            else:
                msg=u'你使用的LiteBook已经是最新版本了。'

        if not notify and not upgrade:
            return
        else:
            evt=VerCheckEvent(imsg = msg, iurl = url)
            wx.PostEvent(self.win, evt)



class AutoCountThread():

    def __init__(self,win):
        self.win=win
        self.running=True
        thread.start_new_thread(self.run, ())

    def stop(self):
        self.running=False


    def run(self):
        global GlobalConfig
        i=int(GlobalConfig['AutoScrollInterval']/1000)
        while self.running:
            if self.win.autoscroll:
                evt = UpdateStatusBarEvent(FieldNum = 1, Value =u"自动翻页已开启:"+unicode(i))
                wx.PostEvent(self.win, evt)
                if i==0:
                    i=int(GlobalConfig['AutoScrollInterval']/1000)
                    evt=ScrollDownPage()
                    wx.PostEvent(self.win, evt)
                    #self.win.text_ctrl_1.ScrollPages(1)
                else:
                     i-=1
            else:
                evt = UpdateStatusBarEvent(FieldNum = 1, Value =u"自动翻页已关闭")
                wx.PostEvent(self.win, evt)
            time.sleep(1)


class MyConfig(ConfigParser.SafeConfigParser):



    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        if self._defaults:
            fp.write("[%s]\n" % ConfigParser.DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, unicode(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s = %s\n" %
                             (key, unicode(value).replace('\n', '\n\t')))
            fp.write("\n")

class PreviewFrame(wx.Frame):
    """The Preview Frame for dir sidebar"""
    def __init__(self, *args, **kwds):
        # begin wxGlade: PreviewFrame.__init__
        kwds["style"] = wx.CAPTION|wx.FRAME_TOOL_WINDOW
        wx.Frame.__init__(self, *args, **kwds)
        self.text_ctrl_1 = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: PreviewFrame.__set_properties
        self.SetTitle(u"预览")
        self.SetSize((400, 200))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: PreviewFrame.__do_layout
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(self.text_ctrl_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        self.Layout()
        # end wxGlade
    def SetText(self,strtxt):
        self.text_ctrl_1.SetValue(strtxt)

# end of class PreviewFrame

class VerCheckDialog(wx.Dialog):
    def __init__(self,parent,msg):
        wx.Dialog.__init__(self, parent,-1,u'版本检查结果')
        sizer = wx.BoxSizer(wx.VERTICAL)

        txtctrl = wx.TextCtrl(self,-1,size=(300,200),style=wx.TE_MULTILINE|wx.TE_READONLY )
        sizer.Add(txtctrl, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        txtctrl.SetValue(msg)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        btn_ok = wx.Button(self,wx.ID_OK,label=u'确定')
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)

        btn_download = wx.Button(self,wx.ID_APPLY,label=u'下载')
        btnsizer.AddButton(btn_download)
        btnsizer.Realize()

        sizer.Add(btnsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)


        self.SetSizer(sizer)
        sizer.Fit(self)

        self.Bind(wx.EVT_BUTTON,self.OnOK,btn_ok)
        self.Bind(wx.EVT_BUTTON,self.OnDown,btn_download)
        self.SetTitle

    def OnOK(self,event):
        self.Destroy()

    def OnDown(self,evt):
        import webbrowser
        webbrowser.open('http://code.google.com/p/litebook-project/downloads/list')

##class VerCheckDialog(wx.Dialog):
##    def __init__(self,msg,url):
##        #begin wxGlade: VerCheckDialog.__init__
##        #kwds["style"] = wx.DEFAULT_DIALOG_STYLE
##        wx.Dialog.__init__(self,None,-1)
##        if url<>'':
##            self.label_1 = hl.HyperLinkCtrl(self, wx.ID_ANY,msg,URL=url)
##        else:
##            self.label_1 = wx.StaticText(self, -1, msg)
##        self.button_1 = wx.Button(self, -1, " OK ")
##        self.Bind(wx.EVT_BUTTON,self.OnOK,self.button_1)
##        self.__set_properties()
##        self.__do_layout()
##        # end wxGlade
##
##    def __set_properties(self):
##        # begin wxGlade: VerCheckDialog.__set_properties
##        self.SetTitle(u"检查更新")
##        # end wxGlade
##
##    def __do_layout(self):
##        # begin wxGlade: VerCheckDialog.__do_layout
##        sizer_1 = wx.BoxSizer(wx.VERTICAL)
##        sizer_2 = wx.BoxSizer(wx.VERTICAL)
##        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_2_copy = wx.BoxSizer(wx.VERTICAL)
##        sizer_3_copy = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_2_copy.Add((200, 40), 0, wx.EXPAND, 0)
##        sizer_3_copy.Add((20, 20), 1, wx.EXPAND, 0)
##        sizer_3_copy.Add(self.label_1, 0, 0, 0)
##        sizer_3_copy.Add((20, 20), 1, wx.EXPAND, 0)
##        sizer_2_copy.Add(sizer_3_copy, 1, wx.EXPAND, 0)
##        sizer_1.Add(sizer_2_copy, 1, wx.EXPAND, 0)
##        sizer_2.Add((200, 20), 0, wx.EXPAND, 0)
##        sizer_3.Add((20, 20), 1, wx.EXPAND, 0)
##        sizer_3.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
##        sizer_3.Add((20, 20), 1, wx.EXPAND, 0)
##        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
##        sizer_2.Add((200, 20), 0, wx.EXPAND, 0)
##        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
##        self.SetSizer(sizer_1)
##        sizer_1.Fit(self)
##        self.Layout()
##        # end wxGlade
##
### end of class VerCheckDialog
##    def OnOK(self,event):
##        self.Destroy()

class FileHistoryDialog(wx.Dialog,wx.lib.mixins.listctrl.ColumnSorterMixin):
    def __init__(self, *args, **kwds):
        # begin wxGlade: FileHistory.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.list_ctrl_1 = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.button_1 = wx.Button(self, -1, u"打开")
        self.button_2 = wx.Button(self, -1, u"取消")
        self.button_3 = wx.Button(self, -1, u"全部清空")
        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.Bind(wx.EVT_BUTTON, self.OnLoadFile, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.clearHistory, self.button_3)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnLoadFile,self.list_ctrl_1)
        self.list_ctrl_1.Bind(wx.EVT_CHAR,self.OnKey)
        self.list_ctrl_1.InsertColumn(0,u'文件名',width=300)
        self.list_ctrl_1.InsertColumn(2,u'日期',width=120)
        self.image_list=wx.ImageList(16,16,mask=False,initialCount=5)
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/up.png",wx.BITMAP_TYPE_ANY)
        self.up=self.image_list.Add(bmp)
        #self.file_icon_list["up"]=8
        bmp=wx.Bitmap(GlobalConfig['IconDir']+u"/down.png",wx.BITMAP_TYPE_ANY)
        self.dn=self.image_list.Add(bmp)
        self.list_ctrl_1.AssignImageList(self.image_list,wx.IMAGE_LIST_SMALL)
        #self.file_icon_list["down"]=9
        self.itemDataMap={}
        wx.lib.mixins.listctrl.ColumnSorterMixin.__init__(self,3)
        self.filename=''
        self.ftype=''
        self.zfilename=''
        self.load_history()


    def __set_properties(self):
        # begin wxGlade: FileHistory.__set_properties
        self.SetTitle(u"已打开文件历史")
        self.SetSize((700, 700))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: FileHistory.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.list_ctrl_1, 8, wx.EXPAND, 0)
        sizer_1.Add((450, 5), 0, 0, 0)
        sizer_2.Add((20, 20), 0, 0, 0)
        sizer_2.Add(self.button_1, 0, 0, 0)
        sizer_2.Add((20, 20), 0, 0, 0)
        sizer_2.Add(self.button_2, 0, 0, 0)
        sizer_2.Add((20, 20), 0, 0, 0)
        sizer_2.Add(self.button_3, 0, 0, 0)
        sizer_2.Add((20, 20), 0, 0, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        sizer_1.Add((20, 5), 0, 0, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade
#unicode(filename)+"','"+ftype+"','"+unicode(zfile)+"',"+str(time.time())
    def load_history(self):
        global SqlCur
        SqlCur.execute("select * from book_history order by date desc")
        for row in SqlCur:
            filename=row[0]
            ftype=row[1]
            zfilename=row[2]
            filedate=row[3]
            filedate_data=filedate
            filedate=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(filedate))
            if ftype<>'normal':
                filename=zfilename+"|"+filename
            index=self.list_ctrl_1.InsertStringItem(sys.maxint,filename)
            self.list_ctrl_1.SetStringItem(index,1,filedate)
            self.list_ctrl_1.SetItemData(index,index)
            self.itemDataMap[index]=(filename,filedate_data)

    def GetSortImages(self):
        return (self.dn,self.up)

    def GetListCtrl(self):
        return self.list_ctrl_1

    def OnCancell(self, event):
        self.Hide()

    def clearHistory(self, event):
        global SqlCon,SqlCur
        dlg=wx.MessageDialog(self,u"此操作将清除所有已打开文件历史，是否继续？",u"清除已打开文件历史",wx.YES_NO|wx.NO_DEFAULT)
        if dlg.ShowModal()==wx.ID_YES:
            SqlCur.execute("delete from book_history")
            SqlCon.commit()
            self.list_ctrl_1.DeleteAllItems()
        dlg.Destroy()
        self.Hide()

    def OnLoadFile(self, event):
        filepath=self.list_ctrl_1.GetItemText(self.list_ctrl_1.GetFirstSelected())
        if filepath.find("|")==-1:
            self.Parent.LoadFile((filepath,))
        else:
            (zfilename,filename)=filepath.split('|',1)
            self.Parent.LoadFile((filename,),'zip',zfilename)
        self.Hide()

    def OnKey(self,event):
        key=event.GetKeyCode()
        if key==wx.WXK_ESCAPE:
            self.Hide()
        else:
            event.Skip()


# end of class FileHistory

class Search_Web_Dialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        global SqlCur
        # begin wxGlade: Search_Web_Dialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        weblist=[]
        flist=glob.glob(cur_file_dir()+"/plugin/*.py")
        for f in flist:
            bname=os.path.basename(f)
            weblist.append(bname[:-3])
        weblist.insert(0,u'搜索所有网站')
        self.sizer_1_staticbox = wx.StaticBox(self, -1, u"搜索小说网站")
        self.label_2 = wx.StaticText(self, -1, u"关键字：    ")
        self.text_ctrl_2 = wx.TextCtrl(self, -1, "")
        self.text_ctrl_1 = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP)
        self.label_3 = wx.StaticText(self, -1, u"选择网站：")
        self.choice_1 = wx.Choice(self, -1, choices=weblist)
        self.button_3 = wx.Button(self, -1, u" 搜索 ")
        self.button_4 = wx.Button(self, -1, u" 取消 ")
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.button_3)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_4)
        self.text_ctrl_2.Bind(wx.EVT_CHAR,self.OnKey)
        self.choice_1.Bind(wx.EVT_CHAR,self.OnKey)
        self.Bind(wx.EVT_CHOICE, self.OnChosen, self.choice_1)





        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        global GlobalConfig
        # begin wxGlade: Search_Web_Dialog.__set_properties
        self.SetTitle(u"搜索网站")
        self.text_ctrl_2.SetMinSize((200, 35))
        self.choice_1.SetMinSize((200, 35))
        if GlobalConfig['lastweb']=='' or not os.path.exists(cur_file_dir()+"/plugin/"+GlobalConfig['lastweb']+'.py'):
            self.choice_1.Select(0)
            self.ShowDesc(self.choice_1.GetString(0))
        else:
            self.choice_1.SetStringSelection(GlobalConfig['lastweb'])
            self.ShowDesc(GlobalConfig['lastweb'])
        self.text_ctrl_2.SetValue(GlobalConfig['lastwebsearchkeyword'])
        self.text_ctrl_1.SetMinSize((285, 84))

        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: Search_Web_Dialog.__do_layout
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.label_2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(self.text_ctrl_2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        sizer_3.Add(self.label_3, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_3.Add(self.choice_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_1.Add(self.text_ctrl_1, 0, wx.EXPAND, 0)
        #sizer_4.Add(self.button_3, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        #sizer_4.Add(self.button_4, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        sizer_4.Add(self.button_3,0,wx.ALIGN_CENTER_VERTICAL,0)
        sizer_4.Add(self.button_4,0,wx.ALIGN_CENTER_VERTICAL,0)
        sizer_1.Add(sizer_4, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def ShowDesc(self,desc):
        global PluginList
        self.text_ctrl_1.SetValue(u'此插件无介绍。')
        if desc<>u'搜索所有网站':
            try:
                self.text_ctrl_1.SetValue(PluginList[desc+'.py'].Description)
            except:
                pass


    def OnChosen(self,event):
        global lastweb
        GlobalConfig['lastweb']=self.choice_1.GetString(event.GetInt())
        self.ShowDesc(event.GetString())


    def OnCancell(self, event):
        self.Destroy()

    def OnOK(self,event):
        self.sitename=self.choice_1.GetString(self.choice_1.GetSelection())
        self.keyword=self.text_ctrl_2.GetValue()
        GlobalConfig['lastwebsearchkeyword']=self.keyword
        self.Close()

    def OnKey(self,event):
        key=event.GetKeyCode()
        if key==wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()



class web_search_result_dialog(wx.Dialog):
    def __init__(self, parent,sitename,keyword):
        global PluginList
        # begin wxGlade: web_search_result_dialog.__init__
        #kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self,parent,-1,style=wx.DEFAULT_DIALOG_STYLE)
        self.list_ctrl_1 = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.list_ctrl_1.InsertColumn(0,u'书名',width=320)
        self.list_ctrl_1.InsertColumn(1,u'作者')
        self.list_ctrl_1.InsertColumn(2,u'状态')
        self.list_ctrl_1.InsertColumn(3,u'大小')
        self.list_ctrl_1.InsertColumn(4,u'最后更新')
        self.list_ctrl_1.InsertColumn(5,u'网站')
        self.button_1 = wx.Button(self, -1, u" 下载(后台) ")
        self.button_2 = wx.Button(self, -1, u" 取消 ")


        dlg = wx.ProgressDialog(u"搜索中",
                       u"搜索进行中...",
                       maximum = 100,
                       parent=self,
                       style =
                         wx.PD_SMOOTH
                         |wx.PD_AUTO_HIDE
                        )
        self.rlist=[]
        if sitename<>u'搜索所有网站':
            self.rlist=None
            self.rlist=PluginList[sitename+'.py'].GetSearchResults(keyword,useproxy=GlobalConfig['useproxy'],proxyserver=GlobalConfig['proxyserver'],proxyport=GlobalConfig['proxyport'],proxyuser=GlobalConfig['proxyuser'],proxypass=GlobalConfig['proxypass'])
            for x in self.rlist:
                x['sitename']=sitename
        else:
            sr=[]
            flist=glob.glob(cur_file_dir()+"/plugin/*.py")
            for x in range(len(flist)):
                sr.append(-1)

            i=0
            crv=threading.Condition()
            srm=[]

            for f in flist:
                bname=os.path.basename(f)

                m=SearchThread(self,PluginList[bname],keyword,sr,i,crv)
                srm.append(bname[:-3])
                i+=1
            isfinished=False
            while isfinished<>True:
                time.sleep(1)
                isfinished=isfull(sr)
                if isfinished==True: dlg.Update(100)
                else:
                    dlg.Update(isfinished)
            self.rlist=[]
            i=0

            for x in sr:
                if x != None and x != -1:
                    for m in x:
                        m['sitename']=srm[i]
                    self.rlist+=x
                i+=1

        dlg.Update(100)
        dlg.Destroy()
        if self.rlist<>None:
            i=0
            for r in self.rlist:
                index=self.list_ctrl_1.InsertStringItem(sys.maxint,r['bookname'])
                self.list_ctrl_1.SetStringItem(index,1,r['authorname'])
                self.list_ctrl_1.SetStringItem(index,2,r['bookstatus'])
                self.list_ctrl_1.SetStringItem(index,3,r['booksize'])
                self.list_ctrl_1.SetStringItem(index,4,r['lastupdatetime'])
                self.list_ctrl_1.SetStringItem(index,5,r['sitename'])
                self.list_ctrl_1.SetItemData(index,i)

                i+=1
        else:
            dlg = wx.MessageDialog(self, u'搜索失败！',
                               u'出错了！',
                               wx.OK | wx.ICON_ERROR
                               )
            dlg.ShowModal()
            dlg.Destroy()
            self.Destroy()
            return None
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_2)
        self.list_ctrl_1.Bind(wx.EVT_CHAR,self.OnKey)
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: web_search_result_dialog.__set_properties
        self.SetTitle(u"搜索结果")
        self.list_ctrl_1.SetMinSize((709, 312))

        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: web_search_result_dialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.list_ctrl_1, 1, wx.EXPAND, 0)
        sizer_2.Add(self.button_1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(self.button_2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(sizer_2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def OnOK(self, event):
        global PluginList
        item=self.list_ctrl_1.GetNextSelected(-1)
        if item==-1:
            dlg = wx.MessageDialog(self, u'没有任何小说被选中！',
                                   u'错误',
                                   wx.OK | wx.ICON_ERROR
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            return
        siten=self.list_ctrl_1.GetItem(item,5).GetText()

        self.GetParent().DT=DownloadThread(self.GetParent(),self.rlist[self.list_ctrl_1.GetItemData(item)]['book_index_url'],PluginList[siten+'.py'],self.list_ctrl_1.GetItemText(item),siten+'.py')
        self.Destroy()

    def OnCancell(self, event):
        self.Destroy()

    def OnKey(self,event):
        key=event.GetKeyCode()
        if key==wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()



class WebSubscrDialog(wx.Dialog):
    def __init__(self, parent):
        global PluginList
        wx.Dialog.__init__(self,parent,-1,pos=(100,-1),style=wx.DEFAULT_DIALOG_STYLE)
        self.list_ctrl_1 = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list_ctrl_1.InsertColumn(0,u'书名',width=200)
        self.list_ctrl_1.InsertColumn(1,u'状态')
        self.list_ctrl_1.InsertColumn(2,u'网址')
        self.list_ctrl_1.InsertColumn(3,u'现有最后章名')
        self.list_ctrl_1.InsertColumn(4,u'现有章数')
        self.list_ctrl_1.InsertColumn(5,u'最后更新时间')
        self.list_ctrl_1.InsertColumn(6,u'本地路径')
        self.button_1 = wx.Button(self, -1, u" 更新 ")
        self.button_2 = wx.Button(self, -1, u" 取消 ")
        self.button_del = wx.Button(self, -1, u" 删除 ")
        self.button_read = wx.Button(self, -1, u" 阅读 ")
        self.button_selall = wx.Button(self, -1, u" 全选 ")


        self.tasklist={}
        self.sublist={}

        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.OnDel, self.button_del)
        self.Bind(wx.EVT_BUTTON, self.OnRead, self.button_read)
        self.Bind(wx.EVT_BUTTON, self.OnSelAll, self.button_selall)
        self.Bind(wx.EVT_CLOSE,self.OnCancell)
        self.Bind(EVT_UPD,self.UpdateFinish)
        self.Bind(wx.EVT_ACTIVATE,self.OnWinAct)
        self.list_ctrl_1.Bind(wx.EVT_CHAR,self.OnKey)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActive, self.list_ctrl_1)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        global SqlCur,SqlCon
        self.SetTitle(u"管理订阅")
        self.list_ctrl_1.SetMinSize((1000, 312))


    def __do_layout(self):
        # begin wxGlade: web_search_result_dialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.list_ctrl_1, 1, wx.EXPAND, 0)
        sizer_2.Add(self.button_selall, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(self.button_1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(self.button_del, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(self.button_read, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(self.button_2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(sizer_2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def OnSelAll(self,evt):
        item=-1
        while True:
            item=self.list_ctrl_1.GetNextItem(item)
            if item==-1:return
            self.list_ctrl_1.Select(item)

    def OnItemActive(self,evt):
        item=evt.GetIndex()
        url=self.list_ctrl_1.GetItem(item,2).GetText()
        self.GetParent().LoadFile([self.sublist[url]['save_path'],])
        self.Hide()

    def OnRead(self,evt):
        item=-1
        item=self.list_ctrl_1.GetNextSelected(item)
        if item == -1: return
        url=self.list_ctrl_1.GetItem(item,2).GetText()
        self.GetParent().LoadFile([self.sublist[url]['save_path'],])
        self.Hide()



    def OnDel(self,evt):
        global SqlCur,SqlCon
        item=-1
        while True:
            item=self.list_ctrl_1.GetNextSelected(item)
            if item == -1: return
            bkname=self.list_ctrl_1.GetItem(item,0).GetText()
            dlg=wx.MessageDialog(self,u"确定要删除订阅："+bkname+u"?",
                                u"删除订阅确认",
                                style=wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            if dlg.ShowModal()==wx.ID_YES:
                url=self.list_ctrl_1.GetItem(item,2).GetText()
                del self.sublist[url]
                if url in self.tasklist.keys():
                    del self.tasklist[url]
                self.list_ctrl_1.DeleteItem(item)
                sqlstr="delete from subscr where index_url='%s'" % url
                SqlCur.execute(sqlstr)
                SqlCon.commit




    def updateList(self):
        global SqlCur
        SqlCur.execute("select * from subscr")
        dblist=[]
        for row in SqlCur:
            if row[1] not in self.sublist.keys():
                bookname=row[0]
                index_url=row[1]
                lc_name=row[2]
                lc_date=row[3]
                chapter_count=row[4]
                save_path=row[5]
                plugin_name=row[6]
                self.sublist[index_url]={'bookname':bookname,'last_chapter':lc_name,
                                         'last_update':lc_date,'save_path':save_path,
                                         'plugin_name':plugin_name,
                                         'ccount':chapter_count
                                        }
                index=self.list_ctrl_1.InsertStringItem(sys.maxint,bookname)
                self.list_ctrl_1.SetStringItem(index,2,index_url)
                self.list_ctrl_1.SetStringItem(index,3,lc_name)
                self.list_ctrl_1.SetStringItem(index,4,str(chapter_count))
                self.list_ctrl_1.SetStringItem(index,5,lc_date)
                self.list_ctrl_1.SetStringItem(index,6,save_path)
        self.list_ctrl_1.SetColumnWidth(3,wx.LIST_AUTOSIZE)
        self.list_ctrl_1.SetColumnWidth(4,wx.LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl_1.SetColumnWidth(5,wx.LIST_AUTOSIZE)




    def loadDB(self):
        global SqlCur
        SqlCur.execute("select * from subscr")
        self.sublist.clear()
        for row in SqlCur:
            bookname=row[0]
            index_url=row[1]
            lc_name=row[2]
            lc_date=row[3]
            chapter_count=row[4]
            save_path=row[5]
            plugin_name=row[6]
            self.sublist[index_url]={'bookname':bookname,'last_chapter':lc_name,
                                     'last_update':lc_date,'save_path':save_path,
                                     'plugin_name':plugin_name,
                                     'ccount':chapter_count
                                    }
            index=self.list_ctrl_1.InsertStringItem(sys.maxint,bookname)
            self.list_ctrl_1.SetStringItem(index,2,index_url)
            self.list_ctrl_1.SetStringItem(index,3,lc_name)
            self.list_ctrl_1.SetStringItem(index,4,str(chapter_count))
            self.list_ctrl_1.SetStringItem(index,5,lc_date)
            self.list_ctrl_1.SetStringItem(index,6,save_path)
            #self.list_ctrl_1.SetItemData(index,plugin_name)
            #self.itemDataMap[index]=(filename,filedate_data)

    def OnUpdate(self, event):
        global PluginList
        item=-1
        while True:
            item=self.list_ctrl_1.GetNextSelected(item)
            if item == -1: return
            url=self.list_ctrl_1.GetItem(item,2).GetText()
            bkname=self.list_ctrl_1.GetItem(item,0).GetText()
            if url in self.tasklist.keys():
                dlg=wx.MessageDialog(self,bkname+u"正在更新中.",u'注意',
                                            style=wx.OK|wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                continue
            self.tasklist[url]=UpdateThread(self,url,
                                    PluginList[self.sublist[url]['plugin_name']]
                                            ,self.sublist[url]['bookname'],
                                            self.sublist[url]['plugin_name'],
                                            self.sublist[url]['ccount']
                                            )
            self.list_ctrl_1.SetStringItem(item,1,u'更新中')
            self.list_ctrl_1.Refresh()

    def UpdateItem(self,index,newstate,url):
        """
        update the list labels of given item
        """
        global SqlCur,SqlCon
        self.list_ctrl_1.SetStringItem(index,0,newstate['bookname'])
        self.list_ctrl_1.SetStringItem(index,2,url)
        self.list_ctrl_1.SetStringItem(index,3,newstate['last_chapter'])
        self.list_ctrl_1.SetStringItem(index,4,str(newstate['ccount']))
        self.list_ctrl_1.SetStringItem(index,5,newstate['last_update'])
        self.list_ctrl_1.SetStringItem(index,6,newstate['save_path'])
        sqlstr="update subscr set bookname='%s',last_chapter_name='%s', \
                last_update='%s',chapter_count=%s where index_url='%s' " % \
                (newstate['bookname'],newstate['last_chapter'],
                    newstate['last_update'],newstate['ccount'],url)
        SqlCur.execute(sqlstr)
        SqlCon.commit()




    def UpdateFinish(self,evt):
        item=-1
        bkstate=evt.bookstate
        if bkstate['index_url'] in self.tasklist.keys():
            del self.tasklist[bkstate['index_url']]
        while True:
            item=self.list_ctrl_1.GetNextItem(item)
            if item==-1:break
            if self.list_ctrl_1.GetItem(item,2).GetText()==bkstate['index_url']:
                break
        if item==-1:
            return False #corresponding task is not found in the list
        if evt.status != 'ok':
            self.list_ctrl_1.SetStringItem(item,1,u'更新失败')
            return False
        elif evt.bk=='':
            self.list_ctrl_1.SetStringItem(item,1,u'没有更新')
            self.sublist[bkstate['index_url']]['last_update']=datetime.today().strftime('%y-%m-%d %H:%M')
        else:
            self.list_ctrl_1.SetStringItem(item,1,u'新增%s章' % bkstate['chapter_count'])
            self.sublist[bkstate['index_url']]['last_chapter']=bkstate['last_chapter_name']
            self.sublist[bkstate['index_url']]['ccount']+=bkstate['chapter_count']
            self.sublist[bkstate['index_url']]['last_update']=datetime.today().strftime('%y-%m-%d %H:%M')
            encoding=DetectFileCoding(self.sublist[bkstate['index_url']]['save_path'])
            fp=codecs.open(self.sublist[bkstate['index_url']]['save_path'],encoding=encoding,mode='a')
            fp.write(evt.bk)
            fp.close()
        self.UpdateItem(item,self.sublist[bkstate['index_url']],bkstate['index_url'])



    def OnWinAct(self,evt):
        if evt.GetActive():
            self.updateList()

    def OnCancell(self, event):
        self.Hide()

    def OnKey(self,event):
        key=event.GetKeyCode()
        if key==wx.WXK_ESCAPE:
            self.Hide()
        else:
            event.Skip()


class UpdateThread:
    def __init__(self,win,url,plugin,bookname,plugin_name=None,last_chcount=0):
        self.win=win
        self.url=url
        self.plugin=plugin
        self.plugin_name=plugin_name
        self.bookname=bookname
        self.last_chcount=last_chcount
        #self.running=True
        thread.start_new_thread(self.run, ())

##    def stop(self):
##        self.running=False

    def run(self):
        evt2=DownloadUpdateAlert(Value='',FieldNum=3)
        self.bk,bkstate=self.plugin.GetBook(self.url,bkname=self.bookname,
                            win=self.win,evt=evt2,
                            useproxy=GlobalConfig['useproxy'],
                            proxyserver=GlobalConfig['proxyserver'],
                            proxyport=GlobalConfig['proxyport'],
                            proxyuser=GlobalConfig['proxyuser'],
                            proxypass=GlobalConfig['proxypass'],
                            concurrent=GlobalConfig['numberofthreads'],
                            mode='update',
                            last_chapter_count=self.last_chcount
                            )
        if self.bk<>None:
            evt1=UpdateEvt(name=self.bookname,status='ok',
                            bk=self.bk,bookstate=bkstate,
                            plugin_name=self.plugin_name,
                            )
        else:
            evt1=UpdateEvt(name=self.bookname,status='nok',bookstate=bkstate)
        wx.PostEvent(self.win,evt1)

class DownloadThread:
    def __init__(self,win,url,plugin,bookname,plugin_name=None):
        self.win=win
        self.url=url
        self.plugin=plugin
        self.plugin_name=plugin_name
        self.bookname=bookname
        #self.running=True
        thread.start_new_thread(self.run, ())

##    def stop(self):
##        self.running=False

    def run(self):
        evt2=DownloadUpdateAlert(Value='',FieldNum=3)
        self.bk,bkstate=self.plugin.GetBook(self.url,bkname=self.bookname,win=self.win,evt=evt2,useproxy=GlobalConfig['useproxy'],proxyserver=GlobalConfig['proxyserver'],proxyport=GlobalConfig['proxyport'],proxyuser=GlobalConfig['proxyuser'],proxypass=GlobalConfig['proxypass'],concurrent=GlobalConfig['numberofthreads'])
        if self.bk<>None:
            evt1=DownloadFinishedAlert(name=self.bookname,status='ok',bk=self.bk,bookstate=bkstate,plugin_name=self.plugin_name)
        else:
            evt1=DownloadFinishedAlert(name=self.bookname,status='nok')
        wx.PostEvent(self.win,evt1)

class SearchThread(threading.Thread):
    def __init__(self,win,plugin,keyword,sr,i,cv):
        threading.Thread.__init__(self,group=None, target=None, name=None, args=(), kwargs={})
        self.win=win
        self.plugin=plugin
        self.keyword=keyword
        self.sr=sr
        self.i=i
        self.cv=cv
        self.start()


    def run(self):
        global GlobalConfig
        self.cv.acquire()
        self.sr[self.i]=self.plugin.GetSearchResults(self.keyword,useproxy=GlobalConfig['useproxy'],proxyserver=GlobalConfig['proxyserver'],proxyport=GlobalConfig['proxyport'],proxyuser=GlobalConfig['proxyuser'],proxypass=GlobalConfig['proxypass'])
        self.cv.release()


class MyChoiceDialog(wx.Dialog):
    def __init__(self, parent,msg='',title='',mychoices=[],default=0):
        # begin wxGlade: MyChoiceDialog.__init__
        wx.Dialog.__init__(self,parent,-1,style=wx.DEFAULT_DIALOG_STYLE)
        self.sizer_1_staticbox = wx.StaticBox(self, -1, u"选择")
        self.label_1 = wx.StaticText(self, -1, msg)
        self.choice_1 = wx.Choice(self, -1, choices=mychoices)
        self.button_1 = wx.Button(self, -1, u"确定")
        self.button_2 = wx.Button(self, -1, u"取消")
        self.checkbox_subscr = wx.CheckBox(self, -1, u"加入订阅")
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_2)
        self.Bind(wx.EVT_CHOICE,self.OnChoice,self.choice_1)
        self.choice_1.Bind(wx.EVT_CHAR,self.OnKey)
        self.choice_1.Select(default)
        if default==0:
            self.checkbox_subscr.SetValue(False)
            self.checkbox_subscr.Disable()
        self.tit=title
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyChoiceDialog.__set_properties
        self.SetTitle(self.tit)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyChoiceDialog.__do_layout
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.label_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_1.Add(self.choice_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(self.checkbox_subscr, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(self.button_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(self.button_2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(sizer_2, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def OnCancell(self, event):
        self.Hide()

    def OnOK(self,event):
        self.sitename=self.choice_1.GetString(self.choice_1.GetSelection())
        self.chosen=self.choice_1.GetStringSelection()
        self.subscr=self.checkbox_subscr.GetValue()
        self.Hide()

    def OnChoice(self,evt):
        if self.choice_1.GetStringSelection() == u'另存为...':
            self.checkbox_subscr.Enable()
        else:
            self.checkbox_subscr.SetValue(False)
            self.checkbox_subscr.Disable()

    def OnKey(self,event):
        key=event.GetKeyCode()
        if key==wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()


class NewOptionDialog(wx.Dialog):
    def __init__(self, parent):
        # begin wxGlade: NewOptionDialog.__init__
        #kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent=parent,title=u'选项对话框',pos=(0,0))
        self.notebook_1 = wx.Notebook(self, -1, style=0)
        self.notebook_1_pane_4 = wx.Panel(self.notebook_1, -1)
        self.notebook_1_pane_3 = wx.Panel(self.notebook_1, -1)
        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, -1)
        self.notebook_1_pane_ltbnet = wx.Panel(self.notebook_1, -1)
        self.staticbox_ltbnet = wx.StaticBox(self.notebook_1_pane_ltbnet, -1, u"LTBNET设置")
        self.notebook_1_pane_1 = wx.ScrolledWindow(self.notebook_1, -1, style=wx.TAB_TRAVERSAL)
        self.sizer_5_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"显示主题")
        self.sizer_6_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"显示模式")
        self.sizer_9_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"背景色或图片背景")
        self.sizer_13_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"字体")
        self.sizer_14_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"下划线")
        self.sizer_16_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"间距设置")
        self.sizer_2_staticbox = wx.StaticBox(self.notebook_1_pane_2, -1, u"启动设置")
        self.sizer_8_staticbox = wx.StaticBox(self.notebook_1_pane_2, -1, u"时间间隔")
        self.sizer_25_staticbox = wx.StaticBox(self.notebook_1_pane_2, -1, u"其他")
        self.sizer_weball_staticbox = wx.StaticBox(self.notebook_1_pane_2, -1, u"Web服务器")
        self.sizer_32_staticbox = wx.StaticBox(self.notebook_1_pane_3, -1, u"下载")
        self.sizer_36_staticbox = wx.StaticBox(self.notebook_1_pane_3, -1, u"代理服务器")
        self.sizer_15_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"显示效果预览")
        self.sizer_26_staticbox = wx.StaticBox(self.notebook_1_pane_4, -1, u"按键方案")
        self.sizer_27_staticbox = wx.StaticBox(self.notebook_1_pane_4, -1, u"双击修改，右键增加删除")
        self.text_ctrl_3 = liteview.LiteView(self.notebook_1_pane_1, -1, "")
        self.combo_box_1 = wx.ComboBox(self.notebook_1_pane_1, -1, choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.button_1 = wx.Button(self.notebook_1_pane_1, -1, u"另存为")
        self.button_2 = wx.Button(self.notebook_1_pane_1, -1, u"删除")
        self.button_theme_import = wx.Button(self.notebook_1_pane_1, -1, u"导入")
        self.button_theme_export = wx.Button(self.notebook_1_pane_1, -1, u"导出")
        self.label_1 = wx.StaticText(self.notebook_1_pane_1, -1, u"选择显示模式：")
        self.combo_box_2 = wx.ComboBox(self.notebook_1_pane_1, -1, choices=[u"纸张模式", u"书本模式", u"竖排书本模式"], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.label_3 = wx.StaticText(self.notebook_1_pane_1, -1, u"选择背景图片：")
        self.text_ctrl_2 = wx.TextCtrl(self.notebook_1_pane_1, -1, "",style=wx.TE_READONLY)
        self.button_3 = wx.Button(self.notebook_1_pane_1, -1, u"选择")
        self.label_4 = wx.StaticText(self.notebook_1_pane_1, -1, u"背景图片排列方式：")
        self.combo_box_3 = wx.ComboBox(self.notebook_1_pane_1, -1, choices=[u"平铺", u"居中"], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.label_5 = wx.StaticText(self.notebook_1_pane_1, -1, u"选择背景色或背景图片：")
        self.combo_box_4 = wx.ComboBox(self.notebook_1_pane_1, -1, choices=[u"使用背景图片", u"使用背景色"], style=wx.CB_DROPDOWN|wx.CB_DROPDOWN|wx.CB_READONLY)
        self.button_4 = wx.Button(self.notebook_1_pane_1, -1, u"选择背景色")
        self.button_5 = wx.Button(self.notebook_1_pane_1, -1, u"选择字体")
        self.button_6 = wx.Button(self.notebook_1_pane_1, -1, u"字体颜色")
        self.label_6 = wx.StaticText(self.notebook_1_pane_1, -1, u"下划线样式")
        self.combo_box_5 = wx.ComboBox(self.notebook_1_pane_1, -1, choices=[u"不使用下划线", u"实线", u"虚线", u"长虚线", u"点虚线"], style=wx.CB_DROPDOWN|wx.CB_DROPDOWN|wx.CB_READONLY)
        self.button_7 = wx.Button(self.notebook_1_pane_1, -1, u"下划线颜色")
        self.label_7 = wx.StaticText(self.notebook_1_pane_1, -1, u"纸张模式页边距：")
        self.spin_ctrl_1 = wx.SpinCtrl(self.notebook_1_pane_1, -1, "", min=0, max=100)
        self.label_8 = wx.StaticText(self.notebook_1_pane_1, -1, u"书本模式页边距：")
        self.spin_ctrl_2 = wx.SpinCtrl(self.notebook_1_pane_1, -1, "", min=0, max=100)
        self.label_9 = wx.StaticText(self.notebook_1_pane_1, -1, u"竖排书本模式页边距：")
        self.spin_ctrl_3 = wx.SpinCtrl(self.notebook_1_pane_1, -1, "", min=0, max=100)
        self.label_10 = wx.StaticText(self.notebook_1_pane_1, -1, u"（竖排）书本模式页中距：")
        self.spin_ctrl_4 = wx.SpinCtrl(self.notebook_1_pane_1, -1, "", min=0, max=100)
        self.label_11 = wx.StaticText(self.notebook_1_pane_1, -1, u"行间距：")
        self.spin_ctrl_5 = wx.SpinCtrl(self.notebook_1_pane_1, -1, "", min=0, max=100)
        self.label_12 = wx.StaticText(self.notebook_1_pane_1, -1, u"竖排书本行间距：")
        self.spin_ctrl_6 = wx.SpinCtrl(self.notebook_1_pane_1, -1, "", min=0, max=100)
        self.checkbox_1 = wx.CheckBox(self.notebook_1_pane_2, -1, u"启动时自动载入上次阅读文件")
        self.checkbox_2 = wx.CheckBox(self.notebook_1_pane_2, -1, u"启动时检查版本更新")
        self.label_13 = wx.StaticText(self.notebook_1_pane_2, -1, u"自动翻页间隔（秒）：")
        self.spin_ctrl_8 = wx.SpinCtrl(self.notebook_1_pane_2, -1, "", min=0, max=100)
        self.label_14 = wx.StaticText(self.notebook_1_pane_2, -1, u"连续阅读提醒时间（分钟）：")
        self.spin_ctrl_9 = wx.SpinCtrl(self.notebook_1_pane_2, -1, "", min=0, max=100)
        self.checkbox_3 = wx.CheckBox(self.notebook_1_pane_2, -1, u"是否启用ESC作为老板键")
        self.checkbox_4 = wx.CheckBox(self.notebook_1_pane_2, -1, u"是否在文件选择侧边栏中预览文件内容")
        self.checkbox_5 = wx.CheckBox(self.notebook_1_pane_2, -1, u"是否只在文件选择侧边栏中只显示支持的文件类型")
        self.label_15 = wx.StaticText(self.notebook_1_pane_2, -1, u"最大曾经打开文件菜单数：")
        self.spin_ctrl_10 = wx.SpinCtrl(self.notebook_1_pane_2, -1, "", min=0, max=100)
        self.checkbox_webserver = wx.CheckBox(self.notebook_1_pane_2, -1, u"启动时运行Web服务器")
        self.label_webport = wx.StaticText(self.notebook_1_pane_2, -1, u"Web服务器端口：")
        self.spin_ctrl_webport = wx.SpinCtrl(self.notebook_1_pane_2, -1, "8000", min=1, max=65535)
        self.label_webroot = wx.StaticText(self.notebook_1_pane_2, -1, u"共享根目录：")
        self.text_ctrl_webroot = wx.TextCtrl(self.notebook_1_pane_2, -1, "", style=wx.TE_READONLY)
        self.button_webroot = wx.Button(self.notebook_1_pane_2, -1, u"选择")
        self.label_MDNS = wx.StaticText(self.notebook_1_pane_2, -1, u"绑定的网络接口：")
        self.combo_box_MDNS = wx.ComboBox(self.notebook_1_pane_2, -1, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)

        self.label_16 = wx.StaticText(self.notebook_1_pane_3, -1, u"下载完毕后的缺省动作：")
        self.combo_box_6 = wx.ComboBox(self.notebook_1_pane_3, -1, choices=[u"直接阅读", u"另存为文件", u"直接保存在缺省目录下"], style=wx.CB_DROPDOWN|wx.CB_DROPDOWN|wx.CB_READONLY)
        self.label_17 = wx.StaticText(self.notebook_1_pane_3, -1, u"保存的缺省目录：")
        self.label_ltbroot = wx.StaticText(self.notebook_1_pane_ltbnet, -1, u"LTBNET共享目录：")
        self.text_ctrl_1 = wx.TextCtrl(self.notebook_1_pane_3, -1, "")
        self.text_ctrl_ltbroot = wx.TextCtrl(self.notebook_1_pane_ltbnet, -1, "", size=(200,-1))
        self.label_ltbport = wx.StaticText(self.notebook_1_pane_ltbnet, -1, u"LTBNET端口(重启litebook后生效)：")
        self.spin_ctrl_ltbport = wx.SpinCtrl(self.notebook_1_pane_ltbnet, -1, "", min=1, max=65536)
        self.checkbox_upnp = wx.CheckBox(self.notebook_1_pane_ltbnet, -1, u"是否在启动时使用UPNP添加端口映射")
        self.checkbox_ltbnet = wx.CheckBox(self.notebook_1_pane_ltbnet, -1, u"是否启用LTBNET（重启litebook后生效）")
        self.button_12 = wx.Button(self.notebook_1_pane_3, -1, u"选择")
        self.button_ltbroot = wx.Button(self.notebook_1_pane_ltbnet, -1, u"选择")
        self.label_18 = wx.StaticText(self.notebook_1_pane_3, -1, u"同时下载的线程个数（需插件支持；不能超过50）：")
        self.spin_ctrl_11 = wx.SpinCtrl(self.notebook_1_pane_3, -1, "20", min=1, max=50)
        self.checkbox_6 = wx.CheckBox(self.notebook_1_pane_3, -1, u"启用代理服务器")
        self.label_19 = wx.StaticText(self.notebook_1_pane_3, -1, u"代理服务器地址：")
        self.text_ctrl_4 = wx.TextCtrl(self.notebook_1_pane_3, -1, "")
        self.label_20 = wx.StaticText(self.notebook_1_pane_3, -1, u"代理服务器端口：")
        self.spin_ctrl_12 = wx.SpinCtrl(self.notebook_1_pane_3, -1, "", min=1, max=65536)
        self.label_21 = wx.StaticText(self.notebook_1_pane_3, -1, u"用户名：")
        self.text_ctrl_5 = wx.TextCtrl(self.notebook_1_pane_3, -1, "")
        self.label_22 = wx.StaticText(self.notebook_1_pane_3, -1, u"密码：")
        self.text_ctrl_6 = wx.TextCtrl(self.notebook_1_pane_3, -1, "", style=wx.TE_PASSWORD)

        self.combo_box_7 = wx.ComboBox(self.notebook_1_pane_4, -1, choices=[], style=wx.CB_DROPDOWN)
        self.button_Key_Save = wx.Button(self.notebook_1_pane_4, -1, u"另存为")
        self.button_Key_Del = wx.Button(self.notebook_1_pane_4, -1, u"删除")
        self.button_key_import = wx.Button(self.notebook_1_pane_4, -1, u"导入")
        self.button_key_export = wx.Button(self.notebook_1_pane_4, -1, u"导出")
        self.grid_1 = keygrid.KeyConfigGrid(self.notebook_1_pane_4)


        self.button_10 = wx.Button(self, -1, u"确定")
        self.button_11 = wx.Button(self, -1, u"取消")


        #绑定事件处理
        self.Bind(wx.EVT_COMBOBOX,self.OnThemeSelect,self.combo_box_1)
        self.Bind(wx.EVT_COMBOBOX,self.OnKeySelect,self.combo_box_7)
        self.Bind(wx.EVT_COMBOBOX,self.OnShowmodeSelect,self.combo_box_2)
        self.Bind(wx.EVT_COMBOBOX,self.OnBGlayoutSelect,self.combo_box_3)
        self.Bind(wx.EVT_COMBOBOX,self.OnBGSet,self.combo_box_4)
        self.Bind(wx.EVT_COMBOBOX,self.OnSelULS,self.combo_box_5)
        self.Bind(wx.EVT_BUTTON,self.OnChoseWebRoot,self.button_webroot)
        self.Bind(wx.EVT_BUTTON,self.OnCancell,self.button_11)
        self.Bind(wx.EVT_BUTTON,self.OnDelTheme,self.button_2)
        self.Bind(wx.EVT_BUTTON,self.OnSaveTheme,self.button_1)
        self.Bind(wx.EVT_BUTTON,self.OnSelectBG,self.button_3)
        self.Bind(wx.EVT_BUTTON,self.OnSelFont,self.button_5)
        self.Bind(wx.EVT_BUTTON,self.OnSelFColor,self.button_6)
        self.Bind(wx.EVT_BUTTON,self.OnSelectBGColor,self.button_4)
        self.Bind(wx.EVT_BUTTON,self.OnSelectULColor,self.button_7)
        self.Bind(wx.EVT_BUTTON,self.SelectDir,self.button_12)
        self.Bind(wx.EVT_BUTTON,self.OnOK,self.button_10)
        self.Bind(wx.EVT_BUTTON,self.OnDelKey,self.button_Key_Del)
        self.Bind(wx.EVT_BUTTON,self.OnSaveKey,self.button_Key_Save)
        self.Bind(wx.EVT_BUTTON,self.OnImportKey,self.button_key_import)
        self.Bind(wx.EVT_BUTTON,self.OnExportKey,self.button_key_export)
        self.Bind(wx.EVT_BUTTON,self.OnExportTheme,self.button_theme_export)
        self.Bind(wx.EVT_BUTTON,self.OnImportTheme,self.button_theme_import)


        self.Bind(wx.EVT_SPINCTRL,self.OnUpdateSpace,self.spin_ctrl_1)
        self.Bind(wx.EVT_SPINCTRL,self.OnUpdateSpace,self.spin_ctrl_2)
        self.Bind(wx.EVT_SPINCTRL,self.OnUpdateSpace,self.spin_ctrl_3)
        self.Bind(wx.EVT_SPINCTRL,self.OnUpdateSpace,self.spin_ctrl_4)
        self.Bind(wx.EVT_SPINCTRL,self.OnUpdateSpace,self.spin_ctrl_5)
        self.Bind(wx.EVT_SPINCTRL,self.OnUpdateSpace,self.spin_ctrl_6)


        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        global GlobalConfig
        # begin wxGlade: NewOptionDialog.__set_properties
        self.SetTitle(u"选项对话框")
        self.SetSize((600, 500))
        self.text_ctrl_3.SetSize((450,300))
        self.combo_box_2.SetSelection(-1)
        self.text_ctrl_2.SetMinSize((300, -1))
        self.combo_box_3.SetSelection(-1)
        self.combo_box_4.SetSelection(-1)
        self.combo_box_5.SetSelection(0)
        self.notebook_1_pane_1.SetScrollRate(10, 10)
        self.combo_box_6.SetSelection(-1)
        self.text_ctrl_1.SetMinSize((150, -1))
        self.text_ctrl_4.SetMinSize((200, -1))
        self.spin_ctrl_11.SetMinSize((100,-1))
        self.text_ctrl_webroot.SetMinSize((200, -1))
        self.label_MDNS.SetToolTipString(u"选择WEB服务器及mDNS所绑定的网络接口，缺省情况下系统会自动选择WLAN接口")

        #set preview area to current setting
        self.text_ctrl_3.SetShowMode(GlobalConfig['showmode'])
        if GlobalConfig['backgroundimg']<>'' and GlobalConfig['backgroundimg']<>None:
            self.text_ctrl_3.SetImgBackground(GlobalConfig['backgroundimg'],GlobalConfig['backgroundimglayout'])
        else:
            self.text_ctrl_3.SetBackgroundColour(GlobalConfig['CurBColor'])
        self.text_ctrl_3.SetFColor(GlobalConfig['CurFColor'])
        self.text_ctrl_3.SetFont(GlobalConfig['CurFont'])
        self.text_ctrl_3.SetUnderline(GlobalConfig['underline'],GlobalConfig['underlinestyle'],GlobalConfig['underlinecolor'])
        self.text_ctrl_3.SetSpace(GlobalConfig['pagemargin'],GlobalConfig['bookmargin'],GlobalConfig['vbookmargin'],GlobalConfig['centralmargin'],GlobalConfig['linespace'],GlobalConfig['vlinespace'])
        self.text_ctrl_3.SetValue(u"《老子》八十一章\n\n　1.道可道，非常道。名可名，非常名。无名天地之始。有名万物之母。故常无欲以观其妙。常有欲以观其徼。此两者同出而异名，同谓之玄。玄之又玄，众妙之门。\n\n　2.天下皆知美之为美，斯恶矣；皆知善之为善，斯不善已。故有无相生，难易相成，长短相形，高下相倾，音声相和，前後相随。是以圣人处无为之事，行不言之教。万物作焉而不辞。生而不有，为而不恃，功成而弗居。夫唯弗居，是以不去。\n\n　3.不尚贤， 使民不争。不贵难得之货，使民不为盗。不见可欲，使民心不乱。是以圣人之治，虚其心，实其腹，弱其志，强其骨；常使民无知、无欲，使夫智者不敢为也。为无为，则无不治。\n\n　4.道冲而用之，或不盈。渊兮似万物之宗。解其纷，和其光，同其尘，湛兮似或存。吾不知谁之子，象帝之先。\n\n　5.天地不仁，以万物为刍狗。圣人不仁，以百姓为刍狗。天地之间，其犹橐迭乎？虚而不屈，动而愈出。多言数穷，不如守中。")
        #set initial value for display tab
        self.combo_box_1.Append(u'当前设置')
        for x in ThemeList:
            self.combo_box_1.Append(x['name'])
        self.combo_box_1.Select(0)

        if GlobalConfig['showmode']=='paper':
            self.combo_box_2.Select(0)
        else:
            if GlobalConfig['showmode']=='book': self.combo_box_2.Select(1)
            else:
                if GlobalConfig['showmode']=='vbook': self.combo_box_2.Select(2)

        if GlobalConfig['backgroundimg']<>'' and GlobalConfig['backgroundimg']<>None:
            self.combo_box_4.Select(0)
            self.text_ctrl_2.SetValue(GlobalConfig['backgroundimg'])
            if GlobalConfig['backgroundimglayout']=='tile':
                self.combo_box_3.Select(0)
            else:
                self.combo_box_3.Select(1)
        else:
            self.combo_box_4.Select(1)
            self.text_ctrl_2.Disable()
            self.button_3.Disable()
            self.combo_box_3.Disable()

        if GlobalConfig['underline']==False:
            self.combo_box_5.Select(0)
        else:
            if GlobalConfig['underlinestyle']==wx.SOLID: self.combo_box_5.Select(1)
            else:
                if GlobalConfig['underlinestyle']==wx.DOT: self.combo_box_5.Select(2)
                else:
                    if GlobalConfig['underlinestyle']==wx.LONG_DASH: self.combo_box_5.Select(3)
                    else:
                        if GlobalConfig['underlinestyle']==wx.DOT_DASH: self.combo_box_5.Select(4)
        self.spin_ctrl_1.SetValue(GlobalConfig['pagemargin'])
        self.spin_ctrl_2.SetValue(GlobalConfig['bookmargin'])
        self.spin_ctrl_3.SetValue(GlobalConfig['vbookmargin'])
        self.spin_ctrl_4.SetValue(GlobalConfig['centralmargin'])
        self.spin_ctrl_5.SetValue(GlobalConfig['linespace'])
        self.spin_ctrl_6.SetValue(GlobalConfig['vlinespace'])
        #set initial value for control tab
        self.checkbox_1.SetValue(GlobalConfig['LoadLastFile'])
        self.checkbox_3.SetValue(GlobalConfig['EnableESC'])
        if MYOS != 'Windows':
            self.checkbox_3.Disable()
        self.checkbox_4.SetValue(GlobalConfig['EnableSidebarPreview'])
        self.spin_ctrl_8.SetValue(GlobalConfig['AutoScrollInterval']/1000)
        self.spin_ctrl_9.SetValue(GlobalConfig['RemindInterval'])
        self.checkbox_2.SetValue(GlobalConfig['VerCheckOnStartup'])
        self.checkbox_5.SetValue(not GlobalConfig['ShowAllFileInSidebar'])
        self.spin_ctrl_10.SetValue(GlobalConfig['MaxOpenedFiles'])
        #set inital value for download tab
        self.combo_box_6.Select(GlobalConfig['DAUDF'])
        self.checkbox_6.SetValue(GlobalConfig['useproxy'])
        self.text_ctrl_4.SetValue(unicode(GlobalConfig['proxyserver']))
        self.spin_ctrl_12.SetValue(GlobalConfig['proxyport'])
        self.text_ctrl_5.SetValue(unicode(GlobalConfig['proxyuser']))
        self.text_ctrl_6.SetValue(unicode(GlobalConfig['proxypass']))
        self.spin_ctrl_11.SetValue(GlobalConfig['numberofthreads'])
        self.text_ctrl_1.SetValue(unicode(GlobalConfig['defaultsavedir']))


        #load the initial value for keyconfig tab
        for kconfig in KeyConfigList:
            if kconfig[0]<>'last':
                self.combo_box_7.Append(kconfig[0])
            else:
                self.combo_box_7.Append(u'当前设置')
        self.combo_box_7.Select(0)
        self.grid_1.Load(KeyConfigList[0])

        #set the initial value for web server
        self.checkbox_webserver.SetValue(GlobalConfig['RunWebserverAtStartup'])
        self.spin_ctrl_webport.SetValue(int(GlobalConfig['ServerPort']))
        self.text_ctrl_webroot.SetValue(GlobalConfig['ShareRoot'])
        #set the inital value for mDNS interface

        ip_int_name_list=[]
        if platform.system() == 'Linux':
            bus = dbus.SystemBus()
            proxy = bus.get_object("org.freedesktop.NetworkManager",
            "/org/freedesktop/NetworkManager")
            manager = dbus.Interface(proxy, "org.freedesktop.NetworkManager")
            # Get device-specific state
            devices = manager.GetDevices()
            for d in devices:
               dev_proxy = bus.get_object("org.freedesktop.NetworkManager", d)
               prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")

               # Get the device's current state and interface name
               state = prop_iface.Get("org.freedesktop.NetworkManager.Device", "State")
               name = prop_iface.Get("org.freedesktop.NetworkManager.Device", "Interface")
               ip_int_name_list.append(name)

        elif platform.system() == 'Darwin':
            for ifname in netifaces.interfaces(): #return addr of 1st network interface
                if ifname != 'lo0':
                    ip_int_name_list.append(ifname)


        self.combo_box_MDNS.Append(u"自动检测")
        self.combo_box_MDNS.AppendItems(ip_int_name_list)
        if GlobalConfig['mDNS_interface']=='AUTO':
            self.combo_box_MDNS.SetStringSelection(u'自动检测')
        else:
            self.combo_box_MDNS.SetStringSelection(GlobalConfig['mDNS_interface'])

        #set initial value for LTBNET
        self.spin_ctrl_ltbport.SetValue(GlobalConfig['LTBNETPort'])
        self.text_ctrl_ltbroot.SetValue(unicode(GlobalConfig['LTBNETRoot']))
        self.checkbox_upnp.SetValue(GlobalConfig['RunUPNPAtStartup'])
        self.checkbox_ltbnet.SetValue(GlobalConfig['EnableLTBNET'])

        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: NewOptionDialog.__do_layout
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_30 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_26 = wx.StaticBoxSizer(self.sizer_26_staticbox, wx.HORIZONTAL)
        sizer_27 = wx.StaticBoxSizer(self.sizer_27_staticbox, wx.HORIZONTAL)
        sizer_31 = wx.BoxSizer(wx.VERTICAL)
        sizer_36 = wx.StaticBoxSizer(self.sizer_36_staticbox, wx.VERTICAL)
        sizer_40 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_39 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_38 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_37 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_32 = wx.StaticBoxSizer(self.sizer_32_staticbox, wx.VERTICAL)
        sizer_35 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_34 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_33 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_weball = wx.StaticBoxSizer(self.sizer_weball_staticbox, wx.VERTICAL)
        sizer_web3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_web2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_MDNS = wx.BoxSizer(wx.HORIZONTAL)

        sizer_25 = wx.StaticBoxSizer(self.sizer_25_staticbox, wx.VERTICAL)
        sizer_29 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8 = wx.StaticBoxSizer(self.sizer_8_staticbox, wx.VERTICAL)
        sizer_24 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_23 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_16 = wx.StaticBoxSizer(self.sizer_16_staticbox, wx.VERTICAL)
        sizer_22 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_21 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_20 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14 = wx.StaticBoxSizer(self.sizer_14_staticbox, wx.HORIZONTAL)
        sizer_13 = wx.StaticBoxSizer(self.sizer_13_staticbox, wx.HORIZONTAL)
        sizer_9 = wx.StaticBoxSizer(self.sizer_9_staticbox, wx.VERTICAL)
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.HORIZONTAL)
        sizer_15 = wx.StaticBoxSizer(self.sizer_15_staticbox, wx.HORIZONTAL)
        sizer_15.Add(self.text_ctrl_3, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_15, 1, wx.EXPAND, 0)
        sizer_5.Add(self.combo_box_1, 0, 0, 0)
        sizer_5.Add(self.button_1, 0, 0, 0)
        sizer_5.Add(self.button_2, 0, 0, 0)
        sizer_5.Add(self.button_theme_export, 0, 0, 0)
        sizer_5.Add(self.button_theme_import, 0, 0, 0)
        sizer_4.Add(sizer_5, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_6.Add(self.label_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_6.Add(self.combo_box_2, 0, 0, 0)
        sizer_4.Add(sizer_6, 0, wx.EXPAND, 0)
        sizer_10.Add(self.label_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_10.Add(self.text_ctrl_2, 0, 0, 0)
        sizer_10.Add(self.button_3, 0, 0, 0)
        sizer_9.Add(sizer_10, 1, wx.EXPAND, 0)
        sizer_11.Add(self.label_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_11.Add(self.combo_box_3, 0, 0, 0)
        sizer_9.Add(sizer_11, 1, wx.EXPAND, 0)
        sizer_12.Add(self.label_5, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_12.Add(self.combo_box_4, 0, 0, 0)
        sizer_12.Add(self.button_4, 0, 0, 0)
        sizer_9.Add(sizer_12, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_9, 0, wx.EXPAND, 0)
        sizer_13.Add(self.button_5, 0, 0, 0)
        sizer_13.Add(self.button_6, 0, 0, 0)
        sizer_4.Add(sizer_13, 0, wx.EXPAND, 0)
        sizer_14.Add(self.label_6, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_14.Add(self.combo_box_5, 0, 0, 0)
        sizer_14.Add(self.button_7, 0, 0, 0)
        sizer_4.Add(sizer_14, 0, wx.EXPAND, 0)
        sizer_17.Add(self.label_7, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_17.Add(self.spin_ctrl_1, 0, 0, 0)
        sizer_16.Add(sizer_17, 1, wx.EXPAND, 0)
        sizer_18.Add(self.label_8, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_18.Add(self.spin_ctrl_2, 0, 0, 0)
        sizer_16.Add(sizer_18, 1, wx.EXPAND, 0)
        sizer_19.Add(self.label_9, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_19.Add(self.spin_ctrl_3, 0, 0, 0)
        sizer_16.Add(sizer_19, 1, wx.EXPAND, 0)
        sizer_20.Add(self.label_10, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_20.Add(self.spin_ctrl_4, 0, 0, 0)
        sizer_16.Add(sizer_20, 1, wx.EXPAND, 0)
        sizer_21.Add(self.label_11, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_21.Add(self.spin_ctrl_5, 0, 0, 0)
        sizer_16.Add(sizer_21, 1, wx.EXPAND, 0)
        sizer_22.Add(self.label_12, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_22.Add(self.spin_ctrl_6, 0, 0, 0)
        sizer_16.Add(sizer_22, 1, wx.EXPAND, 0)
        sizer_4.Add(sizer_16, 0, wx.EXPAND, 0)
        self.notebook_1_pane_1.SetSizer(sizer_4)
        sizer_2.Add(self.checkbox_1, 0, 0, 0)
        sizer_2.Add(self.checkbox_2, 0, 0, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_23.Add(self.label_13, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_23.Add(self.spin_ctrl_8, 0, 0, 0)
        sizer_8.Add(sizer_23, 1, wx.EXPAND, 0)
        sizer_24.Add(self.label_14, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_24.Add(self.spin_ctrl_9, 0, 0, 0)
        sizer_8.Add(sizer_24, 1, wx.EXPAND, 0)
        sizer_1.Add(sizer_8, 0, wx.EXPAND, 0)
        sizer_25.Add(self.checkbox_3, 0, 0, 0)
        sizer_25.Add(self.checkbox_4, 0, 0, 0)
        sizer_25.Add(self.checkbox_5, 0, 0, 0)
        sizer_29.Add(self.label_15, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_29.Add(self.spin_ctrl_10, 0, 0, 0)
        sizer_25.Add(sizer_29, 1, wx.EXPAND, 0)
        sizer_1.Add(sizer_25, 0, wx.EXPAND, 0)
        sizer_weball.Add(self.checkbox_webserver, 0, 0, 0)
        sizer_web2.Add(self.label_webport, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_web2.Add(self.spin_ctrl_webport, 0, 0, 0)
        sizer_weball.Add(sizer_web2, 0, wx.EXPAND, 0)
        sizer_web3.Add(self.label_webroot, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_web3.Add(self.text_ctrl_webroot, 0, 0, 0)
        sizer_web3.Add(self.button_webroot, 0, 0, 0)
        sizer_weball.Add(sizer_web3, 0, wx.EXPAND, 0)
        sizer_MDNS.Add(self.label_MDNS, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_MDNS.Add(self.combo_box_MDNS, 0, 0, 0)
        sizer_weball.Add(sizer_MDNS, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_weball, 0, wx.EXPAND, 0)

        self.notebook_1_pane_2.SetSizer(sizer_1)
        sizer_33.Add(self.label_16, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_33.Add(self.combo_box_6, 0, 0, 0)
        sizer_32.Add(sizer_33, 1, wx.EXPAND, 0)

        sizer_34.Add(self.label_17, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_34.Add(self.text_ctrl_1, 0, 0, 0)
        sizer_34.Add(self.button_12, 0, 0, 0)
        sizer_32.Add(sizer_34, 1, wx.EXPAND, 0)

        sizer_35.Add(self.label_18, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_35.Add(self.spin_ctrl_11, 0, 0, 0)
        sizer_32.Add(sizer_35, 1, wx.EXPAND, 0)
        sizer_31.Add(sizer_32, 0, wx.EXPAND, 0)
        sizer_36.Add(self.checkbox_6, 0, 0, 0)
        sizer_37.Add(self.label_19, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_37.Add(self.text_ctrl_4, 0, 0, 0)
        sizer_36.Add(sizer_37, 1, wx.EXPAND, 0)
        sizer_38.Add(self.label_20, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_38.Add(self.spin_ctrl_12, 0, 0, 0)
        sizer_36.Add(sizer_38, 1, wx.EXPAND, 0)
        sizer_39.Add(self.label_21, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_39.Add(self.text_ctrl_5, 0, 0, 0)
        sizer_36.Add(sizer_39, 1, wx.EXPAND, 0)
        sizer_40.Add(self.label_22, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_40.Add(self.text_ctrl_6, 0, 0, 0)
        sizer_36.Add(sizer_40, 1, wx.EXPAND, 0)
        sizer_31.Add(sizer_36, 0, wx.EXPAND, 0)
        self.notebook_1_pane_3.SetSizer(sizer_31)

        sizer_26.Add(self.combo_box_7, 0, 0, 0)
        sizer_26.Add(self.button_Key_Save, 0, 0, 0)
        sizer_26.Add(self.button_Key_Del, 0, 0, 0)
        sizer_26.Add(self.button_key_export, 0, 0, 0)
        sizer_26.Add(self.button_key_import, 0, 0, 0)
        sizer_7.Add(sizer_26, 0, wx.EXPAND, 0)
        sizer_27.Add(self.grid_1,1,wx.EXPAND,0)
        #sizer_7.Add(self.grid_1, 1, wx.EXPAND, 0)
        sizer_7.Add(sizer_27, 1, wx.EXPAND, 0)
        self.notebook_1_pane_4.SetSizer(sizer_7)

        #LTBNET
        sizer_ltbnet_all = wx.BoxSizer(wx.VERTICAL)
        sizer_ltbnet = wx.StaticBoxSizer(self.staticbox_ltbnet, wx.VERTICAL)
        sizer_ltbnet.Add(self.checkbox_ltbnet,0,wx.EXPAND,0)
        sizer_ltbnet.Add(self.checkbox_upnp,0,wx.EXPAND,0)
        sizer_ltbroot = wx.BoxSizer(wx.HORIZONTAL)
        sizer_ltbroot.Add(self.label_ltbroot, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_ltbroot.Add(self.text_ctrl_ltbroot, 0, 0, 0)
        sizer_ltbroot.Add(self.button_ltbroot, 0, 0, 0)
        sizer_ltbnet.Add(sizer_ltbroot,0,wx.EXPAND,0)
        sizer_ltbport = wx.BoxSizer(wx.HORIZONTAL)
        sizer_ltbport.Add(self.label_ltbport,0,wx.ALIGN_CENTER_VERTICAL,0)
        sizer_ltbport.Add(self.spin_ctrl_ltbport,0,0,0)
        sizer_ltbnet.Add(sizer_ltbport,0,wx.EXPAND,0)
##        sizer_upnp = wx.BoxSizer(wx.HORIZONTAL)
##        sizer_upnp.Add(self.checkbox_upnp,0,wx.ALIGN_CENTER_VERTICAL,0)
##        sizer_ltbnet.Add(sizer_upnp,0,wx.EXPAND,0)
        #sizer_32.Add(sizer_ltbroot, 1, wx.EXPAND, 0)
        #sizer_ltbnet_all.Add(sizer_ltbnet,0,wx.EXPAND,0)


        self.notebook_1_pane_ltbnet.SetSizer(sizer_ltbnet)

        self.notebook_1.AddPage(self.notebook_1_pane_1, u"显示设置")
        self.notebook_1.AddPage(self.notebook_1_pane_2, u"控制设置")
        self.notebook_1.AddPage(self.notebook_1_pane_3, u"下载设置")
        self.notebook_1.AddPage(self.notebook_1_pane_4, u"按键设置")
        self.notebook_1.AddPage(self.notebook_1_pane_ltbnet, u"LTBNET设置")
        sizer_3.Add(self.notebook_1, 1, wx.EXPAND, 0)
        sizer_30.Add((100, 10), 1, wx.EXPAND, 0)
        sizer_30.Add(self.button_10, 0, 0, 0)
        sizer_30.Add((20, 10), 1, wx.EXPAND, 0)
        sizer_30.Add(self.button_11, 0, 0, 0)
        sizer_30.Add((50, 10), 1, wx.EXPAND, 0)
        sizer_3.Add(sizer_30, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_3)
        self.Layout()
        # end wxGlade

    def OnChoseWebRoot(self,evt):
        global GlobalConfig
        fdlg=wx.DirDialog(self,u"请选择共享目录：",GlobalConfig['ShareRoot'])
        if fdlg.ShowModal()==wx.ID_OK:
            rdir=fdlg.GetPath()
            if os.path.isdir(rdir):
                self.text_ctrl_webroot.SetValue(rdir)
            else:
                dlg = wx.MessageDialog(None, rdir+u' 不是一个合法的目录',u"错误！",wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
        fdlg.Destroy()


    def OnCancell(self,event):
        self.Destroy()


    def OnOK(self,event):
        global ThemeList,GlobalConfig,KeyConfigList,KeyMenuList
        GlobalConfig['CurFont']=self.text_ctrl_3.GetFont()
        GlobalConfig['CurFColor']=self.text_ctrl_3.GetFColor()
        GlobalConfig['CurBColor']=self.text_ctrl_3.GetBackgroundColour()
        if self.combo_box_4.GetSelection()==0:
            if self.text_ctrl_3.bg_img_path<>None and self.text_ctrl_3.bg_img_path<>'':
                if os.path.dirname(AnyToUnicode(self.text_ctrl_3.bg_img_path))==cur_file_dir()+u'/background':
                    GlobalConfig['backgroundimg']=os.path.basename(self.text_ctrl_3.bg_img_path)
                else:
                    GlobalConfig['backgroundimg']=self.text_ctrl_3.bg_img_path

        else:
            GlobalConfig['backgroundimg']=None
        GlobalConfig['showmode']=self.text_ctrl_3.show_mode
        GlobalConfig['backgroundimglayout']=self.text_ctrl_3.bg_style
        GlobalConfig['underline']=self.text_ctrl_3.under_line
        GlobalConfig['underlinestyle']=self.text_ctrl_3.under_line_style
        GlobalConfig['underlinecolor']=self.text_ctrl_3.under_line_color
        GlobalConfig['pagemargin']=self.text_ctrl_3.pagemargin
        GlobalConfig['bookmargin']=self.text_ctrl_3.bookmargin
        GlobalConfig['vbookmargin']=self.text_ctrl_3.vbookmargin
        GlobalConfig['centralmargin']=self.text_ctrl_3.centralmargin
        GlobalConfig['linespace']=self.text_ctrl_3.linespace
        GlobalConfig['vlinespace']=self.text_ctrl_3.vlinespace

        GlobalConfig['LoadLastFile']=self.checkbox_1.GetValue()
        GlobalConfig['EnableESC']=self.checkbox_3.GetValue()
        GlobalConfig['VerCheckOnStartup']=self.checkbox_2.GetValue()
        if GlobalConfig['ShowAllFileInSidebar']==self.checkbox_5.GetValue():
            self.GetParent().UpdateSidebar=True
        GlobalConfig['ShowAllFileInSidebar']=not self.checkbox_5.GetValue()
        if MYOS == 'Windows':
            if GlobalConfig['EnableESC']:
                self.GetParent().RegisterHotKey(1,0,wx.WXK_ESCAPE)
                self.GetParent().Bind(wx.EVT_HOTKEY,self.GetParent().OnESC)
            else:
                self.GetParent().UnregisterHotKey(1)
                self.GetParent().Unbind(wx.EVT_HOTKEY)

        GlobalConfig['EnableSidebarPreview']=self.checkbox_4.GetValue()
        try:
            GlobalConfig['AutoScrollInterval']=float(self.spin_ctrl_8.GetValue())*1000
        except:
            GlobalConfig['AutoScrollInterval']=12000
        try:
            GlobalConfig['RemindInterval']=abs(int(self.spin_ctrl_9.GetValue()))
        except:
            GlobalConfig['RemindInterval']=60
        try:
            GlobalConfig['MaxOpenedFiles']=abs(int(self.spin_ctrl_10.GetValue()))
        except:
            GlobalConfig['MaxOpenedFiles']=5

        GlobalConfig['DAUDF']=self.combo_box_6.GetSelection()
        GlobalConfig['useproxy']=self.checkbox_6.GetValue()
        GlobalConfig['proxyserver']=self.text_ctrl_4.GetValue()
        try:
            GlobalConfig['proxyport']=int(self.spin_ctrl_12.GetValue())
        except:
            GlobalConfig['proxyport']=0
        GlobalConfig['proxyuser']=self.text_ctrl_5.GetValue()
        GlobalConfig['proxypass']=self.text_ctrl_6.GetValue()
        try:
            GlobalConfig['numberofthreads']=int(self.spin_ctrl_11.GetValue())
        except:
            GlobalConfig['numberofthreads']=1
        if GlobalConfig['numberofthreads']<=0 or GlobalConfig['numberofthreads']>50:
            GlobalConfig['numberofthreads']=1
        if not os.path.exists(self.text_ctrl_1.GetValue()):
            GlobalConfig['defaultsavedir']=''
        else:
            GlobalConfig['defaultsavedir']=self.text_ctrl_1.GetValue()
        if GlobalConfig['defaultsavedir']=='' and GlobalConfig['DAUDF']==2:
            dlg = wx.MessageDialog(self, u'请指定正确的缺省保存目录!',
                               u'出错了！',
                               wx.OK | wx.ICON_ERROR
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return

        #save key config
        for x in KeyConfigList:
            if x[0]=='last':
                KeyConfigList.remove(x)
                break
        kconfig=[]
        kconfig.append(('last'))
        rs=self.grid_1.GetNumberRows()
        if rs>0:
            i=0
            while i<rs:
                kconfig.append((self.grid_1.GetCellValue(i,0),self.grid_1.GetCellValue(i,1)))
                i+=1
            KeyConfigList.insert(0,kconfig)
        i=1
        tl=len(kconfig)
        #KeyMenuList={}
        while i<tl:
            KeyMenuList[kconfig[i][0]]=keygrid.str2menu(kconfig[i][1])
            i+=1
        self.GetParent().ResetMenu()
        #save web server related config
        GlobalConfig['ShareRoot']=self.text_ctrl_webroot.GetValue()
        GlobalConfig['ServerPort']=int(self.spin_ctrl_webport.GetValue())
        GlobalConfig['RunWebserverAtStartup']=self.checkbox_webserver.GetValue()
        m_int=self.combo_box_MDNS.GetValue()
        if m_int==u'自动检测':
            GlobalConfig['mDNS_interface']="AUTO"
        else:
            GlobalConfig['mDNS_interface']=m_int

        #save LTBNET config
        GlobalConfig['LTBNETPort'] = self.spin_ctrl_ltbport.GetValue()
        GlobalConfig['LTBNETRoot'] = self.text_ctrl_ltbroot.GetValue()
        GlobalConfig['RunUPNPAtStartup'] = self.checkbox_upnp.GetValue()
        GlobalConfig['EnableLTBNET'] = self.checkbox_ltbnet.GetValue()

        self.Destroy()


    def OnDelKey(self,evt):
        global KeyConfigList
        name=self.combo_box_7.GetValue()
        if name==u'当前设置':
            dlg = wx.MessageDialog(self, u'你不能删除这个方案！',u"错误",wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        for x in KeyConfigList:
            if x[0]==name:
                KeyConfigList.remove(x)
                break
        self.combo_box_7.Clear()
        for t in KeyConfigList:
            if t[0]=='last':self.combo_box_7.Append(u'当前设置')
            else:
                self.combo_box_7.Append(t[0])
        self.combo_box_7.SetSelection(0)



    def OnDelTheme(self,event):
        global ThemeList
        name=self.combo_box_1.GetValue()
        if self.combo_box_1.GetSelection()==0:
            dlg = wx.MessageDialog(self, u'你不能删除这个方案！',u"错误",wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        i=0
        n=len(ThemeList)
        while i<n:
            if ThemeList[i]['name']==name:
                ThemeList.__delitem__(i)
                break
            i+=1
        self.combo_box_1.Clear()
        self.combo_box_1.Append(u'当前设置')
        for t in ThemeList:
            self.combo_box_1.Append(t['name'])
        self.combo_box_1.SetSelection(0)
        self.OnThemeSelect(None)


    def OnSaveKey(self,evt):
        global KeyConfigList
        kconfig=[]
        kconfig.append((''))
        tlist=[]
        for k in KeyConfigList:
            if k[0]<>'last':
                tlist.append(k[0])
        while kconfig[0]=='':
            dlg = ComboDialog.ComboDialog(
                    self,tlist,u'输入方案名',u'输入或选择方案名' )
            if dlg.ShowModal() == wx.ID_OK:
                kconfig[0]=dlg.GetValue().strip()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
        for t in KeyConfigList:
            if t[0]==kconfig[0]:
                dlg = wx.MessageDialog(self, u'已经有叫这个名字的显示方案了，你确定要覆盖原有方案吗？',u"提示！",wx.YES_NO|wx.ICON_QUESTION)
                if dlg.ShowModal()==wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    KeyConfigList.remove(t)
        rs=self.grid_1.GetNumberRows()
        if rs>0:
            i=0
            while i<rs:
                kconfig.append((self.grid_1.GetCellValue(i,0),self.grid_1.GetCellValue(i,1)))
                i+=1
            if kconfig[0]=='last':
                KeyConfigList.insert(0,kconfig)
            else:
                KeyConfigList.append(kconfig)
            self.combo_box_7.Clear()
            for t in KeyConfigList:
                if t[0]=='last':self.combo_box_7.Append(u'当前设置')
                else:
                    self.combo_box_7.Append(t[0])
            self.combo_box_7.SetSelection(self.combo_box_7.GetCount()-1)


    def OnSaveTheme(self,event):
        global ThemeList
        l={}
        l['name']=''
        tlist=[]
        for t in ThemeList:
            tlist.append(t['name'])
        while l['name']=='':
            dlg = ComboDialog.ComboDialog(
                    self,tlist,u'输入主题名',u'输入或选择主题名' )
            if dlg.ShowModal() == wx.ID_OK:
                l['name']=dlg.GetValue().strip()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
        for t in ThemeList:
            if t['name']==l['name']:
                dlg = wx.MessageDialog(self, u'已经有叫这个名字的显示方案了，你确定要覆盖原有方案吗？',u"提示！",wx.YES_NO|wx.ICON_QUESTION)
                if dlg.ShowModal()==wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    ThemeList.remove(t)
        l['font']=self.text_ctrl_3.GetFont()
        l['fcolor']=self.text_ctrl_3.GetFColor()
        l['bcolor']=self.text_ctrl_3.GetBackgroundColour()
        l['config']=unicode(l['font'].GetPointSize())+u'|'+unicode(l['font'].GetFamily())+u'|'+unicode(l['font'].GetStyle())+u'|'+unicode(l['font'].GetWeight())+u'|'+unicode(l['font'].GetUnderlined())+u'|'+l['font'].GetFaceName()+u'|'+unicode(l['font'].GetDefaultEncoding())+u'|'+unicode(l['fcolor'])+u'|'+unicode(l['bcolor'])
        r=self.text_ctrl_3.GetConfig()
        l['backgroundimg']=r['backgroundimg']
        if r['backgroundimg']<>None and r['backgroundimg']<>'':
            if os.path.dirname(r['backgroundimg'])==cur_file_dir()+u'/background':
                l['backgroundimg']=os.path.basename(r['backgroundimg'])
            else:
                l['backgroundimg']=r['backgroundimg']
        l['showmode']=r['showmode']
        l['backgroundimglayout']=r['backgroundimglayout']
        l['underline']=r['underline']
        l['underlinestyle']=r['underlinestyle']
        l['underlinecolor']=r['underlinecolor']
        l['pagemargin']=r['pagemargin']
        l['bookmargin']=r['bookmargin']
        l['vbookmargin']=r['vbookmargin']
        l['centralmargin']=r['centralmargin']
        l['linespace']=r['linespace']
        l['vlinespace']=r['vlinespace']
        l['config']+=u'|'+unicode(l['backgroundimg'])
        l['config']+=u'|'+unicode(l['showmode'])
        l['config']+=u'|'+unicode(l['backgroundimglayout'])
        l['config']+=u'|'+unicode(l['underline'])
        l['config']+=u'|'+unicode(l['underlinestyle'])
        l['config']+=u'|'+unicode(l['underlinecolor'])
        l['config']+=u'|'+unicode(l['pagemargin'])
        l['config']+=u'|'+unicode(l['bookmargin'])
        l['config']+=u'|'+unicode(l['vbookmargin'])
        l['config']+=u'|'+unicode(l['centralmargin'])
        l['config']+=u'|'+unicode(l['linespace'])
        l['config']+=u'|'+unicode(l['vlinespace'])
        l['config']+=u'|'+unicode(l['name'])


        ThemeList.append(l)
        self.combo_box_1.Clear()
        self.combo_box_1.Append(u'当前设置')
        for t in ThemeList:
            self.combo_box_1.Append(t['name'])
        self.combo_box_1.SetSelection(self.combo_box_1.GetCount()-1)

    def OnShowmodeSelect(self,evt):
        id=evt.GetInt()
        modes=['paper','book','vbook']
        self.text_ctrl_3.SetShowMode(modes[id])
        self.text_ctrl_3.ReDraw()
    def OnBGlayoutSelect(self,evt):
        id=evt.GetInt()
        layouts=['tile','center']
        self.text_ctrl_3.SetImgBackground(self.text_ctrl_2.GetValue(),layouts[id])
        self.text_ctrl_3.ReDraw()

    def OnBGSet(self,evt):
        id=evt.GetInt()
        layouts=['tile','center']
        if id==0:
            self.text_ctrl_2.Enable()
            self.button_3.Enable()
            self.combo_box_3.Enable()
            if self.text_ctrl_2.GetValue()<>'':
                self.text_ctrl_3.SetImgBackground(self.text_ctrl_2.GetValue(),layouts[self.combo_box_3.GetSelection()])
                self.text_ctrl_3.ReDraw()

        else:
            self.text_ctrl_3.SetImgBackground('')
            self.text_ctrl_2.Clear()
            self.text_ctrl_2.Disable()
            self.button_3.Disable()
            self.combo_box_3.Disable()

    def OnSelectBGColor(self,evt):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            if self.combo_box_4.GetSelection()==1:
                self.text_ctrl_3.SetImgBackground('')
            self.text_ctrl_3.SetBackgroundColour(data.GetColour())

            self.text_ctrl_3.ReDraw()
        dlg.Destroy()

    def OnSelectULColor(self,evt):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            self.text_ctrl_3.SetUnderline(color=data.GetColour())

            self.text_ctrl_3.ReDraw()
        dlg.Destroy()

    def OnSelFont(self,event):
        global GlobalConfig
        data=wx.FontData()
        data.SetInitialFont(self.text_ctrl_3.GetFont())
        data.SetColour(self.text_ctrl_3.GetForegroundColour())
        data.EnableEffects(False)
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            ft=dlg.GetFontData().GetChosenFont()
            self.text_ctrl_3.SetFont(ft)
            self.text_ctrl_3.ReDraw()
        dlg.Destroy()

    def OnSelFColor(self,event):
        global GlobalConfig
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            self.text_ctrl_3.SetFColor(data.GetColour())
            self.text_ctrl_3.ReDraw()
        dlg.Destroy()




    def OnSelectBG(self,evt):
        wildcard = u"所有图片文件|*.gif;*.bmp;*.png;*.tif;*.tiff;*.jpg;*.jpeg;*.tif;*.tiff|"        \
            "JPG (*.jpg,*.jpeg)|*.jpg;*.jpeg|"     \
           "GIF (*.gif)|*.gif|" \
           "BMP (*.bmp)|*.bmp|"    \
           "PNG (*.png)|*.png|"        \
           "TIF (*.tif,*.tiff)|*.tif;*.tiff|"        \
           "All files (*.*)|*.*"

        defaultpath=os.path.dirname(self.text_ctrl_2.GetValue())
        if defaultpath=='':
            defaultpath=cur_file_dir()+u'/background'

        dlg = wx.FileDialog(
            self, message=u"选择背景图片",
            defaultDir=defaultpath,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.FD_FILE_MUST_EXIST
            )
        dlg.ShowModal()
        rpath=dlg.GetPath()
        if rpath<>None and rpath<>'':
            if os.path.dirname(AnyToUnicode(rpath))==cur_file_dir()+u'/background':
                rpath=os.path.basename(rpath)
            self.text_ctrl_2.SetValue(rpath)
            self.text_ctrl_3.SetImgBackground(rpath)
            self.text_ctrl_3.ReDraw()
        dlg.Destroy()

    def OnSelULS(self,evt):
        id=evt.GetInt()
        uls=[None,wx.SOLID,wx.DOT,wx.LONG_DASH,wx.DOT_DASH]
        if id==0:
            self.text_ctrl_3.SetUnderline(False)
        else:
            self.text_ctrl_3.SetUnderline(True,uls[id])
        self.text_ctrl_3.ReDraw()


    def AlignSetting(self):
        sms={'paper':0,'book':1,'vbook':2}
        self.combo_box_2.SetSelection(sms[self.text_ctrl_3.show_mode])
        if self.text_ctrl_3.bg_img==None:
            self.text_ctrl_2.SetValue('')
        else:
            self.text_ctrl_2.SetValue(self.text_ctrl_3.bg_img_path)
        layouts={'tile':0,'center':1}
        self.combo_box_3.SetSelection(layouts[self.text_ctrl_3.bg_style])
        if self.text_ctrl_3.bg_img_path<>None and self.text_ctrl_3.bg_img_path<>'':
            self.combo_box_4.SetSelection(0)
            self.text_ctrl_2.Enable()
            self.button_3.Enable()
            self.combo_box_3.Enable()

        else:
            self.combo_box_4.SetSelection(1)
        uls={wx.SOLID:1,wx.DOT:2,wx.LONG_DASH:3,wx.SHORT_DASH:3,wx.DOT_DASH:4}
        if self.text_ctrl_3.under_line==False: self.combo_box_5.SetSelection(0)
        else:
            self.combo_box_5.SetSelection(uls[self.text_ctrl_3.under_line_style])
        self.spin_ctrl_1.SetValue(self.text_ctrl_3.pagemargin)
        self.spin_ctrl_2.SetValue(self.text_ctrl_3.bookmargin)
        self.spin_ctrl_3.SetValue(self.text_ctrl_3.vbookmargin)
        self.spin_ctrl_4.SetValue(self.text_ctrl_3.centralmargin)
        self.spin_ctrl_5.SetValue(self.text_ctrl_3.linespace)
        self.spin_ctrl_6.SetValue(self.text_ctrl_3.vlinespace)



    def OnKeySelect(self,evt=None):
        global KeyConfigList
        if evt<>None:
            id=evt.GetInt()
        else:
            id=self.combo_box_7.GetSelection()
        self.grid_1.Load(KeyConfigList[id])

    def OnThemeSelect(self,evt=None):
        global ThemeList
        if evt<>None:
            id=evt.GetInt()
        else:
            id=self.combo_box_1.GetSelection()
        if id==0:
            self.text_ctrl_3.SetShowMode(GlobalConfig['showmode'])
            if GlobalConfig['backgroundimg']<>'' and GlobalConfig['backgroundimg']<>None:
                self.text_ctrl_3.SetImgBackground(GlobalConfig['backgroundimg'],GlobalConfig['backgroundimglayout'])
            else:
                self.text_ctrl_3.SetImgBackground(None)
                self.text_ctrl_3.SetBackgroundColour(GlobalConfig['CurBColor'])
            self.text_ctrl_3.SetFColor(GlobalConfig['CurFColor'])
            self.text_ctrl_3.SetFont(GlobalConfig['CurFont'])
            self.text_ctrl_3.SetUnderline(GlobalConfig['underline'],GlobalConfig['underlinestyle'],GlobalConfig['underlinecolor'])
            self.text_ctrl_3.SetSpace(GlobalConfig['pagemargin'],GlobalConfig['bookmargin'],GlobalConfig['vbookmargin'],GlobalConfig['centralmargin'],GlobalConfig['linespace'],GlobalConfig['vlinespace'])
            self.text_ctrl_3.SetValue(u"《老子》八十一章\n\n　1.道可道，非常道。名可名，非常名。无名天地之始。有名万物之母。故常无欲以观其妙。常有欲以观其徼。此两者同出而异名，同谓之玄。玄之又玄，众妙之门。\n\n　2.天下皆知美之为美，斯恶矣；皆知善之为善，斯不善已。故有无相生，难易相成，长短相形，高下相倾，音声相和，前後相随。是以圣人处无为之事，行不言之教。万物作焉而不辞。生而不有，为而不恃，功成而弗居。夫唯弗居，是以不去。\n\n　3.不尚贤， 使民不争。不贵难得之货，使民不为盗。不见可欲，使民心不乱。是以圣人之治，虚其心，实其腹，弱其志，强其骨；常使民无知、无欲，使夫智者不敢为也。为无为，则无不治。\n\n　4.道冲而用之，或不盈。渊兮似万物之宗。解其纷，和其光，同其尘，湛兮似或存。吾不知谁之子，象帝之先。\n\n　5.天地不仁，以万物为刍狗。圣人不仁，以百姓为刍狗。天地之间，其犹橐迭乎？虚而不屈，动而愈出。多言数穷，不如守中。")
        else:
            id-=1
            self.text_ctrl_3.SetShowMode(ThemeList[id]['showmode'])
            if ThemeList[id]['backgroundimg']<>'' and ThemeList[id]['backgroundimg']<>None:
                self.text_ctrl_3.SetImgBackground(ThemeList[id]['backgroundimg'],ThemeList[id]['backgroundimglayout'])
            else:
                self.text_ctrl_3.SetImgBackground(None)
                self.text_ctrl_3.SetBackgroundColour(ThemeList[id]['bcolor'])
            self.text_ctrl_3.SetFColor(ThemeList[id]['fcolor'])
            self.text_ctrl_3.SetFont(ThemeList[id]['font'])
            self.text_ctrl_3.SetUnderline(ThemeList[id]['underline'],ThemeList[id]['underlinestyle'],GlobalConfig['underlinecolor'])
            self.text_ctrl_3.SetSpace(ThemeList[id]['pagemargin'],ThemeList[id]['bookmargin'],GlobalConfig['vbookmargin'],GlobalConfig['centralmargin'],GlobalConfig['linespace'],GlobalConfig['vlinespace'])
            self.text_ctrl_3.ReDraw()
        self.AlignSetting()

    def SelectDir(self,event):
        dlg = wx.DirDialog(self, u"请选择目录：",defaultPath=GlobalConfig['LastDir'],
                          style=wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.text_ctrl_1.SetValue(dlg.GetPath())

        dlg.Destroy()


    def OnUpdateSpace(self,evt):
        lvalue=evt.GetInt()
        lid=evt.GetEventObject()
##        print lid
##        print self.spin_ctrl_2.GetId()
        if lid==self.spin_ctrl_1:self.text_ctrl_3.SetSpace(lvalue)
        if lid==self.spin_ctrl_2:
            self.text_ctrl_3.SetSpace(bookmargin=lvalue)

        if lid==self.spin_ctrl_3:self.text_ctrl_3.SetSpace(vbookmargin=lvalue)
        if lid==self.spin_ctrl_4:self.text_ctrl_3.SetSpace(centralmargin=lvalue)
        if lid==self.spin_ctrl_5:self.text_ctrl_3.SetSpace(linespace=lvalue)
        if lid==self.spin_ctrl_6:self.text_ctrl_3.SetSpace(vlinespace=lvalue)

        self.text_ctrl_3.ReDraw()

    def OnExportKey(self,evt):
        global KeyConfigList
        clist=[]
        for k in KeyConfigList:
            if k[0]=='last':
                clist.append(u'当前设置')
            else:
                clist.append(k[0])
        edlg=CheckDialog(self,u'导出按键配置方案',clist)
        edlg.ShowModal()
        rlist=edlg.GetChecks()
        if len(rlist)>0:
            wildcard = u"所有文件 (*.*)|*.*|"
            dlg = wx.FileDialog(
                self, message=u"导出为...", defaultDir=GlobalConfig['LastDir'],
                defaultFile="", wildcard=wildcard, style=wx.SAVE | wx.FD_OVERWRITE_PROMPT
                )

            if dlg.ShowModal() == wx.ID_OK:
                config=MyConfig()
                for r in rlist:
                    config.add_section(KeyConfigList[r][0])
                    i=1
                    kl=len(KeyConfigList[r])
                    cstr={}
                    while i<kl:
                        if KeyConfigList[r][i][0] not in cstr:
                            cstr[KeyConfigList[r][i][0]]=KeyConfigList[r][i][1]
                        else:
                            cstr[KeyConfigList[r][i][0]]+="&&"+KeyConfigList[r][i][1]
                        i+=1
                    for key,val in cstr.items():
                        config.set(KeyConfigList[r][0],unicode(key),val)
                try:
                    ConfigFile=codecs.open(dlg.GetPath(),encoding='utf-8',mode='w')
                    config.write(ConfigFile)
                    ConfigFile.close()
                except:
                    dlg = wx.MessageDialog(None, u'导出文件错误！',u"错误！",wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False



            dlg.Destroy()



    def OnImportKey(self,evt):
        global GlobalConfig,KeyConfigList
        wildcard = u"所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message=u"选择要导入的文件:",
            defaultDir=GlobalConfig['LastDir'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            flist=dlg.GetPath()
            config=MyConfig()
            try:
                ffp=codecs.open(flist,encoding='utf-8',mode='r')
                config.readfp(ffp)
            except:
                dlg = wx.MessageDialog(self, u'这不是一个合法的配置文件！',
                               u'出错了！',
                               wx.OK | wx.ICON_ERROR
                               )
                dlg.ShowModal()
                dlg.Destroy()
                return
            secs=config.sections()
##            if 'last' in secs:
##                secs[secs.index('last')]=u'导入的当前配置'
            kname_list=[]
            for k in KeyConfigList:
                kname_list.append(k[0])
            cdlg=CheckDialog(self,u'选择要导入的配置...',secs)
            cdlg.ShowModal()
            rlist=cdlg.GetChecks()
            if len(rlist)<=0:return
            tname=''
            for r in rlist:
                if secs[r]=='last':
                    tname=u'导入的当前配置'
                else:
                    tname=secs[r]
                if tname in kname_list:
                    dlg=wx.MessageDialog(self,secs[r]+u" 已有同名配置方案，是否继续？",u"导入",wx.YES_NO|wx.NO_DEFAULT)
                    if dlg.ShowModal()==wx.ID_NO:
                        dlg.Destroy()
                        continue
                    else:
                        KeyConfigList.__delitem__(kname_list.index(secs[r]))
                kconfig=[]
                kconfig.append(tname)
                for f,v in keygrid.LB2_func_list.items():
                    try:
                        cstr=config.get(secs[r],f)
                        cstr_list=cstr.split('&&')
                        for cs in cstr_list:
                            kconfig.append((f,cs))
                    except:

                        kconfig.append((f,v))
                KeyConfigList.append(kconfig)
            cur_str=self.combo_box_7.GetStringSelection()
            self.combo_box_7.Clear()
            for t in KeyConfigList:
                if t[0]=='last':self.combo_box_7.Append(u'当前设置')
                else:
                    self.combo_box_7.Append(t[0])
            self.combo_box_7.SetStringSelection(cur_str)






    def OnExportTheme(self,evt):
        global ThemeList,GlobalConfig
        clist=[]
        clist.append(u'当前设置')
        for t in ThemeList:
            clist.append(t['name'])
        edlg=CheckDialog(self,u'导出显示方案',clist)
        edlg.ShowModal()
        rlist=edlg.GetChecks()
        if len(rlist)>0:
            wildcard = u"litebook2显示配置文件 (*.lbt)|*.lbt|"
            dlg = wx.FileDialog(
                self, message=u"导出为...", defaultDir=GlobalConfig['LastDir'],
                defaultFile="", wildcard=wildcard, style=wx.SAVE | wx.FD_OVERWRITE_PROMPT
                )

            if dlg.ShowModal() == wx.ID_OK:
                config=MyConfig()
                config.add_section('Appearance')
                img_file_list=[]
                if 0 in rlist:
                    ft=GlobalConfig['CurFont']
                    save_str=unicode(ft.GetPointSize())+u'|'+unicode(ft.GetFamily())+u'|'+unicode(ft.GetStyle())+u'|'+unicode(ft.GetWeight())+u'|'+unicode(ft.GetUnderlined())+u'|'+ft.GetFaceName()+u'|'+unicode(ft.GetDefaultEncoding())+u'|'+unicode(GlobalConfig['CurFColor'])+u'|'+unicode(GlobalConfig['CurBColor'])
                    save_str+=u'|'+unicode(os.path.basename(GlobalConfig['backgroundimg']))
                    img_file_list.append[GlobalConfig['backgroundimg']]
                    save_str+=u'|'+unicode(GlobalConfig['showmode'])
                    save_str+=u'|'+unicode(GlobalConfig['backgroundimglayout'])
                    save_str+=u'|'+unicode(GlobalConfig['underline'])
                    save_str+=u'|'+unicode(GlobalConfig['underlinestyle'])
                    save_str+=u'|'+unicode(GlobalConfig['underlinecolor'])
                    save_str+=u'|'+unicode(GlobalConfig['pagemargin'])
                    save_str+=u'|'+unicode(GlobalConfig['bookmargin'])
                    save_str+=u'|'+unicode(GlobalConfig['vbookmargin'])
                    save_str+=u'|'+unicode(GlobalConfig['centralmargin'])
                    save_str+=u'|'+unicode(GlobalConfig['linespace'])
                    save_str+=u'|'+unicode(GlobalConfig['vlinespace'])

                    config.set('Appearance','last',save_str)
                    rlist.remove(0)
                for r in rlist:
                    f=ThemeList[r-1]['config'].split('|')
                    f[9]=os.path.basename(f[9])
                    save_str=''
                    for x in f:
                        save_str=save_str+x+'|'
                    save_str=save_str[:-1]
                    config.set('Appearance',ThemeList[r-1]['name'],save_str)
                    img_file_list.append(ThemeList[r-1]['backgroundimg'])
                try:
                    tmp_ini_name=cur_file_dir()+u'/litebook_tmp/'+'/_tmp_ltb_thm_export.ini'
                    ConfigFile=codecs.open(tmp_ini_name,encoding='utf-8',mode='w')
                    config.write(ConfigFile)
                    ConfigFile.close()
                except:
                    dlg = wx.MessageDialog(None, u'导出失败！',u"错误！",wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                save_name=dlg.GetPath()
                if save_name[-4:]<>'.lbt':
                    save_name+=u'.lbt'
                export_file=zipfile.ZipFile(save_name,'w')
                export_file.write(cur_file_dir()+u'/litebook_tmp/'+'/_tmp_ltb_thm_export.ini','LB_Display_theme.ini')
                for img in img_file_list:
                    if isinstance(img,unicode):
                        img=img.encode('gbk')
                    fpath=img
                    if fpath<>'' and fpath<>None:
                        if img.find('/')==-1:
                            fpath=cur_file_dir()+'/background/'+img
                        try:
                            export_file.write(fpath,os.path.basename(fpath))
                        except:
                            dlg = wx.MessageDialog(None, u'无法导出 '+fpath,u"错误！",wx.OK|wx.ICON_ERROR)
                            dlg.ShowModal()
                            dlg.Destroy()
                            try:
                                os.remove(save_name)
                            except:
                                return
                            return
                export_file.close()




    def OnImportTheme(self,evt):
        global GlobalConfig,ThemeList
        wildcard = u"litebook2显示配置文件 (*.lbt)|*.lbt|" \
        u"所有文件 (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message=u"选择要导入的文件:",
            defaultDir=GlobalConfig['LastDir'],
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            flist=dlg.GetPath()

            try:
                importf=zipfile.ZipFile(flist)
                fnamelist=importf.namelist()
                for fname in fnamelist:
                    if fname.find("..")<>-1 or fname.find("/")<>-1:
                        raise
                importf.extractall(cur_file_dir()+u'/litebook_tmp/')
                config=MyConfig()
                ffp=codecs.open(cur_file_dir()+u'/litebook_tmp/LB_Display_theme.ini',encoding='utf-8',mode='r')
                config.readfp(ffp)
                if not config.has_section('Appearance'):raise
            except:
                dlg = wx.MessageDialog(self, u'这不是一个合法的配置文件！',
                               u'出错了！',
                               wx.OK | wx.ICON_ERROR
                               )
                dlg.ShowModal()
                dlg.Destroy()
                return
            ft_list=config.items('Appearance')
            clist=[]
            for f in ft_list:
                clist.append(f[0])
            cdlg=CheckDialog(self,u'选择要导入的显示配置',clist)
            cdlg.ShowModal()
            cdlg.Destroy()
            rlist=cdlg.GetChecks()
            cur_nlist=[]
            for t in ThemeList:
                cur_nlist.append(t['name'])
            for r in rlist:
                if clist[r]=='last':
                    tname=u'导入的当前配置'
                else:
                    tname=clist[r]
                f=ft_list[r][1].split('|')
                if len(f)<>21: raise
                try:
                    l={}
                    l['font']=wx.Font(int(f[0]),int(f[1]),int(f[2]),int(f[3]),eval(f[4]),f[5],int(f[6]))
                    l['fcolor']=eval(f[7])
                    l['bcolor']=eval(f[8])
                    if f[9]<>'None' and f[9]<>'':
                        l['backgroundimg']=f[9]
                        if f[9] in fnamelist:
                            shutil.copyfile(cur_file_dir()+u'/litebook_tmp/'+"/"+f[9],cur_file_dir()+'/background/'+f[9])
                        else:
                            dlg = wx.MessageDialog(self, u'在导入的文件中未找到'+f[9],
                            u'出错了！',
                            wx.OK | wx.ICON_ERROR
                            )
                            dlg.ShowModal()
                            dlg.Destroy()
                            return
                    else:
                        l['backgroundimg']=None
                    l['showmode']=f[10]
                    l['backgroundimglayout']=f[11]
                    l['underline']=eval(f[12])
                    l['underlinestyle']=int(f[13])
                    l['underlinecolor']=f[14]
                    l['pagemargin']=int(f[15])
                    l['bookmargin']=int(f[16])
                    l['vbookmargin']=int(f[17])
                    l['centralmargin']=int(f[18])
                    l['linespace']=int(f[19])
                    l['vlinespace']=int(f[20])
                    l['name']=tname
                    l['config']=ft_list[r][1]
                except:
                    dlg = wx.MessageDialog(self, tname+u'不是一个合法的配置方案！',
                    u'出错了！',
                    wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    continue
                if tname in cur_nlist:
                    dlg=wx.MessageDialog(self,tname+u" 已有同名配置方案，是否继续？",u"导入",wx.YES_NO|wx.NO_DEFAULT)
                    if dlg.ShowModal()==wx.ID_NO:
                        dlg.Destroy()
                        continue
                    else:
                        ThemeList.__delitem__(cur_nlist.index(tname))
                ThemeList.append(l)
            cur_str=self.combo_box_1.GetStringSelection()
            self.combo_box_1.Clear()
            self.combo_box_1.Append(u'当前设置')
            for t in ThemeList:
                self.combo_box_1.Append(t['name'])
            self.combo_box_1.SetStringSelection(cur_str)



# end of class NewOptionDialog

class CheckDialog(wx.Dialog):
    def __init__(self, parent,title='',clist=[]):
        # begin wxGlade: CheckDialog.__init__
        wx.Dialog.__init__(self,parent,-1,style=wx.DEFAULT_DIALOG_STYLE)
        self.list_box_1 = wx.CheckListBox(self, -1, choices=[])
        self.button_1 = wx.Button(self, -1, u"确定")
        self.button_2 = wx.Button(self, -1, u"取消")
        self.selections=[]
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_2)
        self.list_box_1.Set(clist)
        self.SetTitle(title)
        self.__do_layout()


        # end wxGlade



    def __do_layout(self):
        # begin wxGlade: CheckDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.list_box_1, 0, wx.EXPAND, 0)
        sizer_2.Add(self.button_1, 0, 0, 0)
        sizer_2.Add(self.button_2, 0, 0, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def OnCancell(self,evt):
        self.Destroy()
    def OnOK(self,evt):
        n=self.list_box_1.GetCount()
        i=0
        while i<n:
            if self.list_box_1.IsChecked(i):
                self.selections.append(i)
            i+=1
        self.Close()

    def GetChecks(self):
        return self.selections

# end of class CheckDialog



class SliderDialog(wx.Dialog):
    def __init__(self, parent,val,inpos=(-1,-1)):
        global MYOS
        # begin wxGlade: MyDialog.__init__
        #kwds["style"] = wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self,parent, pos=inpos,style=wx.CLOSE_BOX|wx.THICK_FRAME)
        self.sizer_1_staticbox = wx.StaticBox(self, -1, u"当前进度")
        self.slider_1 = wx.Slider(self, -1, val, 0, 100, style=wx.SL_LABELS)
        self.fristtime=True
        if MYOS == 'Windows':
            self.slider_1.Bind(wx.EVT_KEY_UP,self.OnChar)
            self.slider_1.Bind(wx.EVT_KILL_FOCUS,self.Closeme)
        else:
            self.Bind(wx.EVT_KEY_UP,self.OnChar)
            self.Bind(wx.EVT_KILL_FOCUS,self.Closeme)
        self.slider_1.Bind(wx.EVT_SCROLL,self.OnScroll)
        self.Bind(wx.EVT_CLOSE,self.Closeme)

        self.slider_1.Bind(wx.EVT_KILL_FOCUS,self.Closeme)
        self.__set_properties()
        self.__do_layout()
        self.win=self.GetParent()
        if MYOS != 'Windows':
            self.SetFocus()
        # end wxGlade


    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        # end wxGlade
        self.SetTransparent(220)
        self.slider_1.SetLineSize(1)




    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.VERTICAL)
        sizer_1.Add(self.slider_1, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade
        self.SetSize((200,-1))

# end of class MyDialog
    def Closeme(self,evt=None):
        self.Destroy()
        self.win.slider=None
        return
##
##    def ToTop(self,evt):
##        self.win.text_ctrl_1.ScrollTop()
##
##    def ToBottom(self,evt):
##        self.win.text_ctrl_1.ScrollBottom()

    def OnScroll(self,evt):
        tval=self.slider_1.GetValue()
        if tval<>100:
            tpos=int(float(self.win.text_ctrl_1.ValueCharCount)*(float(tval)/100.0))
            self.win.text_ctrl_1.JumpTo(tpos)
        else:
            self.win.text_ctrl_1.ScrollBottom()



    def OnChar(self,evt):
        global KeyConfigList
        for k in KeyConfigList:
            if k[0]=='last':
                break
        keystr=keygrid.key2str(evt)
        for f in k:
            if f[0]==u'显示进度条':
                break
        key=evt.GetKeyCode()
        if self.fristtime and keystr==f[1]:
            self.fristtime=False
            return
        if key==wx.WXK_ESCAPE or keystr==f[1]:
            self.Closeme()
        else:
            evt.Skip()


    def fadein(self):
        t=100
        while t<250:
            self.SetTransparent(t)
            self.Show()
            time.sleep(0.01)
            t+=15



class cnsort:
    #use the code from henrysting@gmail.com, change a little bit
    def __init__(self):
        global MYOS
    # 建立拼音辞典
        self.dic_py = dict()
        try:
            f_py = open(cur_file_dir()+'/py.dat',"r")
            f_bh = open(cur_file_dir()+'/bh.dat',"r")
        except:
            return None
        content_py = f_py.read()
        lines_py = content_py.split('\n')
        n=len(lines_py)
        for i in range(0,n-1):
            word_py, mean_py = lines_py[i].split('\t', 1)#将line用\t进行分割，最多分一次变成两块，保存到word和mean中去
            self.dic_py[word_py]=mean_py
        f_py.close()

        #建立笔画辞典
        self.dic_bh = dict()
        content_bh = f_bh.read()
        lines_bh = content_bh.split('\n')
        n=len(lines_bh)
        for i in range(0,n-1):
            word_bh, mean_bh = lines_bh[i].split('\t', 1)#将line用\t进行分割，最多分一次变成两块，保存到word和mean中去
            self.dic_bh[word_bh]=mean_bh
        f_bh.close()


    # 辞典查找函数
    def searchdict(self,dic,uchar):
        if isinstance(uchar, str):
            uchar = unicode(uchar,'utf-8')
        if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
            value=dic.get(uchar.encode('utf-8'))
            if value == None:
                value = '*'
        else:
            value = uchar
        if isinstance(value,str):
            return value.decode('gbk')
        else:
            return value

    #比较单个字符
    def comp_char_PY(self,A,B):
        if A==B:
            return -1
        pyA=self.searchdict(self.dic_py,A)
        pyB=self.searchdict(self.dic_py,B)
        if pyA > pyB:
            return 1
        elif pyA < pyB:
            return 0
        else:
            bhA=eval(self.searchdict(self.dic_bh,A))
            bhB=eval(self.searchdict(self.dic_bh,B))
            if bhA > bhB:
                return 1
            elif bhA < bhB:
                return 0
            else:
                return False

    #比较字符串
    def comp_char(self,A,B):
        charA = A.decode("utf-8")
        charB = B.decode("utf-8")
        n=min(len(charA),len(charB))
        i=0
        while i < n:
            dd=self.comp_char_PY(charA[i],charB[i])
            if dd == -1:
                i=i+1
                if i==n:
                    dd=len(charA)>len(charB)
            else:
                break
        return dd

    # 排序函数
    def cnsort(self,nline):
        n = len(nline)
        lines="\n".join(nline)
        for i in range(1, n):  # 插入法
            tmp = nline[i]
            j = i
            while j > 0 and self.comp_char(nline[j-1],tmp):
                nline[j] = nline[j-1]
                j -= 1
            nline[j] = tmp
        return nline


##    # 将一个字符串转换成一个含每个字拼音的list，字符串中的连续的ASCII会按原样放在一个值内
##    def strToPYL(istr):
##        global dic_py
##        if isinstance(istr,str):
##            istr=istr.decode('gbk')
##            istr=istr.encode('utf-8')
##            istr=istr.decode('utf-8')
##        else:
##            if isinstance(istr,unicode):
##                istr=istr.encode('utf-8')
##                istr=istr.decode('utf-8')
##            else:
##                return None
##        lastasic=False
##        py_list=[]
##        for ichr in istr:
##           if ord(ichr)<=255:
##               if lastasic:
##                   py_list[len(py_list)-1]+=ichr
##               else:
##                   py_list.append(ichr)
##               lastasic=True
##           else:
##               py_list.append(searchdict(dic_py,ichr)[:-1])
##               lastasic=False
##        return py_list

    # 将一个字符串转换成一个含每个字拼音的list，字符串中的连续的ASCII会按原样放在一个值内
    def strToPYS(self,istr):
        if isinstance(istr,str):
            istr=istr.decode('gbk')
            istr=istr.encode('utf-8')
            istr=istr.decode('utf-8')
        else:
            if isinstance(istr,unicode):
                istr=istr.encode('utf-8')
                istr=istr.decode('utf-8')
            else:
                return None
        rstr=''
        for ichr in istr:
           if ord(ichr)<=255:rstr+=ichr
           else:
               rstr+=self.searchdict(self.dic_py,ichr)[:-1]
        return rstr

class Convert_EPUB_Dialog(wx.Dialog):
    def __init__(self, parent,outfile,title,author):
        # begin wxGlade: Search_Web_Dialog.__init__
        wx.Dialog.__init__(self, parent=parent)
        self.outfile=outfile
        self.title=title
        self.author=author
        self.sizer_3_staticbox = wx.StaticBox(self, -1, u"输出")
        self.sizer_1_staticbox = wx.StaticBox(self, -1, u"转换为EPUB文件")
        self.sizer_2_staticbox = wx.StaticBox(self, -1, "")
        self.radio_box_1 = wx.RadioBox(self, -1, u"章节划分方式：", choices=[u"自动", u"按照字数"], majorDimension=2, style=wx.RA_SPECIFY_COLS)
        self.label_zishu = wx.StaticText(self, -1, u"字数：")
        self.text_ctrl_zishu = wx.TextCtrl(self, -1, "")
        self.label_13 = wx.StaticText(self, -1, u"书名：")
        self.text_ctrl_2 = wx.TextCtrl(self, -1, "")
        self.label_author = wx.StaticText(self, -1, u"作者：")
        self.text_ctrl_author = wx.TextCtrl(self, -1, "")
        self.label_author_copy = wx.StaticText(self, -1, u"输出文件：")
        self.text_ctrl_3 = wx.TextCtrl(self, -1, "")
        self.button_1 = wx.Button(self, -1, u"另存为")
        self.button_3 = wx.Button(self, -1, u" 确定 ")
        self.button_4 = wx.Button(self, -1, u" 取消 ")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBOX, self.OnChose, self.radio_box_1)
        self.Bind(wx.EVT_BUTTON, self.OnSaveas, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.button_3)
        self.Bind(wx.EVT_BUTTON, self.OnCancell, self.button_4)
        self.Bind(wx.EVT_TEXT,self.onChangeName,self.text_ctrl_2)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: Search_Web_Dialog.__set_properties
        self.SetTitle(u"文件转换")
        self.radio_box_1.SetSelection(0)
        self.text_ctrl_zishu.SetValue('10000')
        self.text_ctrl_zishu.Enable(False)
        self.text_ctrl_3.SetMinSize((200, -1))
        # end wxGlade
        self.text_ctrl_author.SetValue(self.author)
        self.text_ctrl_2.SetValue(self.title)
        self.text_ctrl_3.SetValue(os.path.abspath(GlobalConfig['ShareRoot']+os.sep+self.outfile+u".epub"))


    def __do_layout(self):
        # begin wxGlade: Search_Web_Dialog.__do_layout
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.VERTICAL)
        sizer_author = wx.BoxSizer(wx.HORIZONTAL)
        sizer_23 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        sizer_zishu = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.radio_box_1, 0, 0, 0)
        sizer_zishu.Add(self.label_zishu, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_zishu.Add(self.text_ctrl_zishu, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_2.Add(sizer_zishu, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_23.Add(self.label_13, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_23.Add(self.text_ctrl_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(sizer_23, 0, wx.EXPAND, 0)
        sizer_author.Add(self.label_author, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_author.Add(self.text_ctrl_author, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(sizer_author, 0, wx.EXPAND, 0)
        sizer_3.Add(self.label_author_copy, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.text_ctrl_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.button_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_4.Add(self.button_3, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_4.Add(self.button_4, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(sizer_4, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def onChangeName(self,evt):
        newtit=self.text_ctrl_2.GetValue().strip()
        self.text_ctrl_3.SetValue(os.path.abspath(GlobalConfig['ShareRoot']+os.sep+newtit+u".epub"))

    def OnChose(self, event): # wxGlade: Search_Web_Dialog.<event_handler>
        if event.GetInt()==1:
            if event.IsChecked():
                self.text_ctrl_zishu.Enable()
        else:
            self.text_ctrl_zishu.Disable()
            event.Skip()

    def OnSaveas(self, event): # wxGlade: Search_Web_Dialog.<event_handler>
        wildcard = u"EPUB 电子书 (*.epub)|*.epub|"        \
                   "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message=u"另存为", defaultDir=GlobalConfig['ShareRoot'],
            defaultFile=self.title, wildcard=wildcard, style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.text_ctrl_3.SetValue(path)


    def OnOK(self, event): # wxGlade: Search_Web_Dialog.<event_handler>
        good=True
        self.divide_method=self.radio_box_1.GetSelection()
        if self.divide_method==1:
            try:
                self.zishu=int(self.text_ctrl_zishu.GetValue())
            except:
                good=False
            if good:
                if self.zishu<10000:good=False
            if not good:
                dlg = wx.MessageDialog(self, u'字数必须大于等于10000!',
                   u'出错了！',
                   wx.OK | wx.ICON_ERROR
                   )
                dlg.ShowModal()
                dlg.Destroy()
                return
        elif self.divide_method==0: self.zishu=10000
        outfile=self.text_ctrl_3.GetValue()
        if os.path.isdir(os.path.dirname(outfile)) and outfile[-5:].lower()=='.epub' and os.access(os.path.dirname(outfile),os.W_OK|os.R_OK):
            if os.path.exists(outfile):
                dlg = wx.MessageDialog(self, u'已经有叫这个名字的文件，你确定要覆盖原有文件吗？',u"提示！",wx.YES_NO|wx.ICON_QUESTION)
                if dlg.ShowModal()==wx.ID_NO:
                    dlg.Destroy()
                    return
            if outfile[-5:].lower()=='.epub':
                outfile=outfile[:-5]
            self.outfile=outfile

        else:
            dlg = wx.MessageDialog(self, u'输出的文件名或路径非法！',
                   u'出错了！',
                   wx.OK | wx.ICON_ERROR
                   )
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.title=self.text_ctrl_2.GetValue()
        self.author=self.text_ctrl_author.GetValue()
        self.id='OK'
        self.Close()


    def OnCancell(self, event):
        self.id=''
        self.Destroy()


class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.Menu103(None)
        for fname in filenames:
            sufix=fname.lower()[-4:]
            if sufix=='.rar' or sufix=='.zip':
                dlg=ZipFileDialog(self.window,fname)
                dlg.ShowModal()
                if dlg.selected_files<>[]:
                    self.window.LoadFile(dlg.selected_files,'zip',fname,openmethod='append')
                    dlg.Destroy()
                else:
                    dlg.Destroy()
            else:
                self.window.LoadFile(filenames,openmethod='append')


class LBHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):


    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """
    __version__ = "0.1"
    __all__ = ["LBHTTPRequestHandler"]
    server_version = "SimpleHTTP/" +__version__
    prefixpath=None


    def log_request(self,code=1,size=0):
        pass

    def log_error(self,*args, **kwds):
        pass

    def setup(self):
        global GlobalConfig
        BaseHTTPServer.BaseHTTPRequestHandler.setup(self)
        self.prefixpath=GlobalConfig['ShareRoot']


    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404,"File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        client_addr = self.client_address[0]
        if myup.checkLocalIP(client_addr)==False:
            return
        try:
            browser=unicode(self.headers['user-agent'])
        except:
            browser=u'unknown'
        f = StringIO()
        if browser.find(u'Stanza')<>-1:
            #if the browser is Stanza
            flist=glob.glob(self.prefixpath+os.sep+"*.epub")
##        fp=open('test.xml','r')
##        buf=fp.read()
            xml_header=u"""<?xml version='1.0' encoding='utf-8'?>
    <feed xmlns:dc="http://purl.org/dc/terms/" xmlns:opds="http://opds-spec.org/2010/catalog" xmlns="http://www.w3.org/2005/Atom">
      <title>LiteBook书库</title>
      <author>
        <name>LiteBook.Author</name>
        <uri>http://code.google.com/p/litebook-project/</uri>
      </author>
      """
            xml_header=xml_header.encode('utf-8')
            f.write(xml_header)
            for fname in flist:
    ##            if not isinstance(fname,unicode):
    ##                fname=fname.decode('gbk')
                f.write("  <entry>\n")
                if not isinstance(fname,unicode): fname=fname.decode('gbk')
                fname=fname.encode('utf-8')
                bname=os.path.basename(fname)
                f.write("<title>"+bname[:-4]+'</title>\n')
                f.write('<author>\n<name>unknown</name></author>\n')
                cont=u'<content type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">标签：General Fiction<br/></div></content>'
                cont=cont.encode('utf-8')
                f.write(cont+'\n')
                burl="<link href='/"+bname+"' type='application/epub+zip'/>\n"
                burl=urllib.quote('/'+bname)
                f.write("<link href='"+burl+"' type='application/epub+zip'/>\n")
                f.write("  </entry>\n")
            f.write('</feed>')
            length = f.tell()
            f.seek(0)
            self.send_response(200)
            self.send_header("Content-type", "application/atom+xml")
            self.send_header("Content-Length", str(length))
            self.end_headers()
        else:
            msg=u"""<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <title>LItebook共享书库</title>
</head>
<body>
<h2>LiteBook 共享图书列表：</h2>
<ul>"""
            msg=msg.encode('utf-8')
            f.write(msg)
            flist=glob.glob(self.prefixpath+os.sep+"*.*")
            for fname in flist:
                if not isinstance(fname,unicode): fname=fname.decode('gbk')
                fname=fname.encode('utf-8')
                bname=os.path.basename(fname)
                burl=urllib.quote('/'+bname)
                f.write("<li><a href='"+burl+"'>"+bname+"</a></li>\n")
            d=datetime(2000,1,1)
            ds=unicode(d.now())
            end=u"</ul>注：本列表由litebook自动生成于"+ds+"</body></html>"
            end=end.encode('utf-8')
            f.write(end)
            length=f.tell()
            f.seek(0)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(length))
            self.end_headers()
        return f






    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        - add prefix_path support; added by Hu Jun 2011-03-13
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        path=path.decode('utf-8')
        words = path.split('/')
        words = filter(None, words)
        path=self.prefixpath
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        if not 'Range' in self.headers:
            shutil.copyfileobj(source, outputfile)
        else:#this is to support Range Get
            (startpos,endpos)=self.headers['Range'][6:].split('-')
            if startpos=='':startpos=0
            else:
                startpos=int(startpos)
            if endpos=='':
                endpos=os.fstat(source.fileno()).st_size
            else:
                endpos=int(endpos)
            source.seek(startpos)
            ins=source.read(endpos-startpos)
            outputfile.write(ins)
            source.close()
            outputfile.close()

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

##    if not mimetypes.inited:
##        mimetypes.init() # try to read system mime.types
##    extensions_map = mimetypes.types_map.copy()
    extensions_map={}
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        '.epub': 'application/epub+zip'
        })

class ThreadedLBServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class ThreadAddUPNPMapping(threading.Thread):
    def __init__(self,win):
        threading.Thread.__init__(self)
        self.win=win

    def run(self):
        global GlobalConfig
        #add UPNP mapping
        ml=[
        {'port':GlobalConfig['ServerPort'],'proto':'TCP','desc':"LITEBOOK"},
        {'port':GlobalConfig['LTBNETPort'],'proto':'UDP','desc':"LITEBOOK"},
        ]
        r=False
        try:
            r=myup.changePortMapping(ml)
        except:
            pass
        if r==False:
            evt=AlertMsgEvt(txt=u'UPNP端口映射设置失败！请手动设置宽带路由器并添加相应的端口映射。')
        else:
            evt=AlertMsgEvt(txt=u'UPNP端口映射设置完成')
        wx.PostEvent(self.win, evt)
        evt = UpdateStatusBarEvent(FieldNum = 3, Value =u'')
        wx.PostEvent(self.win, evt)
        return

class ThreadChkPort(threading.Thread):
    def __init__(self,win,alertOnOpen=True):
        threading.Thread.__init__(self)
        self.win=win
        self.aOO=alertOnOpen

    def run(self):
        global GlobalConfig
        for x in range(30):
            time.sleep(1)
            try:
                pstatus=GlobalConfig['kadp_ctrl'].PortStatus(False)
            except:
                continue
            if pstatus==-1:
                evt=AlertMsgEvt(txt=u'LTBNET端口未打开！请设置宽带路由器并添加相应的端口映射。')
                wx.PostEvent(self.win, evt)
                evt = UpdateStatusBarEvent(FieldNum = 3, Value =u'')
                wx.PostEvent(self.win, evt)
                return
            elif pstatus==1:
                if self.aOO==True:
                    evt=AlertMsgEvt(txt=u'LTBNET端口已打开！')
                    wx.PostEvent(self.win, evt)
                evt = UpdateStatusBarEvent(FieldNum = 3, Value =u'')
                wx.PostEvent(self.win, evt)
                return
        evt=AlertMsgEvt(txt=u'LTBNET端口未打开！请设置宽带路由器并添加相应的端口映射。')
        wx.PostEvent(self.win, evt)
        evt = UpdateStatusBarEvent(FieldNum = 3, Value =u'')
        wx.PostEvent(self.win, evt)
        return


if __name__ == "__main__":
    if MYOS == 'Windows':
        cache_dir=os.environ['USERPROFILE'].decode('gbk')+u"\\litebook\\cache"
    else:
        cache_dir=unicode(os.environ['HOME'],'utf-8')+u"/litebook/cache"
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    try:
        if MYOS == 'Windows':
            SqlCon = sqlite3.connect(os.environ['APPDATA'].decode('gbk')+u"\\litebook.bookdb")
        else:
            SqlCon = sqlite3.connect(unicode(os.environ['HOME'],'utf-8')+u"/.litebook.bookdb")
    except:
        print unicode(os.environ['HOME'],'utf-8')+u"/litebook.bookdb is not a sqlite file!"
    SqlCur=SqlCon.cursor()
    found=True
    sqlstr="select name from sqlite_master where type='table' and name='book_history'"
    try:
        SqlCur.execute(sqlstr)
    except:
        found=False
    if SqlCur.fetchall() == []:
        found=False
    if found==False:
        sqlstr = """CREATE TABLE `book_history` (
          `name` varchar(512) NOT NULL,
          `type` varchar(20) NOT NULL,
          `zfile` varchar(512) default NULL,
          `date` float unsigned NOT NULL
        ) ;
        """
        SqlCur.execute(sqlstr)

    sqlstr="select name from sqlite_master where type='table' and name='subscr'"
    found=True
    try:
        SqlCur.execute(sqlstr)
    except:
        found=False
    if SqlCur.fetchall() == []:
        found=False
    if found == False:
        sqlstr = """
        CREATE TABLE `subscr` (
          `bookname` varchar(512) NOT NULL,
          `index_url` varchar(512) PRIMARY KEY,
          `last_chapter_name` varchar(512) default NULL,
          `last_update` varchar(128) NOT NULL,
          `chapter_count` int unsigned NOT NULL,
          `save_path` varchar(512) NOT NULL,
          `plugin_name` varchar(128) NOT NULL
        ) ;
        """
        SqlCon.execute(sqlstr)


    app = wx.PySimpleApp(False)
    #app = wx.PySimpleApp(0)
    fname=None
    if MYOS != 'Windows':
        if len(sys.argv)>1:
            if sys.argv[1]=='-reset':
                print u"此操作将把当前配置恢复为缺省配置，可以解决某些启动问题，但是会覆盖当前设置，是否继续？(Y/n)"
                inc=raw_input()
                if inc=='Y':
                    try:
                        os.remove(unicode(os.environ['HOME'],'utf-8')+u"/.litebook_key.ini")
                        os.remove(unicode(os.environ['HOME'],'utf-8')+u"/.litebook.ini")
                    except:
                        pass
            else:
                fname=sys.argv[1]
                fname=os.path.abspath(fname)

                if not os.path.exists(fname):
                    print fname,u'不存在!'
                    sys.exit()
    else:
        if len(sys.argv)>1:
            if sys.argv[1].lower()=='-reset':
                dlg=wx.MessageDialog(None,u"此操作将把当前配置恢复为缺省配置，可以解决某些启动问题，但是会覆盖当前设置，是否继续？",u"恢复到LiteBook的缺省设置",wx.YES_NO|wx.NO_DEFAULT)
                if dlg.ShowModal()==wx.ID_YES:
                    try:
                        os.remove(os.environ['APPDATA'].decode('gbk')+u"\\litebook.ini")
                        os.remove(os.environ['APPDATA'].decode('gbk')+u"\\litebook_key.ini")
                    except:
                        pass
            else:
                fname=sys.argv[1]
                fname=os.path.abspath(fname)
                if not os.path.exists(fname):
                    dlg = wx.MessageDialog(None,fname+u' 不存在',u"错误！",wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    sys.exit()
    readConfigFile()
    #create share_root if it doesn't exist
    if not os.path.isdir(GlobalConfig['ShareRoot']):
        os.makedirs(GlobalConfig['ShareRoot'])
    readKeyConfig()
    readPlugin()
    if GlobalConfig['InstallDefaultConfig']:InstallDefaultConfig()
    wx.InitAllImageHandlers()
    t0=time.time()
    frame_1 = MyFrame(None,fname)
    app.SetTopWindow(frame_1)
    #print "windows is created ",time.time()-t0
    frame_1.Show()
    app.MainLoop()
