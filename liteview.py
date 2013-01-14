#!/usr/bin/env py32
# -*- coding: utf-8 -*-
#

#
u"""LiteView is a read-only optimized wxpython text control, which provides
following features:
- 3 show modes: paper/book/vbook
- configurable: background(picture)/font/underline/margin
- render speed is almost independent of file size

Author: Hu Jun

update on 12/24/2010
- add scroll-line support
- fix a bug that cause 1.5 character over the right edge of line

Updated: 11/19/2010
- first beta,all major feature implemented

"""
#
#update on 2010.12.26
# fix a bug of breakline
#


#
#update on 2010.12.2
# fix a bug of resizing not working under linux
#
import platform
import sys
MYOS = platform.system()
if MYOS != 'Linux' and MYOS != 'Darwin' and MYOS != 'Windows':
    print "This version of litebook only support Linux and MAC OSX"
    sys.exit(1)
import wx
import re
import time
import os

def cur_file_dir():
    #获取脚本路径
    global MYOS
    if MYOS == 'Linux':
        path = sys.path[0]
    else:
        path = sys.argv[0]

    if isinstance(path,str):
        path=path.decode('utf-8')

    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)



#---------------------------------------------------------------------------

class LiteView(wx.ScrolledWindow):
    u"""LiteView，一个看书的wxpython文本控件，具备如下特性：
        -只读
        -支持 背景（图片）/行间距/下划线/页边距/字体 等可设置
        -支持三种不同的显示模式（纸张/书本/竖排书本）
        -支持文字选择和拷贝（鼠标右键单击拷贝）

    """
    def __init__(self, parent, id = -1, bg_img=None):
        u"""
        bg_img: background image, can be bitmap obj or a string of filepath
        """
        sdc=wx.ScreenDC()
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=sdc.GetSize(), style=wx.SUNKEN_BORDER|wx.CLIP_CHILDREN)
        if platform.system()=='Linux': #this is to fix resize problem under linux
            self.SetMinSize((300,300))
        else:
            self.SetMinSize((150,150))
        #初始化一些设置
        self.TextBackground='white'
        self.SetBackgroundColour(self.TextBackground)
        self.pagemargin=50
        self.bookmargin=50
        self.vbookmargin=50
        self.centralmargin=20
        self.linespace=5
        self.vlinespace=15
        self.Value=""
        self.ValueCharCount=0
        self.under_line=True
        self.under_line_color="GREY"
        self.under_line_style=wx.DOT
        self.curPageTextList=[]
        self.bg_buff=None
        self.newbmp=None
        self.newnewbmp=None
        self.bg_img_path=None
        self.SetImgBackground(bg_img)
        self.bg_style='tile'
        self.show_mode='paper'
        self.buffer_bak=None
        self.TextForeground='black'
        #render direction, used for self.GetHitPos()
        self.RenderDirection=1
        #defaul selection color
        self.DefaultSelectionColor=wx.Colour(255,  0,  0,128)
        #setup the default font
        self.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.current_pos=0
        self.start_pos=0
        self.SelectedRange=[0,0]
        # Initialize the buffer bitmap.  No real DC is needed at this point.
        self.buffer=None
        # Initialize the mouse dragging value
        self.LastMousePos=None
        self.FirstMousePos=None

        #绑定事件处理
##        self.Bind(wx.EVT_SCROLLWIN,self.OnScroll)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CHAR,self.OnChar)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_LEFT_DOWN,self.OnMouseDrag)
        self.Bind(wx.EVT_LEFT_UP,self.OnMouseDrag)
        self.Bind(wx.EVT_MOTION,self.OnMouseDrag)
        self.Bind(wx.EVT_LEFT_DOWN,self.MouseClick)

        #self.Bind(wx.EVT_RIGHT_UP,self.OnMouseDrag)

    def MouseClick(self,evt):
        self.SetFocus()
        evt.Skip()

    def GetHitPos(self,pos):
        """返回坐标所在字在self.Value中的[index,字的坐标]"""
        r={}
        dc=wx.MemoryDC()
        dc.SelectObject(wx.EmptyBitmap(1, 1))#this is needed on MAC OSX
        dc.SetFont(self.GetFont())
        ch_h=dc.GetCharHeight()
        ch_w=dc.GetTextExtent(u'我')[0]
        if self.show_mode=='paper':
            line=pos[1]/(self.linespace+ch_h)
            tlen=len(self.curPageTextList)
            if tlen<=0: return None
            if line>=tlen:line=tlen-1
            pos_list=dc.GetPartialTextExtents(self.curPageTextList[line][0])
            i=0
            tlen=pos[0]-self.pagemargin
            while i<len(pos_list):
                if pos_list[i]>tlen:break
                else:
                    i+=1
            if i>=len(self.curPageTextList[line][0]):
                i=len(self.curPageTextList[line][0])
            m=0
            delta=0

            while m<line:
                delta+=len(self.curPageTextList[m][0])+self.curPageTextList[m][1]
                m+=1
            delta+=i
            if len(self.curPageTextList[line][0])==0:
                x=self.pagemargin
            else:
                x=self.pagemargin+dc.GetTextExtent(self.curPageTextList[line][0][:i])[0]

##            if self.RenderDirection==1 or self.start_pos==0:
##                y=(ch_h+self.linespace)*line
##            else:
##                y=(ch_h+self.linespace)*line+1.5*self.linespace

            y=self.curPageTextList[line][2]
            r['index']=self.start_pos+delta
            r['pos']=(x,y)
            r['line']=line
            r['row']=i
            return r
        elif self.show_mode=='book':
            if self.RenderDirection==1:
                if pos[0]<=self.maxWidth/2:
                    line=pos[1]/(self.linespace+ch_h)
                    tlen=pos[0]-self.bookmargin
                else:
                    line=pos[1]/(self.linespace+ch_h)+len(self.curPageTextList)/2
                    tlen=pos[0]-self.centralmargin-self.maxWidth/2
            else:
                if pos[0]<=self.maxWidth/2:
                    line=self.blockline-((self.maxHeight-pos[1])/(self.linespace+ch_h))-1
                    tlen=pos[0]-self.bookmargin
                else:
                    line=self.blockline-((self.maxHeight-pos[1])/(self.linespace+ch_h))-1+len(self.curPageTextList)/2
                    tlen=pos[0]-self.centralmargin-self.maxWidth/2
            if line>=len(self.curPageTextList):line=len(self.curPageTextList)-1
            pos_list=dc.GetPartialTextExtents(self.curPageTextList[line][0])
            i=0
            while i<len(pos_list):
                if pos_list[i]>tlen:break
                else:
                    i+=1
            if i>=len(self.curPageTextList[line][0]):
                i=len(self.curPageTextList[line][0])
            m=0
            delta=0
            while m<line:
                delta+=len(self.curPageTextList[m][0])+self.curPageTextList[m][1]
                m+=1
            delta+=i
            if pos[0]<=self.maxWidth/2:
                if len(self.curPageTextList[line][0])==0:
                    x=self.bookmargin
                else:
                    x=self.bookmargin+dc.GetTextExtent(self.curPageTextList[line][0][:i])[0]
##                if self.RenderDirection==1 or self.start_pos==0:
##                    y=(ch_h+self.linespace)*line
##                else:
##                    y=(ch_h+self.linespace)*line+self.linespace*1.5
            else:
                if len(self.curPageTextList[line][0])==0:
                    x=self.centralmargin+self.maxWidth/2
                else:
                    x=self.centralmargin+self.maxWidth/2+dc.GetTextExtent(self.curPageTextList[line][0][:i])[0]
##                if self.RenderDirection==1 or self.start_pos==0:
##                    y=(ch_h+self.linespace)*(line-len(self.curPageTextList)/2)
##                else:
##                    y=(ch_h+self.linespace)*(line-len(self.curPageTextList)/2)+self.linespace*1.5
            y=self.curPageTextList[line][2]
            r['index']=self.start_pos+delta
            r['pos']=(x,y)
            r['line']=line
            r['row']=i
            return r
        elif self.show_mode=='vbook':
