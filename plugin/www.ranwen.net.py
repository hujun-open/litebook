#!/usr/bin/env python
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

Description=u"""支持的网站: http://www.ranwen.net/
插件版本：1.0
发布时间: 2013-01-02
简介：
    - 支持多线程下载
    - 关键字不能为空
    - 支持HTTP代理
作者：litebook.author@gmail.com
"""

SearchURL='http://www.ranwen.net/modules/article/search.php'

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

def htm2txt(inf):
    """ extract the text context"""
    doc=html.document_fromstring(inf)
    content=doc.xpath('//*[@id="bgdiv"]/table[2]/tbody/tr[1]/td/table/tbody/tr')
    htmls=html.tostring(content[0],False)
    htmls=htmls.replace('<br>','\n')
    htmls=htmls.replace('<p>','\n')
    htmls=htmls.replace('&#160;',' ')
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
    post_data=urllib.urlencode({u"searchkey":key,u'searchType':'articlename'})
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
    rtable=doc.xpath('//*[@id="searchhight"]/table') #get the main table, you could use chrome inspect element to get the xpath
    if len(rtable)!=0:
        row_list=rtable[0].findall('tr') #get the row list
        row_list=row_list[1:] #remove first row of caption
        for row in row_list:
            r={}
            col_list = row.getchildren() #get col list in each row
            r['bookname']=col_list[0].xpath('a')[0].text
            r['book_index_url']=col_list[1].xpath('a')[0].get('href')
            r['authorname']=col_list[2].xpath('a')[0].text
            r['booksize']=col_list[3].text
            r['lastupdatetime']=col_list[4].text
            r['bookstatus']=col_list[5].xpath('font')[0].text
            rlist.append(r)
        return rlist
    else:#means the search result is a direct hit, the result page is the book portal page
        #rtable=doc.xpath('//*[@id="content"]/div[2]/div[2]/table')
        r={}
        r['bookname']=doc.xpath('//*[@id="content"]/div[2]/div[2]/table/tr/td/table/tbody/tr[1]/td/table/tr[1]/td/h1')[0].text
        r['bookstatus']=doc.xpath('//*[@id="content"]/div[2]/div[2]/table/tr/td/table/tbody/tr[1]/td/table/tr[2]/td[2]/table/tr[1]/td[4]')[0].text
        r['lastupdatetime']=doc.xpath('//*[@id="content"]/div[2]/div[2]/table/tr/td/table/tbody/tr[1]/td/table/tr[2]/td[2]/table/tr[1]/td[6]')[0].text
        r['authorname']=doc.xpath('//*[@id="content"]/div[2]/div[2]/table/tr/td/table/tbody/tr[1]/td/table/tr[2]/td[2]/table/tr[2]/td[6]/a/b')[0].text
        r['book_index_url']=doc.xpath('//*[@id="content"]/div[2]/div[2]/table/tr/td/table/tbody/tr[1]/td/table/tr[2]/td[2]/table/tr[4]/td/div/b/a[1]')[0].get('href')
        r['booksize']=''
##        for k,v in r.items():
##            print k,v
        return [r]
    return []

def GetBook(url,bkname='',win=None,evt=None,useproxy=False,proxyserver='',
            proxyport=0,proxyuser='',proxypass='',concurrent=10,
            mode='new',last_chapter_count=0,):
    """
    mode is either 'new' or 'update', default is 'new', update is used to
    retrie the updated part
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
    r=doc.xpath('//*[@id="defaulthtml4"]/table') #get the main table, you could use chrome inspect element to get the xpath
    row_list=r[0].findall('tr') #get the row list
    clist=[]
    for r in row_list:
        for col in r.getchildren(): #get col list in each row
            for a in col.xpath('div/a'): #use relative xpath to locate <a>
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
        tlist.append(NewDThread(Q,useproxy,proxyserver,proxyport,proxyuser,proxypass,tr,cv))
    while True:
        qlen=Q.qsize()
        if Q.empty():
            Q.join()
            break
        percent=int((float(ccount-qlen)/float(ccount))*100)
        evt.Value=u'正在下载 '+bkname+u' '+str(percent)+'%'
        wx.PostEvent(win,evt)
        time.sleep(1)
    i=0
    bb=u''
    for c in clist:
        bb+=c['cname'][0]
        bb+=tr[i]
        i+=1


    if not isinstance(bb,unicode):
        bb=bb.decode('GBK','ignore')
    evt.Value=bkname+u' 下载完毕!'
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
    GetBook('http://www.ranwen.net/files/article/17/17543/index.html')
    #GetSearchResults(u'修真世界')

