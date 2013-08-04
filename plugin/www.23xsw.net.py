﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

#-------------------------------------------------------------------------------
# Name:        litebook plugin for www.ranwen.net
# Purpose:
#
# Author:
#
# Created:     02/01/2013
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import platform
import sys
import re, htmlentitydefs
MYOS = platform.system()
osarch=platform.architecture()
if osarch[1]=='ELF' and MYOS == 'Linux':
    sys.path.append('..')
    if osarch[0]=='64bit':
        from lxml_linux_64 import html
    elif osarch[0]=='32bit':
#        from lxml_linux import etree
        from lxml_linux import html

elif MYOS == 'Darwin':
    from lxml_osx import html
else:
    from lxml import html
#import lxml.html
import urlparse
import urllib2
import time
import re
import wx
import thread
import threading
import htmlentitydefs
import urllib
import Queue
from datetime import datetime

Description=u"""支持的网站: http://www.23xsw.net/
插件版本：1.0
发布时间: TBD
简介：
    - 支持多线程下载
    - 关键字大于2
    - 支持HTTP代理
    - 支持流看
作者：litebook.author@gmail.com
"""

SearchURL='http://www.23xsw.net/modules/article/search.php'

def myopen(url,post_data=None,useproxy=False,proxyserver='',proxyport=0,proxyuser='',proxypass=''):
    interval=10 #number of seconds to wait after fail download attampt
    max_retries=3 #max number of retry
    retry=0
    finished=False
    if useproxy:
        proxy_info = {
            'user' : proxyuser,
            'pass' : proxypass,
            'host' : proxyserver,
            'port' : proxyport
            }
        proxy_support = urllib2.ProxyHandler({"http" : \
        "http://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy_info})
        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
    if post_data<>None:
        myrequest=urllib2.Request(url,post_data)
    else:
        myrequest=urllib2.Request(url)
        #spoof user-agent as IE8 on win7
    myrequest.add_header("User-Agent","Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)")

    while retry<max_retries and finished==False:
        try:
            fp=urllib2.urlopen(myrequest)
            finished=True
        except:
            retry+=1
            time.sleep(interval)
    if finished==False:
        return None
    else:
        try:
            return fp.read()
        except:
            return None


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

def unescape(text):
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def htm2txt(inf):
    """ extract the text context"""
    doc=html.document_fromstring(inf)
    content=doc.xpath('//*[@id="contents"]')
    htmls=html.tostring(content[0],False)
    htmls=htmls.replace('<br>','\n')
    htmls=htmls.replace('<p>','\n')
    htmls=unescape(htmls)
    p=re.compile('\n{2,}') #replace more than 2 newlines in a row into one newline
    htmls=p.sub('\n',htmls)
    newdoc=html.document_fromstring(htmls)
    return newdoc.text_content()


class NewDThread:
    def __init__(self,Q,useproxy=False,proxyserver='',proxyport=0,proxyuser='',proxypass='',tr=[],cv=None):
        self.Q=Q
        self.proxyserver=proxyserver
        self.proxyport=proxyport
        self.proxyuser=proxyuser
        self.proxypass=proxypass
        self.useproxy=useproxy
        self.tr=tr
        self.cv=cv
        thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            try:
                task=self.Q.get(False)
            except:
                return
            self.cv.acquire()
            self.tr[task['index']]=htm2txt(myopen(task['url'],post_data=None,
                        useproxy=self.useproxy,
                        proxyserver=self.proxyserver,proxyport=self.proxyport,
                        proxyuser=self.proxyuser,proxypass=self.proxypass))
            self.cv.release()
            self.Q.task_done()






def get_search_result(url,key,useproxy=False,proxyserver='',proxyport=0,proxyuser='',proxypass=''):
    #get search result web from url by using key as the keyword
    #this only apply for POST
    #return None when fetch fails
    if useproxy:
        proxy_info = {
            'user' : proxyuser,
            'pass' : proxypass,
            'host' : proxyserver,
            'port' : proxyport # or 8080 or whatever
            }
        proxy_support = urllib2.ProxyHandler({"http" : \
        "http://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy_info})
        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        # install it
        urllib2.install_opener(opener)
    if isinstance(key,unicode):
        key=key.encode("GBK")
    post_data=urllib.urlencode({u"searchkey":key,u'searchtype':'articlename'})
    myrequest=urllib2.Request(url,post_data)
    #spoof user-agent as IE8 on win7
    myrequest.add_header("User-Agent","Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)")
    try:
        rr=urllib2.urlopen(myrequest)
        return rr.read()
    except Exception as inst:
        return None

def GetSearchResults(key,useproxy=False,proxyserver='',proxyport=0,proxyuser='',proxypass=''):
    global SearchURL
    if key.strip()=='':return []
    rlist=[]
    page=get_search_result(SearchURL,key,useproxy,proxyserver,proxyport,proxyuser,proxypass)
    if page==None:
        return None
    doc=html.document_fromstring(page)
    rtable=doc.xpath('//*[@id="content"]/table')
    #get the main table, you could use chrome inspect element to get the xpath. note: for tables, end with /table, dont end with table/tbody because chrome sometime will insert tbody
    #you could use chorme extension xpath helper to get correct xpath because sometime chrome inspect element return wrong result
    if len(rtable)!=0:
        row_list=rtable[0].findall('tr') #get the row list
        row_list=row_list[1:] #remove first row of caption
        for row in row_list:
            r={}
            col_list = row.getchildren() #get col list in each row
            r['bookname']=col_list[0].xpath('a')[0].text
            r['book_index_url']=col_list[1].xpath('a')[0].get('href')
            r['book_index_url']=urlparse.urljoin(SearchURL,r['book_index_url'])
            r['authorname']=col_list[2].text
            r['booksize']=col_list[3].text
            r['lastupdatetime']=col_list[4].text
            r['bookstatus']=col_list[5].text
            rlist.append(r)
        return rlist


    else:#means the search result is a direct hit, the result page is the book portal page
        r={}
        try:
            r['bookname']=doc.xpath('//*[@id="content"]/dd[1]/h1')[0].text
            r['bookstatus']=doc.xpath('//*[@id="at"]/tr[1]/td[3]')[0].text #remove tbody here
            r['lastupdatetime']=doc.xpath('//*[@id="at"]/tr[2]/td[3]')[0].text
            r['authorname']=doc.xpath('//*[@id="at"]/tr[1]/td[2]')[0].text
            r['book_index_url']=doc.xpath("//*[@id='content']/dd[2]/div[@class='fl'][2]/p[@class='btnlinks']/a[@class='read']")[0].get('href')
            r['book_index_url']=urlparse.urljoin(SearchURL,r['book_index_url'])
            r['booksize']=''
        except:
            return []
        return [r]
    return []

def GetBook(url,bkname='',win=None,evt=None,useproxy=False,proxyserver='',
            proxyport=0,proxyuser='',proxypass='',concurrent=10,
            mode='new',last_chapter_count=0,dmode='down',sevt=None,control=[]):
    """
    mode is either 'new' or 'update', default is 'new', update is used to
    retrie the updated part
    dmode is either 'down' or 'stream'
    sevt is the event for stream
    if control != [] then download will stop (because list is mutable type, boolean is not)
    """
    bb=''
    cv=threading.Lock()
    if useproxy:
        proxy_info = {
            'user' : proxyuser,
            'pass' : proxypass,
            'host' : proxyserver,
            'port' : proxyport
            }
        proxy_support = urllib2.ProxyHandler({"http" : \
        "http://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy_info})
        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
    try:
        up=urllib2.urlopen(url)
    except:
        return None,{'index_url':url}
    fs=up.read()

    up.close()
    doc=html.document_fromstring(fs)
    r=doc.xpath('//*[@id="at"]') #get the main table, you could use chrome inspect element to get the xpath
    row_list=r[0].findall('tr') #get the row list
    clist=[]
    for r in row_list:
        for col in r.getchildren(): #get col list in each row
            for a in col.xpath('a'): #use relative xpath to locate <a>
                chapt_name=a.text,
                chapt_url=urlparse.urljoin(url,a.get('href'))
                clist.append({'cname':chapt_name,'curl':chapt_url})
    ccount=len(clist)
    if mode=='update':
        if ccount<=last_chapter_count:

            return '',{'index_url':url}
        else:
            clist=clist[last_chapter_count:]
            ccount=len(clist)
    i=0
    Q=Queue.Queue()
    tr=[]
    for c in clist:
        Q.put({'url':c['curl'],'index':i})
        tr.append(-1)
        i+=1
    tlist=[]
    for x in range(concurrent):
        tlist.append(NewDThread(Q,useproxy,proxyserver,proxyport,proxyuser,
                                proxypass,tr,cv))
    i=0
    while True:
        if control!=[]:
            return None, {'index_url':url}
        qlen=Q.qsize()
        if Q.empty():
            Q.join()
            break
        percent=int((float(ccount-qlen)/float(ccount))*100)
        evt.Value=str(percent)+'%'
        wx.PostEvent(win,evt)
        if dmode=='stream':
            if tr[i] != -1:
                sevt.value="\n"+clist[i]['cname'][0]+"\n"+tr[i]
                wx.PostEvent(win,sevt)
                i+=1
        time.sleep(1)
    i=0
    bb=u''
    for c in clist:
        bb+="\n"+c['cname'][0]+"\n"
        bb+=tr[i]
        i+=1


    if not isinstance(bb,unicode):
        bb=bb.decode('GBK','ignore')
    evt.Value=u'下载完毕!'
    evt.status='ok'
    bookstate={}
    bookstate['bookname']=bkname
    bookstate['index_url']=url
    bookstate['last_chapter_name']=clist[-1:][0]['cname'][0]
    bookstate['last_update']=datetime.today().strftime('%y-%m-%d %H:%M')
    bookstate['chapter_count']=ccount
    wx.PostEvent(win,evt)
    return bb,bookstate







if __name__ == '__main__':
    #GetBook('http://www.ranwen.net/files/article/17/17543/index.html')
    #GetSearchResults(u'修真')
    GetBook("http://www.23xsw.net/book/2/2445/index.html")