##            if self.RenderDirection==1:
            newwidth=self.maxWidth/2-self.vbookmargin-self.centralmargin
            newheight=self.maxHeight-2*self.vbookmargin
            self.blockline=newwidth/(ch_w+self.vlinespace)
            if pos[0]>self.maxWidth/2:
                line=(self.maxWidth-self.vbookmargin-pos[0])/(ch_w+self.vlinespace)+1
            else:
                line=(self.maxWidth/2-self.centralmargin-2*ch_w-pos[0])/(ch_w+self.vlinespace)+2+self.blockline
            if line>=len(self.curPageTextList):line=len(self.curPageTextList)-1

            tlen=pos[1]-self.vbookmargin
            if tlen<0:tlen=0
            ti=tlen/(ch_h+2)
            if ti>=len(self.curPageTextList[line][0]):ti=len(self.curPageTextList[line][0])
            m=0
            delta=0
            while m<line:
                delta+=len(self.curPageTextList[m][0])+self.curPageTextList[m][1]
                m+=1
            delta+=ti
            m=0
            y=ti*(ch_h+2)+self.vbookmargin
            if line<=self.blockline:
                x=self.maxWidth-self.vbookmargin-line*(ch_w+self.vlinespace/2+self.vlinespace/2)-self.vlinespace/3
            else:
                x=(self.maxWidth/2)-(self.centralmargin/2)-(line-self.blockline)*(ch_w+self.vlinespace/2+self.vlinespace/2)-ch_w


##            else:
##                #if direction == -1
##                none


            r['index']=self.start_pos+delta
            r['pos']=(x,y)
            r['line']=line
            r['row']=ti
            v1=r['index']
            return r


    def GenSelectColor(self):
        """返回选择文字时候被选择文字的颜色"""
        cf=wx.NamedColour(self.TextForeground)
        oldr=cf.Red()
        oldg=cf.Green()
        oldb=cf.Blue()
        if self.bg_img==None:
            cb=wx.NamedColour(self.TextBackground)
            bgr=cb.Red()
            bgg=cb.Green()
            bgb=cb.Blue()
            newr=(510-oldr-bgr)/2
            newg=(510-oldg-bgg)/2
            newb=(510-oldb-bgb)/2
            if oldr==0: oldr=1
            if oldg==0: oldg=1
            if oldb==0: oldb=1
            if bgr==0:bgr=1
            if bgg==0:bgg=1
            if bgb==0:bgb=1
            if (float(oldg)/float(oldr)<0.5 and float(oldb)/float(oldr)<0.5) or (float(bgg)/float(bgr)<0.5 and float(bgb)/float(bgr)<0.5):
                return (wx.Colour(newr,newg,newb,128))
            else:
                return self.DefaultSelectionColor
        else:
            dc = wx.MemoryDC( )
            dc.SelectObject( self.bg_buff)
            x=dc.GetSize()[0]/2
            y=dc.GetSize()[1]/2
            n=50
            xt=x+n
            b=0
            g=0
            r=0
            while x<xt:
                y+=1
                tc=dc.GetPixel(x,y)
                b+=tc.Blue()
                g+=tc.Green()
                r+=tc.Red()
                x+=1
            b/=n
            g/=n
            r/=n
            newr=(510-oldr-r)/2
            newg=(510-oldg-g)/2
            newb=(510-oldb-b)/2
            if oldr==0: oldr=1
            if oldg==0: oldg=1
            if oldb==0: oldb=1
            if r==0: r=1
            if g==0: g=1
            if b==0: b=1
            if (float(oldg)/float(oldr)<0.5 and float(oldb)/float(oldr)<0.5) or (float(g)/float(r)<0.5 and float(b)/float(r)<0.5):
                return (wx.Colour(newr,newg,newb,128))
            else:
                return self.DefaultSelectionColor



    def DrawSelection(self,dc,r1,r2):
        """内部函数，画出选择文字时的选择条"""
        dc.SetFont(self.GetFont())
        if r1==None or r2==None:return

        ch_h=dc.GetCharHeight()
        ch_w=dc.GetTextExtent(u'我')[0]
        newc=self.GenSelectColor()
        self.blockline=self.maxHeight/(ch_h+self.linespace)
        dc.SetTextForeground(newc)
        dc.BeginDrawing()
        gc = wx.GraphicsContext.Create(dc)
        gc.SetBrush(wx.Brush(newc))
        if self.show_mode=='paper':
            if r1['pos'][1]==r2['pos'][1]:
                #如果在同一行
                dc.SetTextForeground(newc)
                y=r1['pos'][1]
                if r1['pos'][0]>r2['pos'][0]:
                    x1=r2['pos'][0]
                    x2=r1['pos'][0]
                    i1=r2['index']
                    i2=r1['index']
                else:
                    x2=r2['pos'][0]
                    x1=r1['pos'][0]
                    i2=r2['index']
                    i1=r1['index']
                gc.DrawRectangle(x1,y,(x2-x1),ch_h)
            else:
                if r1['pos'][1]>r2['pos'][1]:
                    y2=r1['pos'][1]
                    x2=r1['pos'][0]
                    l2=r1['line']
                    w2=r1['row']
                    y1=r2['pos'][1]
                    x1=r2['pos'][0]
                    l1=r2['line']
                    w1=r2['row']
                elif r1['pos'][1]<r2['pos'][1]:
                    y1=r1['pos'][1]
                    x1=r1['pos'][0]
                    l1=r1['line']
                    w1=r1['row']
                    y2=r2['pos'][1]
                    x2=r2['pos'][0]
                    l2=r2['line']
                    w2=r2['row']
                gc.DrawRectangle(x1,y1,self.maxWidth-self.pagemargin-x1,ch_h)
                line=l1
                y=y1+ch_h+self.linespace
                while line<l2-1:
                    gc.DrawRectangle(self.pagemargin,y,self.maxWidth-2*self.pagemargin,ch_h)
                    line+=1
                    y+=ch_h+self.linespace
                gc.DrawRectangle(self.pagemargin,y,x2-self.pagemargin,ch_h)


        elif self.show_mode=='book':
            if r1['pos'][1]==r2['pos'][1] \
                and ((r1['pos'][0]<=self.maxWidth/2 and r2['pos'][0]<=self.maxWidth/2) \
                or (r1['pos'][0]>self.maxWidth/2 and r2['pos'][0]>self.maxWidth/2)):
                    dc.SetTextForeground(newc)
                    y=r1['pos'][1]
                    if r1['pos'][0]>r2['pos'][0]:
                        x1=r2['pos'][0]
                        x2=r1['pos'][0]
                        i1=r2['index']
                        i2=r1['index']
                    else:
                        x2=r2['pos'][0]
                        x1=r1['pos'][0]
                        i2=r2['index']
                        i1=r1['index']
                    gc.DrawRectangle(x1,y,(x2-x1),ch_h)
            else:
                if r1['index']<r2['index']:
                    y1=r1['pos'][1]
                    x1=r1['pos'][0]
                    l1=r1['line']
                    w1=r1['row']
                    i1=r1['index']
                    i2=r2['index']
                    y2=r2['pos'][1]
                    x2=r2['pos'][0]
                    l2=r2['line']
                    w2=r2['row']

                else:
                    y2=r1['pos'][1]
                    x2=r1['pos'][0]
                    l2=r1['line']
                    w2=r1['row']
                    i1=r2['index']
                    i2=r1['index']

                    y1=r2['pos'][1]
                    x1=r2['pos'][0]
                    l1=r2['line']
                    w1=r2['row']

                #draw book mode
                #draw left page
                if l1<self.blockline:
                    gc.DrawRectangle(x1,y1,self.maxWidth/2-self.centralmargin/2-x1,ch_h)
                    line=l1
                    y=y1+ch_h+self.linespace
                    if l2<=self.blockline:
                        tline=l2-1
                    else:
                        tline=self.blockline-1
                    while line<tline:
                        gc.DrawRectangle(self.bookmargin,y,self.maxWidth/2-self.centralmargin/2-self.bookmargin,ch_h)
                        line+=1
                        y+=ch_h+self.linespace
                    if l2<=self.blockline:
                        gc.DrawRectangle(self.bookmargin,y,x2-self.bookmargin,ch_h)
                #draw right page
                if l2>=self.blockline:
                    y=0
                    if l1>=self.blockline:
                        y=y1
                        gc.DrawRectangle(x1,y,self.maxWidth-self.bookmargin-x1,ch_h)
                        line=l1
                        y+=self.linespace+ch_h
                        while line<l2-1:
                            gc.DrawRectangle(self.maxWidth/2+self.centralmargin/2,y,self.maxWidth-(self.maxWidth/2+self.centralmargin/2+self.bookmargin),ch_h)
                            line+=1
                            y+=ch_h+self.linespace
                        gc.DrawRectangle(self.maxWidth/2+self.centralmargin/2,y,x2-(self.maxWidth/2+self.centralmargin/2),ch_h)
                    else:
                        if l2==line+1:
                            gc.DrawRectangle(self.maxWidth/2+self.centralmargin/2,y,x2-(self.maxWidth/2+self.centralmargin/2),ch_h)
                            y+=self.linespace+ch_h
                        else:

                            if l1>self.blockline:
                                tt=l2
                            else:
                                tt=l2-1
                            while line<tt:
                                gc.DrawRectangle(self.maxWidth/2+self.centralmargin/2,y,self.maxWidth-(self.maxWidth/2+self.centralmargin/2+self.bookmargin),ch_h)
                                line+=1
                                y+=ch_h+self.linespace
                            gc.DrawRectangle(self.maxWidth/2+self.centralmargin/2,y,x2-(self.maxWidth/2+self.centralmargin/2),ch_h)

        elif self.show_mode=='vbook':
            newwidth=self.maxWidth/2-self.vbookmargin-self.centralmargin
            newheight=self.maxHeight-2*self.vbookmargin
            self.blockline=newwidth/(ch_w+self.vlinespace)
            if r1['pos'][0]==r2['pos'][0]:
                if r1['pos'][1]<r2['pos'][1]:
                    x1=r1['pos'][0]
                    x2=r2['pos'][0]
                    y1=r1['pos'][1]
                    y2=r2['pos'][1]
                else:
                    x1=r2['pos'][0]
                    x2=r1['pos'][0]
                    y1=r2['pos'][1]
                    y2=r1['pos'][1]
                bar_wid=ch_w+self.vlinespace/2
                gc.DrawRectangle(x1,y1,bar_wid,y2-y1)
            else:
                bar_wid=ch_w+self.vlinespace/2
                if r1['pos'][0]>r2['pos'][0]:
                    x1=r1['pos'][0]
                    x2=r2['pos'][0]
                    y1=r1['pos'][1]
                    y2=r2['pos'][1]
                    l1=r1['line']
                    l2=r2['line']
                    i1=r1['row']
                    i2=r2['row']
                    v1=r1['index']
                    v2=r2['index']
                else:
                    x1=r2['pos'][0]
                    x2=r1['pos'][0]
                    y1=r2['pos'][1]
                    y2=r1['pos'][1]
                    l1=r2['line']
                    l2=r1['line']
                    i1=r2['row']
                    i2=r1['row']
                    v1=r2['index']
                    v2=r1['index']

                #draw right page
                if l1<=self.blockline:

                    line=l1
                    gc.DrawRectangle(x1,y1,bar_wid,self.maxHeight-self.vbookmargin-y1)
                    line+=1
                    x=x1-(ch_w+self.vlinespace/2+self.vlinespace/2)
                    y=self.vbookmargin
                    if self.blockline>l2:
                        tline=l2
                    else:
                        tline=self.blockline
                    while line<tline:
                        gc.DrawRectangle(x,y,bar_wid,self.maxHeight-2*self.vbookmargin)
                        line+=1
                        x-=(ch_w+self.vlinespace/2+self.vlinespace/2)
                    if tline==l2:
                        gc.DrawRectangle(x,y,bar_wid,(ch_h+2)*i2)
                    else:
                        gc.DrawRectangle(x,y,bar_wid,self.maxHeight-2*self.vbookmargin)
                #draw left page
                if l2>self.blockline:
                    if l1>self.blockline:

                        line=l1
                        gc.DrawRectangle(x1,y1,bar_wid,self.maxHeight-self.vbookmargin-y1)
                        line+=1
                        x=x1-(ch_w+self.vlinespace/2+self.vlinespace/2)
                        y=self.vbookmargin
                        while line<l2:
                            gc.DrawRectangle(x,y,bar_wid,self.maxHeight-2*self.vbookmargin)
                            line+=1
                            x-=(ch_w+self.vlinespace/2+self.vlinespace/2)
                        gc.DrawRectangle(x,y,bar_wid,(ch_h+2)*i2)
                    else:

                        line=self.blockline
                        x=self.maxWidth/2-self.centralmargin-2*ch_w
                        y=self.vbookmargin
                        while line<l2-1:
                            gc.DrawRectangle(x,y,bar_wid,self.maxHeight-2*self.vbookmargin)
                            line+=1
                            x-=(ch_w+self.vlinespace/2+self.vlinespace/2)
                        gc.DrawRectangle(x,y,bar_wid,(ch_h+2)*i2)



        dc.EndDrawing()


    def OnMouseDrag(self,evt):
        """处理鼠标事件的函数，主要是用来处理选择文字极其拷贝的操作"""
        if evt.ButtonDown(wx.MOUSE_BTN_LEFT):
            self.LastMousePos=evt.GetPositionTuple()
            self.FirstMousePos=evt.GetPositionTuple()
            if self.buffer_bak<>None:
                if self.bg_img==None or self.bg_buff==None or self.newbmp==None:
                    self.buffer=self.buffer_bak.GetSubBitmap(wx.Rect(0, 0, self.buffer_bak.GetWidth(), self.buffer_bak.GetHeight()))
                    dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
                else:
                    self.newbmp=self.buffer_bak.GetSubBitmap(wx.Rect(0, 0, self.buffer_bak.GetWidth(), self.buffer_bak.GetHeight()))
                    dc = wx.BufferedDC(wx.ClientDC(self), self.newbmp)
                dc.BeginDrawing()
                dc.EndDrawing()
            return
        if evt.Dragging():
            current_mouse_pos=evt.GetPositionTuple()
            if current_mouse_pos==self.LastMousePos or self.FirstMousePos==None:
                return
            else:
                r1=self.GetHitPos(self.FirstMousePos)
                r2=self.GetHitPos(current_mouse_pos)
                if self.bg_img==None or self.bg_buff==None or self.newbmp==None:
                    self.buffer=self.buffer_bak.GetSubBitmap(wx.Rect(0, 0, self.buffer_bak.GetWidth(), self.buffer_bak.GetHeight()))
                    dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
                else:
                    self.newbmp=self.buffer_bak.GetSubBitmap(wx.Rect(0, 0, self.buffer_bak.GetWidth(), self.buffer_bak.GetHeight()))
                    dc = wx.BufferedDC(wx.ClientDC(self), self.newbmp)
                self.DrawSelection(dc,r1,r2)
            self.LastMousePos=current_mouse_pos
        elif evt.ButtonUp(wx.MOUSE_BTN_LEFT) and not evt.LeftDClick():
            if self.FirstMousePos==None:return
            current_mouse_pos=evt.GetPositionTuple()
            r1=self.GetHitPos(self.FirstMousePos)
            r2=self.GetHitPos(current_mouse_pos)
            if r1==None or r2==None:return
            if r1['index']>r2['index']:
                self.SelectedRange[0]=r2['index']
                self.SelectedRange[1]=r1['index']
##                self.SelectedRange=[r2['index'],r1['index']]
            else:
                self.SelectedRange[1]=r2['index']
                self.SelectedRange[0]=r1['index']
##                self.SelectedRange=[r1['index'],r2['index']]


##        if evt.RightUp():
##            clipdata = wx.TextDataObject()
##            clipdata.SetText(self.Value[self.SelectedRange[0]:self.SelectedRange[1]])
##            if not wx.TheClipboard.IsOpened():
##                wx.TheClipboard.Open()
##                wx.TheClipboard.SetData(clipdata)
##                wx.TheClipboard.Close()
##            if self.buffer_bak<>None:
##                if self.bg_img==None or self.bg_buff==None or self.newbmp==None:
##                    self.buffer=self.buffer_bak.GetSubBitmap(wx.Rect(0, 0, self.buffer_bak.GetWidth(), self.buffer_bak.GetHeight()))
##                    dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
##                else:
##                    self.newbmp=self.buffer_bak.GetSubBitmap(wx.Rect(0, 0, self.buffer_bak.GetWidth(), self.buffer_bak.GetHeight()))
##                    dc = wx.BufferedDC(wx.ClientDC(self), self.newbmp)
##                dc.BeginDrawing()
##                dc.EndDrawing()

    def CopyText(self):
        clipdata = wx.TextDataObject()
        clipdata.SetText(self.Value[self.SelectedRange[0]:self.SelectedRange[1]])
        if not wx.TheClipboard.IsOpened():
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(clipdata)
            wx.TheClipboard.Close()
        if self.buffer_bak<>None:
            if self.bg_img==None or self.bg_buff==None or self.newbmp==None:
                self.buffer=self.buffer_bak.GetSubBitmap(wx.Rect(0, 0, self.buffer_bak.GetWidth(), self.buffer_bak.GetHeight()))
                dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            else:
                self.newbmp=self.buffer_bak.GetSubBitmap(wx.Rect(0, 0, self.buffer_bak.GetWidth(), self.buffer_bak.GetHeight()))
                dc = wx.BufferedDC(wx.ClientDC(self), self.newbmp)
            dc.BeginDrawing()
            dc.EndDrawing()

    def OnChar(self,event):
        """键盘输入控制函数"""
        key=event.GetKeyCode()
        if key == wx.WXK_PAGEDOWN or key==wx.WXK_SPACE or key==wx.WXK_RIGHT:
            self.ScrollP(1)
            return
        if key==wx.WXK_LEFT or key == wx.WXK_PAGEUP:
            self.ScrollP(-1)
            return
        if key == wx.WXK_UP:
            self.ScrollLine(-1)
            return
        if key == wx.WXK_DOWN:
            self.ScrollLine(1)
            return


        if key == wx.WXK_HOME :
            self.ScrollTop()
            return
        if key == wx.WXK_END :
            self.ScrollBottom()
            return
        event.Skip()

    def DrawBackground(self,dc):
        """Draw background according to show_mode and bg_img"""
        sz = dc.GetSize()
        w = self.bg_img.GetWidth()
        h = self.bg_img.GetHeight()
        if self.bg_style=='tile':
            x = 0
            while x <= sz.width:
                y = 0

                while y <= sz.height:
                    dc.DrawBitmap(self.bg_img, x, y)
                    y = y + h
                x = x + w
        else:
            startx=(sz.width-w)/2
            if startx<0:startx=0
            starty=(sz.height-h)/2
            if starty<0:starty=0
            dc.DrawBitmap(self.bg_img,startx,starty)
        self.DrawBookCentral(dc)

##        if self.show_mode=='vbook':
##            oldpen=dc.GetPen()
##            oldbrush=dc.GetBrush()
##            dc.SetPen(wx.Pen('grey',width=5))
##            dc.SetBrush(wx.Brush('white',style=wx.TRANSPARENT))
##            dc.DrawLine(self.vbookmargin,self.vbookmargin,self.maxWidth-self.vbookmargin,self.vbookmargin)
##            dc.DrawLine(self.vbookmargin,self.maxHeight-2*self.vbookmargin,self.maxWidth-self.vbookmargin,self.maxHeight-2*self.vbookmargin)
##            dc.SetPen(oldpen)
##            dc.SetBrush(oldbrush)

##        if self.show_mode=='book' or self.show_mode=='vbook':
##            dc.DrawLine(3,0,3,sz.height)
##            dc.DrawLine(4,0,4,sz.height)
##            dc.DrawLine(6,0,6,sz.height)
##            dc.DrawLine(8,0,8,sz.height)
##            dc.DrawLine(10,0,10,sz.height)
##
##            dc.DrawLine(sz.width-3,0,sz.width-3,sz.height)
##            dc.DrawLine(sz.width-4,0,sz.width-4,sz.height)
##            dc.DrawLine(sz.width-6,0,sz.width-6,sz.height)
##            dc.DrawLine(sz.width-8,0,sz.width-8,sz.height)
##            dc.DrawLine(sz.width-10,0,sz.width-10,sz.height)
##            x=sz.width/2-20
##            y=self.pagemargin+10
##            n=self.pagemargin+10
##            xt=x+n
##            b=0
##            g=0
##            r=0
##            while x<xt:
##                tc=dc.GetPixel(x,y)
##                b+=tc.Blue()
##                g+=tc.Green()
##                r+=tc.Red()
##                x+=1
##            b/=n
##            g/=n
##            r/=n
##
##            dc.GradientFillLinear((sz.width/2-self.centralmargin,0, self.centralmargin,sz.height),wx.Color(r,g,b,0),'grey')
##            dc.GradientFillLinear((sz.width/2,0, self.centralmargin,sz.height),'grey',wx.Color(r,g,b,0))



    def DrawBookCentral(self,dc):
        sz = dc.GetSize()
        if self.show_mode=='book' or self.show_mode=='vbook':
            dc.DrawLine(3,0,3,sz.height)
            dc.DrawLine(4,0,4,sz.height)
            dc.DrawLine(6,0,6,sz.height)
            dc.DrawLine(8,0,8,sz.height)
            dc.DrawLine(10,0,10,sz.height)

            dc.DrawLine(sz.width-3,0,sz.width-3,sz.height)
            dc.DrawLine(sz.width-4,0,sz.width-4,sz.height)
            dc.DrawLine(sz.width-6,0,sz.width-6,sz.height)
            dc.DrawLine(sz.width-8,0,sz.width-8,sz.height)
            dc.DrawLine(sz.width-10,0,sz.width-10,sz.height)
            x=sz.width/2-20
            y=self.pagemargin+10
            n=self.pagemargin+10
            xt=x+n
            b=0
            g=0
            r=0
            while x<xt:
                tc=dc.GetPixel(x,y)
                b+=tc.Blue()
                g+=tc.Green()
                r+=tc.Red()
                x+=1
            b/=n
            g/=n
            r/=n
            dc.GradientFillLinear((sz.width/2-self.centralmargin,0, self.centralmargin,sz.height),wx.Colour(r,g,b,0),'grey')
            dc.GradientFillLinear((sz.width/2,0, self.centralmargin,sz.height),'grey',wx.Colour(r,g,b,0))


    def Clear(self):
        self.SetValue('')
        self.ReDraw()

    def ReDraw(self):
        """ReDraw self"""
        delta=(self.GetSize()[1]-self.GetClientSize()[1])+1
        self.maxHeight=self.GetClientSize()[1]
        self.maxWidth=self.GetClientSize()[0]-delta
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.current_pos=self.start_pos
        self.bg_buff=None
        self.buffer=None
        self.ShowPos(1)
##        self.current_pos=0
        self.current_pos=self.start_pos
        self.ShowPos(1)

        self.Refresh(False)



    def SetShowMode(self,m):
        """设置显示模式，支持的有'book/paper/vbook'"""
        self.show_mode=m

    def GetPos(self):
        """返回当前页面显示最后一个字在self.ValueList中的index"""
        return self.current_pos


    def GetStartPos(self):
        return self.start_pos

    def GetPosPercent(self):
        try:
            return (float(self.current_pos)/float(self.ValueCharCount))*100
        except:
            return False

    def GetConfig(self):
        r={}
        r['pagemargin']=self.pagemargin
        r['bookmargin']=self.bookmargin
        r['vbookmargin']=self.vbookmargin
        r['centralmargin']=self.centralmargin
        r['linespace']=self.linespace
        r['vlinespace']=self.vlinespace
        r['underline']=self.under_line
        r['underlinecolor']=self.under_line_color
        r['underlinestyle']=self.under_line_style
        r['backgroundimg']=self.bg_img_path
        r['backgroundimglayout']=self.bg_style
        r['showmode']=self.show_mode
        return r


    def ScrollHalfP(self,direction=1):
        """翻半页"""
        if self.show_mode<>'paper':return
        line_no=len(self.curPageTextList)
        self.ScrollLine(direction,line_no/2)

    def ScrollPercent(self,percent,direction=1):
        """按百分比翻页"""
        if not isinstance(percent,int) or percent<=0 or percent>100:return
        delta=(self.ValueCharCount*percent)/100
        if direction==1:
            newpos=self.current_pos+delta
            if newpos<self.ValueCharCount:
                self.current_pos=newpos
                self.ShowPos()
            else:
                self.start_pos=self.ValueCharCount
                self.ShowPos(-1)
        else:
            newpos=self.start_pos-delta
            if newpos<=0:
                self.current_pos=0
                self.ShowPos()
            else:
                self.start_pos=newpos
                self.ShowPos(-1)
        self.Refresh()









    def ScrollLine(self,direction=1,line_count=1):
        if self.show_mode<>'paper':return
        line_no=len(self.curPageTextList)
        if line_no == 0:return
        if direction==1:
            if self.curPageTextList[line_no-1][4]>=self.ValueCharCount:
                return
            self.current_pos=self.curPageTextList[line_count-1][4]
            self.ScrollP(1)
        elif direction==-1:
            self.start_pos=self.curPageTextList[line_no-line_count][3]
            self.ScrollP(-1)




    def ScrollTop(self):
        """显示第一页"""
        self.current_pos=0
        self.start_pos=0
        self.ShowPos(1)
        self.Refresh()

    def ScrollBottom(self):
        """显示最后一页"""
        self.start_pos=self.ValueCharCount
        self.ShowPos(-1)
        self.Refresh()

    def ScrollP(self,direction):
        """向上或是向下翻页"""
##        t1=time.time()
        self.ShowPos(direction)
        self.Refresh(False) #Use False to avoid background flicker
##        print time.time()-t1

##    def getPreviousLine(self,txt):
##        llist=txt.splitlines()
##        dc=wx.MemoryDC()
##        dc.SetFont(self.GetFont())
##        delta=2*dc.GetCharHeight()
##        lline=llist[len(llist)-1]
##        newwidth=self.maxWidth-2*self.pagemargin
##        if dc.GetTextExtent(lline)[0]<=newwidth:
##            if txt[len(txt)-1]=='\n':
##                return lline+'\n'
##            else:
##                return lline
##        else:
##            high=len(lline)-1
##            low=0
##
##            while low<high:
##                mid=(low+high)/2
##                if dc.GetTextExtent(lline[mid:])[0]>newwidth:  low=mid+1
##                else:
##                    if dc.GetTextExtent(lline[mid:])[0]<newwidth: high=mid-1
##                    else:
##                        break
##            if dc.GetTextExtent(lline[mid:])[0]>newwidth: mid-=1
##            if txt[len(txt)-1]=='\n': return lline[mid:]+'\n'
##            else:
##                return lline[mid:]


##    def ScrollL(self,direction):
##        """向上或是向下翻行"""
##        if direction==1:
##            self.current_pos=self.start_pos+len(self.curPageTextList[0][0])+self.curPageTextList[0][1]
##            self.ShowPos(1)
##        else:
##            n=len(self.curPageTextList)
##            self.start_pos=self.start_pos+len()
##
##            self.ShowPos(-1)
##
##        self.Refresh()


##    def OnScroll(self,evt):
##        if self.GetScrollPos(wx.VERTICAL)==0:
##            self.ScollP(-1)
####            pass
##        else:
##            if self.GetScrollPos(wx.VERTICAL)+self.GetScrollThumb(wx.VERTICAL)==self.GetScrollRange(wx.VERTICAL):
##                self.ScollP(1)
##        evt.Skip()
    def OnResize(self,evt):
        """处理窗口尺寸变化的事件"""
        self.isdirty=True
        self.ReDraw()
        evt.Skip()




    def OnPaint(self, event):
        """处理重画事件"""
        delta=(self.GetSize()[1]-self.GetClientSize()[1])+1
        self.maxHeight=self.GetClientSize()[1]
        self.maxWidth=self.GetClientSize()[0]-delta
        self.SetVirtualSize((self.maxWidth, self.maxHeight))

        if self.buffer<>None and not self.isdirty:

            if self.bg_img==None or self.bg_buff==None or self.newbmp==None:

                dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
            else:

                dc = wx.BufferedPaintDC(self, self.newbmp, wx.BUFFER_VIRTUAL_AREA)
        else:

            self.ShowPos(1)

    def GetValue(self):
        return self.Value

    def SetValue(self,txt,pos=0):
        """赋值函数，载入并显示一个字符串"""
        #把DOS ending转换成UNIX Ending，否则选择文字的时候会出问题
        self.Value=txt.replace("\r\n","\n")
        self.ValueCharCount=len(self.Value)
        self.current_pos=pos
        self.start_pos=0
        self.Refresh()
        self.ReDraw()

    def JumpTo(self,pos):
        self.current_pos=pos
        self.start_pos=0
        self.ShowPos(1)
        self.ReDraw()

    def SetSpace(self,pagemargin=None,bookmargin=None,vbookmargin=None,centralmargin=None,linespace=None,vlinespace=None):
        if pagemargin<>None:self.pagemargin=pagemargin
        if bookmargin<>None:self.bookmargin=bookmargin
        if vbookmargin<>None:self.vbookmargin=vbookmargin
        if centralmargin<>None:self.centralmargin=centralmargin
        if linespace<>None:self.linespace=linespace
        if vlinespace<>None:self.vlinespace=vlinespace

    def SetUnderline(self,visual=None,style=None,color=None):
        if visual<>None:self.under_line=visual
        if color<>None:self.under_line_color=color
        if style<>None:self.under_line_style=style

    def SetFColor(self,color):
        self.TextForeground=color

    def GetFColor(self):
        return self.TextForeground

    def SetImgBackground(self,img,style='tile'):
        """设置图片背景"""
        self.bg_style=style
        if img==None or img=='':
            self.bg_img=None
            self.bg_img_path=None
            return
        if isinstance(img,wx.Bitmap):
            self.bg_img=img
        else:
            if isinstance(img,str) or isinstance(img,unicode):
                if img=='' or img==None:
                    self.bg_img=None
                    return
                if isinstance(img,str):img=img.decode('gbk')
                if os.name=='nt' or sys.platform=='win32':
                    if img.find('\\')==-1:
                        if not isinstance(sys.argv[0],unicode):
                            argv0=os.path.abspath(sys.argv[0]).decode('gbk')
                        else:
                            argv0=os.path.abspath(sys.argv[0])
                        img=os.path.dirname(argv0)+u"\\background\\"+img
                else:
                    if img.find('/')==-1:
                        img=cur_file_dir()+u"/background/"+img
                if not os.path.exists(img):
                    return False
                self.bg_img_path=img
                self.bg_img=wx.Bitmap(img, wx.BITMAP_TYPE_ANY)
            else:
                self.bg_img=None
##        if self.bg_img<>None:
##            self.bg_img_buffer.BeginDrawing()
##            self.DrawBackground(self.bg_img_buffer)
##            self.bg_img_buffer.EndDrawing()


    def breakline(self,line,dc):
        """内部函数，断句"""
        rr=line
        rlist=[]

        if self.show_mode=='paper':
            newwidth=self.maxWidth-2*self.pagemargin
            #delta=int(dc.GetCharWidth()*2.5)
            delta=dc.GetCharWidth()
            delta=0
        elif self.show_mode=='book':
            newwidth=self.maxWidth/2-self.bookmargin-self.centralmargin
            delta=dc.GetCharHeight()
        elif self.show_mode=='vbook':
            ch_h=dc.GetCharHeight()
            ch_w=dc.GetCharWidth()
            newwidth=self.maxWidth-2*self.vbookmargin
            newheight=self.maxHeight-2*self.vbookmargin
        if self.show_mode=='book' or self.show_mode=='paper':
            llist=dc.GetPartialTextExtents(line)
##            ii=0
##            test=[]
##            while ii<len(line):
##                #test[line[ii]]=llist[ii]
##                test.append((line[ii],llist[ii]))
##                ii+=1
##            print 'newwidth is',newwidth
##            for x in test:
##                print x[0],x[1]
            n=len(llist)-1
            mid=0
            mylen=llist[n]
            while mylen>newwidth:
                high=n
                low=mid
                base=mid
                if base==0:
                    lfix=llist[0]
                else:
                    lfix=llist[base]-llist[base-1]
                mid=(low+high)/2
                while low<=high:
                    if (llist[mid]-llist[base]+lfix)>newwidth:
                        high=mid-1
                    else:
                        if (llist[mid]-llist[base]+lfix)<newwidth:
                            low=mid+1
                        else:
##                            print "give me a break"
##                            print "low,high",low,high
##                            print llist
                            break
                    mid=(low+high)/2
    ##            if dc.GetTextExtent(rr[:mid])[0]>newwidth: mid-=1
                mid+=1
                rlist.append([rr[base:mid],0])
                nstr=rr[base:mid]
#                if nstr[-2:]==u'酒醉':
##                print nstr
##                print 'high is ',high
##                print 'low is ',low
                mylen=llist[n]-llist[mid-1]
            rlist.append([rr[mid:],1])
            return rlist
        elif self.show_mode=='vbook':
            n=newheight/(ch_h+2)
            i=0
            while i<len(line):
                rlist.append([line[i:i+n],0])
                i+=n
            i-=n
            rlist[len(rlist)-1][1]=1
            return rlist





    def mywrap(self,txt):
        """排版"""
        dc=wx.MemoryDC()
        dc.SelectObject(wx.EmptyBitmap(1, 1))
        dc.SetFont(self.GetFont())
        ch_h=dc.GetCharHeight()
        ch_w=dc.GetCharWidth()
        if self.show_mode=='paper':
            newwidth=self.maxWidth-2*self.pagemargin
        elif self.show_mode=='book':
            newwidth=self.maxWidth/2-self.bookmargin-self.centralmargin
        elif self.show_mode=='vbook':
            newwidth=self.maxWidth-2*self.vbookmargin
            newheight=self.maxHeight-2*self.vbookmargin
        rlist=[]
        if self.show_mode=='paper':
            for line in txt.splitlines():
                if dc.GetTextExtent(line)[0]<= newwidth:
                    rlist.append([line,1])
                else:
                    trlist=self.breakline(line,dc)
                    rlist+=trlist
        elif self.show_mode=='book':
            for line in txt.splitlines():
                if dc.GetTextExtent(line)[0]<= newwidth:
                    rlist.append([line,1])
                else:
                    trlist=self.breakline(line,dc)
                    rlist+=trlist
        elif self.show_mode=='vbook':
            for line in txt.splitlines():
                if len(line)*(self.linespace+ch_h)<=newheight:
                    rlist.append([line,1])
                else:
                    trlist=self.breakline(line,dc)
                    rlist+=trlist
        return rlist



    def Find(self,key,pos=0,direction=1):
        if direction==1:
            next_index=self.Value.find(key,pos)
        else:
            next_index=self.Value.rfind(key,0,pos)
        if next_index==-1:return False
        self.JumpTo(next_index)
        self.ReDraw()
        return next_index



    def ShowPosition(self,pos):
        self.start_pos=pos
        self.ShowPos()


    def ShowPos(self,direction=1):
        """从指定位置开始，画出一页的文本"""


##        if self.Value==None or self.Value=='':
##            print "value"
##            self.Value=u"LiteBook 2.0"
##            self.ValueCharCount=len(u"LiteBook 2.0")

        self.isdirty=False
##        if self.start_pos<0: self.start_pos=0
        if self.Value==None:
            return
        if direction==1:
            if self.current_pos>=self.ValueCharCount & self.ValueCharCount<>0:
                return
        else:
            if self.start_pos<=0:
##                self.start_pos=0
                return
##        if direction==1:
##            if self.current_pos>=len(self.Value) & self.ValueCharCount<>0:
##                return


        self.RenderDirection=direction
        dc=wx.MemoryDC()
        dc.SelectObject(wx.EmptyBitmap(1, 1))
        dc.SetFont(self.GetFont())


        ch_h=dc.GetCharHeight()
        ch_w=dc.GetCharWidth()
        maxcount=(self.maxHeight/(ch_h+self.linespace))*((self.maxWidth-2*self.pagemargin)/(ch_w))
        self.blockline=self.maxHeight/(ch_h+self.linespace)
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.buffer = wx.EmptyBitmap(self.maxWidth, self.maxHeight)
        if self.bg_buff==None:
            dc = wx.BufferedDC(None, self.buffer)
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
        else:
            self.newbmp=self.bg_buff.GetSubBitmap(wx.Rect(0, 0, self.bg_buff.GetWidth(), self.bg_buff.GetHeight()));
            dc = wx.BufferedDC(None, self.newbmp)
        dc.SetFont(self.GetFont())
        dc.SetTextForeground(self.TextForeground)
        dc.SetTextBackground('black')
        dc.BeginDrawing()

        #draw backgroup

        if self.bg_img<>None and self.bg_buff==None:
            self.DrawBackground(dc)
            if self.bg_buff==None:
                memory = wx.MemoryDC( )
                x,y = self.GetClientSizeTuple()
                self.bg_buff = wx.EmptyBitmap( x,y, -1 )
                memory.SelectObject( self.bg_buff )
                memory.Blit( 0,0,x,y, dc, 0,0)
                memory.SelectObject( wx.NullBitmap)
        if self.bg_img==None:
            self.DrawBookCentral(dc)

        if self.ValueCharCount==0:
            dc.EndDrawing()
            memory = wx.MemoryDC( )
            x,y = self.GetClientSizeTuple()
            self.buffer_bak = wx.EmptyBitmap( x,y, -1 )
            memory.SelectObject( self.buffer_bak )
            memory.Blit( 0,0,x,y, dc, 0,0)
            memory.SelectObject( wx.NullBitmap)
            return

        if self.show_mode=='paper':
            #draw paper mode
            h=0
            cur_pos=self.current_pos
            cur_x=0
            self.curPageTextList=[]
            if direction==1:

                if cur_pos+maxcount<len(self.Value):
                    tmptxt=self.Value[cur_pos:cur_pos+maxcount]
                else:
                    tmptxt=self.Value[cur_pos:]
                ptxtlist=self.mywrap(tmptxt)
                if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                line=0
                delta=0
                line_start=0
                line_end=0
                while line<self.blockline:
                    dc.DrawText(ptxtlist[line][0],self.pagemargin,h)
                    if self.under_line:
                        oldpen=dc.GetPen()
                        newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                        dc.SetPen(newpen)
                        dc.DrawLine(self.pagemargin,h+ch_h+2,self.maxWidth-self.pagemargin,h+ch_h+2)
                        dc.SetPen(oldpen)
                    line_start=self.current_pos+delta
                    delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                    line_end=self.current_pos+delta
                    self.curPageTextList.append([ptxtlist[line][0],ptxtlist[line][1],h,line_start,line_end])
                    if line==len(ptxtlist)-1:break
                    h+=ch_h+self.linespace
                    line+=1
                self.start_pos=self.current_pos
                self.current_pos+=delta

            else:
                pos1=self.start_pos-maxcount
                if pos1<0: pos1=0
                pos2=self.start_pos
                tmptxt=self.Value[pos1:pos2]
                ptxtlist=self.mywrap(tmptxt)
                if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                line=len(ptxtlist)-1
                if line<0:line=0
                delta=0
                h=self.maxHeight-ch_h
                tlen=len(ptxtlist)-1-self.blockline
                elist=[]
                line_start=0
                line_end=0
                if tlen<0:
                    tmptxt=self.Value[:maxcount]
                    ptxtlist=self.mywrap(tmptxt)
                    if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                    line=0
                    delta=0
                    h=0
                    cpos=0
                    while line<self.blockline:
                        dc.DrawText(ptxtlist[line][0],self.pagemargin,h)

                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(self.pagemargin,h+ch_h+2,self.maxWidth-self.pagemargin,h+ch_h+2)
                            dc.SetPen(oldpen)
                        line_start=cpos+delta
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        line_end=cpos+delta
                        self.curPageTextList.append([ptxtlist[line][0],ptxtlist[line][1],h,line_start,line_end])
                        if line==len(ptxtlist)-1:break
                        h+=ch_h+self.linespace
                        line+=1
                    self.start_pos=delta
                    self.current_pos=delta
                else:
                    delta=0
                    while line>tlen :
                        dc.DrawText(ptxtlist[line][0],self.pagemargin,h)
                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(self.pagemargin,h+ch_h+2,self.maxWidth-self.pagemargin,h+ch_h+2)
                            dc.SetPen(oldpen)

                        line_end=self.start_pos-delta
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        line_start=self.start_pos-delta
                        elist.append([ptxtlist[line][0],ptxtlist[line][1],h,line_start,line_end])
                        h-=(ch_h+self.linespace)
                        line-=1

                self.current_pos=self.start_pos

                self.start_pos-=delta
                i=len(elist)-1
                while i>=0:
                    self.curPageTextList.append(elist[i])
                    i-=1
        elif self.show_mode=='book':
            #draw book mode
            h=0
            cur_pos=self.current_pos
            cur_x=0
            self.curPageTextList=[]
            if direction==1:
                if cur_pos+maxcount<len(self.Value):
                    tmptxt=self.Value[cur_pos:cur_pos+maxcount]
                else:
                    tmptxt=self.Value[cur_pos:]
                ptxtlist=self.mywrap(tmptxt)
                if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                line=0
                delta=0
                #draw left page
                while line<self.blockline:
                    dc.DrawText(ptxtlist[line][0],self.bookmargin,h)
                    self.curPageTextList.append([ptxtlist[line][0],ptxtlist[line][1],h])
                    if self.under_line:
                        oldpen=dc.GetPen()
                        newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                        dc.SetPen(newpen)
                        dc.DrawLine(self.bookmargin,h+ch_h+2,self.maxWidth-self.bookmargin,h+ch_h+2)
                        dc.SetPen(oldpen)
                    delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                    if line==len(ptxtlist)-1:break
                    h+=ch_h+self.linespace
                    line+=1
                #draw right page
                if line>=self.blockline:
                    h=0
                    newx=self.maxWidth/2+self.centralmargin
                    while line<2*self.blockline:
                        dc.DrawText(ptxtlist[line][0],newx,h)
                        self.curPageTextList.append([ptxtlist[line][0],ptxtlist[line][1],h])
    ##                    if self.under_line:
    ##                        oldpen=dc.GetPen()
    ##                        newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
    ##                        dc.SetPen(newpen)
    ##                        dc.DrawLine(self.maxWidth/2+self.centralmargin,h+ch_h+2,self.maxWidth-self.bookmargin,h+ch_h+2)
    ##                        dc.SetPen(oldpen)
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        if line==len(ptxtlist)-1:break
                        h+=ch_h+self.linespace
                        line+=1
                self.start_pos=self.current_pos
                self.current_pos+=delta

            else:
                pos1=self.start_pos-maxcount
                if pos1<0: pos1=0
                pos2=self.start_pos
                tmptxt=self.Value[pos1:pos2]
                ptxtlist=self.mywrap(tmptxt)
                if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                line=len(ptxtlist)-1
                if line<0:line=0
                delta=0
                h=self.maxHeight-ch_h
                tlen=len(ptxtlist)-1-2*self.blockline
                elist=[]
                if tlen<0:
                    tmptxt=self.Value[:maxcount]
                    ptxtlist=self.mywrap(tmptxt)
                    if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                    line=0
                    delta=0
                    h=0
                    #draw left page
                    while line<self.blockline:
                        dc.DrawText(ptxtlist[line][0],self.pagemargin,h)
                        self.curPageTextList.append([ptxtlist[line][0],ptxtlist[line][1],h])
                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(self.pagemargin,h+ch_h+2,self.maxWidth-self.pagemargin,h+ch_h+2)
                            dc.SetPen(oldpen)
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        if line==len(ptxtlist)-1:break
                        h+=ch_h+self.linespace
                        line+=1
                    #draw right page
                    h=0
                    newx=self.maxWidth/2+self.centralmargin
                    while line<2*self.blockline:
                        dc.DrawText(ptxtlist[line][0],newx,h)
                        self.curPageTextList.append([ptxtlist[line][0],ptxtlist[line][1],h])
##                        if self.under_line:
##                            oldpen=dc.GetPen()
##                            print "i am e"
##                            #newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
##                            print "style is ",self.under_line_style
##                            print "dot is ",wx.DOT
##                            print "newpen sty is ",newpen.GetStyle()
##                            dc.SetPen(newpen)
##                            dc.DrawLine(self.maxWidth/2+self.centralmargin,h+ch_h+2,self.maxWidth-self.bookmargin,h+ch_h+2)
##                            dc.SetPen(oldpen)
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        if line==len(ptxtlist)-1:break
                        h+=ch_h+self.linespace
                        line+=1
                    self.start_pos=delta
                    self.current_pos=delta
                else:
                    elist_right=[]
                    line=tlen+self.blockline
                    #draw left page
                    while line>tlen:
                        dc.DrawText(ptxtlist[line][0],self.pagemargin,h)
                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(self.pagemargin,h+ch_h+2,self.maxWidth-self.pagemargin,h+ch_h+2)
                            dc.SetPen(oldpen)
                        elist.append([ptxtlist[line][0],ptxtlist[line][1],h])
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        h-=(ch_h+self.linespace)
                        line-=1
                    #draw right page
                    h=self.maxHeight-ch_h
                    newx=self.maxWidth/2+self.centralmargin
                    line=len(ptxtlist)-1
                    while line>tlen+self.blockline:
                        dc.DrawText(ptxtlist[line][0],newx,h)
##                        if self.under_line:
##                            oldpen=dc.GetPen()
##                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
##                            dc.SetPen(newpen)
##                            dc.DrawLine(self.pagemargin,h+ch_h+2,self.maxWidth-self.pagemargin,h+ch_h+2)
##                            dc.SetPen(oldpen)
                        elist_right.append([ptxtlist[line][0],ptxtlist[line][1],h])
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        h-=(ch_h+self.linespace)
                        line-=1

                self.current_pos=self.start_pos
                self.start_pos-=delta
                i=len(elist)-1
                while i>=0:
                    self.curPageTextList.append(elist[i])
                    i-=1
                if self.RenderDirection==-1 & self.start_pos<>0:
                    i=len(elist_right)-1
                    while i>=0:
                        self.curPageTextList.append(elist_right[i])
                        i-=1

        elif self.show_mode=='vbook':
            #draw vertical book
            ch_w=dc.GetTextExtent(u'我')[0]

            h=0
            cur_pos=self.current_pos
            cur_x=0
            self.curPageTextList=[]
            newwidth=self.maxWidth/2-self.vbookmargin-self.centralmargin
            newheight=self.maxHeight-2*self.vbookmargin
            self.blockline=newwidth/(ch_w+self.vlinespace)
            if direction==1:
                if cur_pos+maxcount<len(self.Value):
                    tmptxt=self.Value[cur_pos:cur_pos+maxcount]
                else:
                    tmptxt=self.Value[cur_pos:]
                ptxtlist=self.mywrap(tmptxt)
                if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                line=0
                delta=0
                #draw right page

                x=self.maxWidth-self.vbookmargin
                while line<=self.blockline:
                    y=self.vbookmargin

                    for chh in ptxtlist[line][0]:
                        dc.DrawText(chh,x,y)
                        y+=(ch_h+2)
                    x-=(self.vlinespace/2)
                    self.curPageTextList.append(ptxtlist[line])
                    if self.under_line:
                        oldpen=dc.GetPen()
                        newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                        dc.SetPen(newpen)
                        dc.DrawLine(x,self.vbookmargin,x,self.maxHeight-self.vbookmargin)
                        dc.SetPen(oldpen)
                    x-=(ch_w+self.vlinespace/2)
                    delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                    if line==len(ptxtlist)-1:break
                    line+=1
                #draw left page
                if line>self.blockline:
                    x=self.maxWidth/2-self.centralmargin-2*ch_w
                    while line<=2*self.blockline:
                        y=self.vbookmargin
                        for chh in ptxtlist[line][0]:
                            dc.DrawText(chh,x,y)
                            y+=(ch_h+2)
                        x-=(self.vlinespace/2)
                        self.curPageTextList.append(ptxtlist[line])
                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(x,self.vbookmargin,x,self.maxHeight-self.vbookmargin)
                            dc.SetPen(oldpen)
                        x-=(ch_w+self.vlinespace/2)
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        if line==len(ptxtlist)-1:break
                        line+=1
                self.start_pos=self.current_pos
                self.current_pos+=delta

            else:

                pos1=self.start_pos-maxcount
                if pos1<0: pos1=0
                pos2=self.start_pos
                tmptxt=self.Value[pos1:pos2]
                ptxtlist=self.mywrap(tmptxt)
                if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                line=len(ptxtlist)-1
                if line<0:line=0
                delta=0
                h=self.maxHeight-ch_h
                tlen=len(ptxtlist)-1-2*self.blockline
                elist=[]
                if tlen<0:
                    tmptxt=self.Value[:maxcount]
                    ptxtlist=self.mywrap(tmptxt)
                    if tmptxt[len(tmptxt)-1]<>'\n':ptxtlist[len(ptxtlist)-1][1]=0
                    line=0
                    delta=0
                    h=0
                    #draw right page
                    x=self.maxWidth-self.vbookmargin
                    while line<=self.blockline:
                        y=self.vbookmargin
                        for chh in ptxtlist[line][0]:
                            dc.DrawText(chh,x,y)
                            y+=(ch_h+2)
                        x-=(self.vlinespace/2)
                        self.curPageTextList.append(ptxtlist[line])
                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(x,self.vbookmargin,x,self.maxHeight-self.vbookmargin)
                            dc.SetPen(oldpen)
                        x-=(ch_w+self.vlinespace/2)
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        if line==len(ptxtlist)-1:break
                        line+=1
                    #draw left page
                    x=self.maxWidth/2-self.centralmargin-2*ch_w
                    while line<=2*self.blockline:
                        y=self.vbookmargin
                        for chh in ptxtlist[line][0]:
                            dc.DrawText(chh,x,y)
                            y+=(ch_h+2)
                        x-=(self.vlinespace/2)
                        self.curPageTextList.append(ptxtlist[line])
                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(x,self.vbookmargin,x,self.maxHeight-self.vbookmargin)
                            dc.SetPen(oldpen)
                        x-=(ch_w+self.vlinespace/2)
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        if line==len(ptxtlist)-1:break
                        line+=1
                    self.start_pos=delta
                    self.current_pos=delta
                else:
                    line=tlen
                    #line=0
                    #draw right page
                    x=self.maxWidth-self.vbookmargin
                    while line<=tlen+self.blockline:
                        y=self.vbookmargin
                        for chh in ptxtlist[line][0]:
                            dc.DrawText(chh,x,y)
                            y+=(ch_h+2)
                        x-=(self.vlinespace/2)
                        self.curPageTextList.append(ptxtlist[line])
                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(x,self.vbookmargin,x,self.maxHeight-self.vbookmargin)
                            dc.SetPen(oldpen)
                        x-=(ch_w+self.vlinespace/2)
                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        if line==len(ptxtlist)-1:break
                        line+=1
                    #draw left page
                    x=self.maxWidth/2-self.centralmargin-2*ch_w
                    line=tlen+self.blockline+1
                    while line<len(ptxtlist):
                        y=self.vbookmargin
                        for chh in ptxtlist[line][0]:
                            dc.DrawText(chh,x,y)
                            y+=(ch_h+2)
                        x-=(self.vlinespace/2)
                        if self.under_line:
                            oldpen=dc.GetPen()
                            newpen=wx.Pen(self.under_line_color,style=self.under_line_style)
                            dc.SetPen(newpen)
                            dc.DrawLine(x,self.vbookmargin,x,self.maxHeight-self.vbookmargin)
                            dc.SetPen(oldpen)
                        x-=(ch_w+self.vlinespace/2)
                        self.curPageTextList.append(ptxtlist[line])


                        delta+=len(ptxtlist[line][0])+ptxtlist[line][1]
                        line+=1

                self.current_pos=self.start_pos
                self.start_pos-=delta
                i=len(elist)-1
                while i>=0:
                    self.curPageTextList.append(elist[i])
                    i-=1
        dc.EndDrawing()

        memory = wx.MemoryDC( )
        x,y = self.GetClientSizeTuple()
        self.buffer_bak = wx.EmptyBitmap( x,y, -1 )
        memory.SelectObject( self.buffer_bak )
        memory.Blit( 0,0,x,y, dc, 0,0)
        memory.SelectObject( wx.NullBitmap)






class MyTestFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.Maximize(True)


        # Tool Bar
        self.frame_1_toolbar = wx.ToolBar(self, -1)
        self.SetToolBar(self.frame_1_toolbar)
        # Tool Bar end
        self.frame_1_statusbar = self.CreateStatusBar(1, 0)

        # Menu Bar
        self.frame_1_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(101, u"关于(&A)", u"关于本程序", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "item")
        self.SetMenuBar(self.frame_1_menubar)
        # Menu Bar end
        self.Bind(wx.EVT_MENU, self.Menu101, id=101)
        self.__set_properties()
        self.panel_1 = LiteView(self)
        self.__do_layout()



    def Menu101(self,evt):
        self.ShowFullScreen(True,wx.FULLSCREEN_ALL)



        # end wxGlade

    def __set_properties(self):
        self.frame_1_toolbar.Realize()
        self.frame_1_statusbar.SetStatusWidths([-1])
        # statusbar fields
        frame_1_statusbar_fields = ["frame_1_statusbar"]
        for i in range(len(frame_1_statusbar_fields)):
            self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

# end of class MyFrame




if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyTestFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    if len(sys.argv)<=1:
        fp=open("3.txt",'r')
    else:
        fp=open(sys.argv[1],'r')
    alltxt=fp.read()
    alltxt=alltxt.decode('gbk','ignore')
    if len(sys.argv)<=2:
        frame_1.panel_1.SetImgBackground('6.jpg')
        pass
    else:
        frame_1.panel_1.SetImgBackgroup(sys.argv[2])
    if len(sys.argv)<=3:
        frame_1.panel_1.SetShowMode('paper')
    else:
        frame_1.panel_1.SetShowMode(sys.argv[3])
    frame_1.panel_1.SetValue(alltxt)
##    frame_1.panel_1.Refresh()
##    frame_1.panel_1.Update()

    app.MainLoop()


