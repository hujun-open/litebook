#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a grid based class used to configure keymap

import wx
import wx.grid as gridlib
import string

# begin wxGlade: extracode
# end wxGlade


KeyMap = {
            wx.WXK_BACK : "WXK_BACK",
            wx.WXK_TAB : "WXK_TAB",
            wx.WXK_RETURN : "WXK_RETURN",
            wx.WXK_ESCAPE : "WXK_ESCAPE",
            wx.WXK_SPACE : "WXK_SPACE",
            wx.WXK_DELETE : "WXK_DELETE",
            wx.WXK_START : "WXK_START",
            wx.WXK_LBUTTON : "WXK_LBUTTON",
            wx.WXK_RBUTTON : "WXK_RBUTTON",
            wx.WXK_CANCEL : "WXK_CANCEL",
            wx.WXK_MBUTTON : "WXK_MBUTTON",
            wx.WXK_CLEAR : "WXK_CLEAR",
            wx.WXK_SHIFT : "WXK_SHIFT",
            wx.WXK_ALT : "WXK_ALT",
            wx.WXK_CONTROL : "WXK_CONTROL",
            wx.WXK_MENU : "WXK_MENU",
            wx.WXK_PAUSE : "WXK_PAUSE",
            wx.WXK_CAPITAL : "WXK_CAPITAL",
            #wx.WXK_PRIOR : "WXK_PRIOR",
            #wx.WXK_NEXT : "WXK_NEXT",
            wx.WXK_END : "WXK_END",
            wx.WXK_HOME : "WXK_HOME",
            wx.WXK_LEFT : "WXK_LEFT",
            wx.WXK_UP : "WXK_UP",
            wx.WXK_RIGHT : "WXK_RIGHT",
            wx.WXK_DOWN : "WXK_DOWN",
            wx.WXK_SELECT : "WXK_SELECT",
            wx.WXK_PRINT : "WXK_PRINT",
            wx.WXK_EXECUTE : "WXK_EXECUTE",
            wx.WXK_SNAPSHOT : "WXK_SNAPSHOT",
            wx.WXK_INSERT : "WXK_INSERT",
            wx.WXK_HELP : "WXK_HELP",
            wx.WXK_NUMPAD0 : "WXK_NUMPAD0",
            wx.WXK_NUMPAD1 : "WXK_NUMPAD1",
            wx.WXK_NUMPAD2 : "WXK_NUMPAD2",
            wx.WXK_NUMPAD3 : "WXK_NUMPAD3",
            wx.WXK_NUMPAD4 : "WXK_NUMPAD4",
            wx.WXK_NUMPAD5 : "WXK_NUMPAD5",
            wx.WXK_NUMPAD6 : "WXK_NUMPAD6",
            wx.WXK_NUMPAD7 : "WXK_NUMPAD7",
            wx.WXK_NUMPAD8 : "WXK_NUMPAD8",
            wx.WXK_NUMPAD9 : "WXK_NUMPAD9",
            wx.WXK_MULTIPLY : "WXK_MULTIPLY",
            wx.WXK_ADD : "WXK_ADD",
            wx.WXK_SEPARATOR : "WXK_SEPARATOR",
            wx.WXK_SUBTRACT : "WXK_SUBTRACT",
            wx.WXK_DECIMAL : "WXK_DECIMAL",
            wx.WXK_DIVIDE : "WXK_DIVIDE",
            wx.WXK_F1 : "WXK_F1",
            wx.WXK_F2 : "WXK_F2",
            wx.WXK_F3 : "WXK_F3",
            wx.WXK_F4 : "WXK_F4",
            wx.WXK_F5 : "WXK_F5",
            wx.WXK_F6 : "WXK_F6",
            wx.WXK_F7 : "WXK_F7",
            wx.WXK_F8 : "WXK_F8",
            wx.WXK_F9 : "WXK_F9",
            wx.WXK_F10 : "WXK_F10",
            wx.WXK_F11 : "WXK_F11",
            wx.WXK_F12 : "WXK_F12",
            wx.WXK_F13 : "WXK_F13",
            wx.WXK_F14 : "WXK_F14",
            wx.WXK_F15 : "WXK_F15",
            wx.WXK_F16 : "WXK_F16",
            wx.WXK_F17 : "WXK_F17",
            wx.WXK_F18 : "WXK_F18",
            wx.WXK_F19 : "WXK_F19",
            wx.WXK_F20 : "WXK_F20",
            wx.WXK_F21 : "WXK_F21",
            wx.WXK_F22 : "WXK_F22",
            wx.WXK_F23 : "WXK_F23",
            wx.WXK_F24 : "WXK_F24",
            wx.WXK_NUMLOCK : "WXK_NUMLOCK",
            wx.WXK_SCROLL : "WXK_SCROLL",
            wx.WXK_PAGEUP : "WXK_PAGEUP",
            wx.WXK_PAGEDOWN : "WXK_PAGEDOWN",
            wx.WXK_NUMPAD_SPACE : "WXK_NUMPAD_SPACE",
            wx.WXK_NUMPAD_TAB : "WXK_NUMPAD_TAB",
            wx.WXK_NUMPAD_ENTER : "WXK_NUMPAD_ENTER",
            wx.WXK_NUMPAD_F1 : "WXK_NUMPAD_F1",
            wx.WXK_NUMPAD_F2 : "WXK_NUMPAD_F2",
            wx.WXK_NUMPAD_F3 : "WXK_NUMPAD_F3",
            wx.WXK_NUMPAD_F4 : "WXK_NUMPAD_F4",
            wx.WXK_NUMPAD_HOME : "WXK_NUMPAD_HOME",
            wx.WXK_NUMPAD_LEFT : "WXK_NUMPAD_LEFT",
            wx.WXK_NUMPAD_UP : "WXK_NUMPAD_UP",
            wx.WXK_NUMPAD_RIGHT : "WXK_NUMPAD_RIGHT",
            wx.WXK_NUMPAD_DOWN : "WXK_NUMPAD_DOWN",
            #wx.WXK_NUMPAD_PRIOR : "WXK_NUMPAD_PRIOR",
            wx.WXK_NUMPAD_PAGEUP : "WXK_NUMPAD_PAGEUP",
            #wx.WXK_NUMPAD_NEXT : "WXK_NUMPAD_NEXT",
            wx.WXK_NUMPAD_PAGEDOWN : "WXK_NUMPAD_PAGEDOWN",
            wx.WXK_NUMPAD_END : "WXK_NUMPAD_END",
            wx.WXK_NUMPAD_BEGIN : "WXK_NUMPAD_BEGIN",
            wx.WXK_NUMPAD_INSERT : "WXK_NUMPAD_INSERT",
            wx.WXK_NUMPAD_DELETE : "WXK_NUMPAD_DELETE",
            wx.WXK_NUMPAD_EQUAL : "WXK_NUMPAD_EQUAL",
            wx.WXK_NUMPAD_MULTIPLY : "WXK_NUMPAD_MULTIPLY",
            wx.WXK_NUMPAD_ADD : "WXK_NUMPAD_ADD",
            wx.WXK_NUMPAD_SEPARATOR : "WXK_NUMPAD_SEPARATOR",
            wx.WXK_NUMPAD_SUBTRACT : "WXK_NUMPAD_SUBTRACT",
            wx.WXK_NUMPAD_DECIMAL : "WXK_NUMPAD_DECIMAL",
            wx.WXK_NUMPAD_DIVIDE : "WXK_NUMPAD_DIVIDE",

            wx.WXK_WINDOWS_LEFT : "WXK_WINDOWS_LEFT",
            wx.WXK_WINDOWS_RIGHT : "WXK_WINDOWS_RIGHT",
            wx.WXK_WINDOWS_MENU : "WXK_WINDOWS_MENU",

            wx.WXK_COMMAND : "WXK_COMMAND",

            wx.WXK_SPECIAL1 : "WXK_SPECIAL1",
            wx.WXK_SPECIAL2 : "WXK_SPECIAL2",
            wx.WXK_SPECIAL3 : "WXK_SPECIAL3",
            wx.WXK_SPECIAL4 : "WXK_SPECIAL4",
            wx.WXK_SPECIAL5 : "WXK_SPECIAL5",
            wx.WXK_SPECIAL6 : "WXK_SPECIAL6",
            wx.WXK_SPECIAL7 : "WXK_SPECIAL7",
            wx.WXK_SPECIAL8 : "WXK_SPECIAL8",
            wx.WXK_SPECIAL9 : "WXK_SPECIAL9",
            wx.WXK_SPECIAL10 : "WXK_SPECIAL10",
            wx.WXK_SPECIAL11 : "WXK_SPECIAL11",
            wx.WXK_SPECIAL12 : "WXK_SPECIAL12",
            wx.WXK_SPECIAL13 : "WXK_SPECIAL13",
            wx.WXK_SPECIAL14 : "WXK_SPECIAL14",
            wx.WXK_SPECIAL15 : "WXK_SPECIAL15",
            wx.WXK_SPECIAL16 : "WXK_SPECIAL16",
            wx.WXK_SPECIAL17 : "WXK_SPECIAL17",
            wx.WXK_SPECIAL18 : "WXK_SPECIAL18",
            wx.WXK_SPECIAL19 : "WXK_SPECIAL19",
            wx.WXK_SPECIAL2 : "WXK_SPECIAL2",
        }

RKeyMap= {
"WXK_BACK":wx.WXK_BACK,
"WXK_TAB":wx.WXK_TAB,
"WXK_RETURN":wx.WXK_RETURN,
"WXK_ESCAPE":wx.WXK_ESCAPE,
"WXK_SPACE":wx.WXK_SPACE,
"WXK_DELETE":wx.WXK_DELETE,
"WXK_START":wx.WXK_START,
"WXK_LBUTTON":wx.WXK_LBUTTON,
"WXK_RBUTTON":wx.WXK_RBUTTON,
"WXK_CANCEL":wx.WXK_CANCEL,
"WXK_MBUTTON":wx.WXK_MBUTTON,
"WXK_CLEAR":wx.WXK_CLEAR,
"WXK_SHIFT":wx.WXK_SHIFT,
"WXK_ALT":wx.WXK_ALT,
"WXK_CONTROL":wx.WXK_CONTROL,
"WXK_MENU":wx.WXK_MENU,
"WXK_PAUSE":wx.WXK_PAUSE,
"WXK_CAPITAL":wx.WXK_CAPITAL,
# "WXK_PRIOR":wx.WXK_PRIOR,
# "WXK_NEXT":wx.WXK_NEXT,
"WXK_END":wx.WXK_END,
"WXK_HOME":wx.WXK_HOME,
"WXK_LEFT":wx.WXK_LEFT,
"WXK_UP":wx.WXK_UP,
"WXK_RIGHT":wx.WXK_RIGHT,
"WXK_DOWN":wx.WXK_DOWN,
"WXK_SELECT":wx.WXK_SELECT,
"WXK_PRINT":wx.WXK_PRINT,
"WXK_EXECUTE":wx.WXK_EXECUTE,
"WXK_SNAPSHOT":wx.WXK_SNAPSHOT,
"WXK_INSERT":wx.WXK_INSERT,
"WXK_HELP":wx.WXK_HELP,
"WXK_NUMPAD0":wx.WXK_NUMPAD0,
"WXK_NUMPAD1":wx.WXK_NUMPAD1,
"WXK_NUMPAD2":wx.WXK_NUMPAD2,
"WXK_NUMPAD3":wx.WXK_NUMPAD3,
"WXK_NUMPAD4":wx.WXK_NUMPAD4,
"WXK_NUMPAD5":wx.WXK_NUMPAD5,
"WXK_NUMPAD6":wx.WXK_NUMPAD6,
"WXK_NUMPAD7":wx.WXK_NUMPAD7,
"WXK_NUMPAD8":wx.WXK_NUMPAD8,
"WXK_NUMPAD9":wx.WXK_NUMPAD9,
"WXK_MULTIPLY":wx.WXK_MULTIPLY,
"WXK_ADD":wx.WXK_ADD,
"WXK_SEPARATOR":wx.WXK_SEPARATOR,
"WXK_SUBTRACT":wx.WXK_SUBTRACT,
"WXK_DECIMAL":wx.WXK_DECIMAL,
"WXK_DIVIDE":wx.WXK_DIVIDE,
"WXK_F1":wx.WXK_F1,
"WXK_F2":wx.WXK_F2,
"WXK_F3":wx.WXK_F3,
"WXK_F4":wx.WXK_F4,
"WXK_F5":wx.WXK_F5,
"WXK_F6":wx.WXK_F6,
"WXK_F7":wx.WXK_F7,
"WXK_F8":wx.WXK_F8,
"WXK_F9":wx.WXK_F9,
"WXK_F10":wx.WXK_F10,
"WXK_F11":wx.WXK_F11,
"WXK_F12":wx.WXK_F12,
"WXK_F13":wx.WXK_F13,
"WXK_F14":wx.WXK_F14,
"WXK_F15":wx.WXK_F15,
"WXK_F16":wx.WXK_F16,
"WXK_F17":wx.WXK_F17,
"WXK_F18":wx.WXK_F18,
"WXK_F19":wx.WXK_F19,
"WXK_F20":wx.WXK_F20,
"WXK_F21":wx.WXK_F21,
"WXK_F22":wx.WXK_F22,
"WXK_F23":wx.WXK_F23,
"WXK_F24":wx.WXK_F24,
"WXK_NUMLOCK":wx.WXK_NUMLOCK,
"WXK_SCROLL":wx.WXK_SCROLL,
"WXK_PAGEUP":wx.WXK_PAGEUP,
"WXK_PAGEDOWN":wx.WXK_PAGEDOWN,
"WXK_NUMPAD_SPACE":wx.WXK_NUMPAD_SPACE,
"WXK_NUMPAD_TAB":wx.WXK_NUMPAD_TAB,
"WXK_NUMPAD_ENTER":wx.WXK_NUMPAD_ENTER,
"WXK_NUMPAD_F1":wx.WXK_NUMPAD_F1,
"WXK_NUMPAD_F2":wx.WXK_NUMPAD_F2,
"WXK_NUMPAD_F3":wx.WXK_NUMPAD_F3,
"WXK_NUMPAD_F4":wx.WXK_NUMPAD_F4,
"WXK_NUMPAD_HOME":wx.WXK_NUMPAD_HOME,
"WXK_NUMPAD_LEFT":wx.WXK_NUMPAD_LEFT,
"WXK_NUMPAD_UP":wx.WXK_NUMPAD_UP,
"WXK_NUMPAD_RIGHT":wx.WXK_NUMPAD_RIGHT,
"WXK_NUMPAD_DOWN":wx.WXK_NUMPAD_DOWN,
# "WXK_NUMPAD_PRIOR":wx.WXK_NUMPAD_PRIOR,
"WXK_NUMPAD_PAGEUP":wx.WXK_NUMPAD_PAGEUP,
# "WXK_NUMPAD_NEXT":wx.WXK_NUMPAD_NEXT,
"WXK_NUMPAD_PAGEDOWN":wx.WXK_NUMPAD_PAGEDOWN,
"WXK_NUMPAD_END":wx.WXK_NUMPAD_END,
"WXK_NUMPAD_BEGIN":wx.WXK_NUMPAD_BEGIN,
"WXK_NUMPAD_INSERT":wx.WXK_NUMPAD_INSERT,
"WXK_NUMPAD_DELETE":wx.WXK_NUMPAD_DELETE,
"WXK_NUMPAD_EQUAL":wx.WXK_NUMPAD_EQUAL,
"WXK_NUMPAD_MULTIPLY":wx.WXK_NUMPAD_MULTIPLY,
"WXK_NUMPAD_ADD":wx.WXK_NUMPAD_ADD,
"WXK_NUMPAD_SEPARATOR":wx.WXK_NUMPAD_SEPARATOR,
"WXK_NUMPAD_SUBTRACT":wx.WXK_NUMPAD_SUBTRACT,
"WXK_NUMPAD_DECIMAL":wx.WXK_NUMPAD_DECIMAL,
"WXK_NUMPAD_DIVIDE":wx.WXK_NUMPAD_DIVIDE,
"WXK_WINDOWS_LEFT":wx.WXK_WINDOWS_LEFT,
"WXK_WINDOWS_RIGHT":wx.WXK_WINDOWS_RIGHT,
"WXK_WINDOWS_MENU":wx.WXK_WINDOWS_MENU,
"WXK_COMMAND":wx.WXK_COMMAND,
"WXK_SPECIAL1":wx.WXK_SPECIAL1,
"WXK_SPECIAL2":wx.WXK_SPECIAL2,
"WXK_SPECIAL3":wx.WXK_SPECIAL3,
"WXK_SPECIAL4":wx.WXK_SPECIAL4,
"WXK_SPECIAL5":wx.WXK_SPECIAL5,
"WXK_SPECIAL6":wx.WXK_SPECIAL6,
"WXK_SPECIAL7":wx.WXK_SPECIAL7,
"WXK_SPECIAL8":wx.WXK_SPECIAL8,
"WXK_SPECIAL9":wx.WXK_SPECIAL9,
"WXK_SPECIAL10":wx.WXK_SPECIAL10,
"WXK_SPECIAL11":wx.WXK_SPECIAL11,
"WXK_SPECIAL12":wx.WXK_SPECIAL12,
"WXK_SPECIAL13":wx.WXK_SPECIAL13,
"WXK_SPECIAL14":wx.WXK_SPECIAL14,
"WXK_SPECIAL15":wx.WXK_SPECIAL15,
"WXK_SPECIAL16":wx.WXK_SPECIAL16,
"WXK_SPECIAL17":wx.WXK_SPECIAL17,
"WXK_SPECIAL18":wx.WXK_SPECIAL18,
"WXK_SPECIAL19":wx.WXK_SPECIAL19,
"WXK_SPECIAL2":wx.WXK_SPECIAL2,
}
#func_list=[u'向上翻行',u'向下翻行',u'向上翻页',u'向下翻页',u'向上翻半页',u'向下翻半页',u'前进10%',u'后退10%',u'前进1%',u'后退1%',u'跳到首页',u'跳到结尾',u'文件列表',u'打开文件',u'另存为',u'关闭',u'上一个文件',u'下一个文件',u'搜索小说网站',u'搜索LTBNET',u'重新载入插件',u'选项',u'退出',u'拷贝',u'查找',u'查找下一个',u'查找上一个',u'替换',u'纸张显示模式',u'书本显示模式',u'竖排书本显示模式',u'显示工具栏',u'显示目录',u'全屏显示',u'显示文件侧边栏',u'自动翻页',u'智能分段',u'添加到收藏夹',u'整理收藏夹',u'简明帮助',u'版本更新内容',u'检查更新',u'关于',u'过滤HTML标记',u'切换为简体字',u'切换为繁体字',u'显示进度条',u'增大字体',u'减小字体',u'清空缓存',u'最小化',u'生成EPUB文件',u'启用WEB服务器',u'显示章节侧边栏',u'缩小工具栏',u'放大工具栏']

LB2_func_list={
u'向上翻行':'----+WXK_UP',
u'向下翻行':'----+WXK_DOWN',
u'向上翻页':'----+WXK_PAGEUP',
u'向上翻页':'----+WXK_LEFT',
u'向下翻页':'----+WXK_PAGEDOWN',
u'向下翻页':'----+WXK_RIGHT',
u'向下翻页':'----+WXK_SPACE',
u'向上翻半页':'----+","',
u'向下翻半页':'----+"."',
u'后退10%':'----+"["',
u'前进10%':'----+"]"',
u'后退1%':'----+"9"',
u'前进1%':'----+"0"',
u'跳到首页':'----+WXK_HOME',
u'跳到结尾':'----+WXK_END',
u'文件列表':'C---+"O"',
u'打开文件':'C---+"P"',
u'另存为':'C---+"S"',
u'关闭':'C---+"Z"',
u'上一个文件':'C---+"["',
u'下一个文件':'C---+"]"',
u'搜索小说网站':'-A--+"C"',
u'搜索LTBNET':'C---+"G"',
u'下载管理器':'C---+"D"',
u'重新载入插件':'C---+"R"',
u'选项':'-A--+"O"',
u'退出':'-A--+"X"',
u'拷贝':'C---+"C"',
u'查找':'C---+"F"',
u'替换':'C---+"H"',
u'查找下一个':'----+WXK_F3',
u'查找上一个':'----+WXK_F4',
u'纸张显示模式':'-A--+"M"',
u'书本显示模式':'-A--+"B"',
u'竖排书本显示模式':'-A--+"N"',
u'显示工具栏':'C---+"T"',
u'缩小工具栏':'C---+"-"',
u'放大工具栏':'C---+"="',
u'显示目录':'C---+"U"',
u'全屏显示':'C---+"I"',
u'显示文件侧边栏':'-A--+"D"',
u'显示章节侧边栏':'-A--+"J"',
u'自动翻页':'-A--+"T"',
u'智能分段':'-A--+"P"',
u'添加到收藏夹':'C---+"D"',
u'整理收藏夹':'C---+"M"',
u'简明帮助':'----+WXK_F1',
u'版本更新内容':'----+WXK_F2',
u'检查更新':'----+WXK_F5',
u'关于':'----+WXK_F6',
u'过滤HTML标记':'----+WXK_F9',
u'切换为简体字':'----+WXK_F7',
u'切换为繁体字':'----+WXK_F8',
u'显示进度条':'----+"Z"',
u'增大字体':'----+"="',
u'减小字体':'----+"-"',
u'清空缓存':'CA--+"Q"',
u'最小化':'----+WXK_ESCAPE',
u'生成EPUB文件':'C---+"E"',
u'启用WEB服务器':'-A--+"W"',
u'检测端口是否开启':'C---+"Q"',
u'使用UPNP添加端口映射':'C---+"I"',
u'管理订阅':'C---+"Y"',
}

func_list = LB2_func_list.keys()


def str2menu(keystr):
    mstr=' \t'
    mod,keysub=keystr.split('+',1)
    if mod[0]<>'-':mstr+='CTRL+'
    if mod[1]<>'-':mstr+='ALT+'
    if mod[2]<>'-':mstr+='SHIFT+'
    if mod[3]<>'-':mstr+='META+'
    if keysub[0]=='"':
        mstr+=keysub[1]
    else:
        mstr+=keysub[4:]
    return mstr



def str2key(keystr):
    rkey={}
    rkey['ALT']=False
    rkey['CTRL']=False
    rkey['SHIFT']=False
    rkey['META']=False
    rkey['KEY']=0
    mod,keysub=keystr.split('+',1)
    if mod[0]<>'-':rkey['CTRL']=True
    if mod[1]<>'-':rkey['ALT']=True
    if mod[2]<>'-':rkey['SHIFT']=True
    if mod[3]<>'-':rkey['META']=True
    if keysub[0]=='"':

        rkey['KEY']=ord(keysub[1])
    else:
        rkey['KEY']=RKeyMap[keysub]
    return rkey


def key2str(evt):
    global KeyMap
    keycode=evt.GetKeyCode()
    modifiers = ""
    for mod, ch in [(evt.ControlDown(), 'C'),
                    (evt.AltDown(),     'A'),
                    (evt.ShiftDown(),   'S'),
                    (evt.MetaDown(),    'M')]:
        if mod:
            modifiers += ch
        else:
            modifiers += '-'
    keyname = KeyMap.get(keycode, None)
    if keyname is None:
        if keycode < 256:
            if keycode == 0:
                keyname = "NUL"
            elif keycode < 27:
                keyname = "\"%s\"" % chr(ord('A') + keycode-1).upper()
            else:
                keyname = "\"%s\"" % chr(keycode).upper()
        else:
            keyname = "(%s)" % keycode
    return modifiers+"+"+keyname





class KeyConfigGrid(gridlib.Grid):
    def __init__(self,parent):


        gridlib.Grid.__init__(self,parent,name='OptionGrid')
        self.curCol=None
        self.curRow=None
        self.startKey=False
        self.startKeyCell=''
        self.tRow=None
        self.CreateGrid(0, 2)
        self.SetColLabelValue(0, u"功能(双击修改)")
        self.SetColLabelValue(1, u"按键(双击修改)")
#        self.Bind(wx.EVT_CHAR,self.OnChar)
        self.GetGridWindow().Bind(wx.EVT_CHAR,self.OnChar)
        self.Bind(wx.EVT_KEY_UP,self.OnChar)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK,self.OnDClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK,self.OnLClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.Popmenu)


    def OnLClick(self,evt):

        if self.curCol<>None and self.startKey:
            self.SetCellValue(self.curRow,self.curCol,self.startKeyCell)
        evt.Skip()
##        else:
##            evt.Skip()



    def OnDClick(self,evt):
        col=evt.GetCol()
        if self.curCol<>None and self.startKey:
            self.SetCellValue(self.curRow,self.curCol,self.startKeyCell)
        if col<>1:
            evt.Skip()
            return
        r=evt.GetRow()
        self.curCol=col
        self.curRow=r
        self.startKeyCell=self.GetCellValue(r,1)
        self.SetCellValue(r,1,u'请按键...')
        self.startKey=True


    def Popmenu(self,evt):
        if not hasattr(self,"popupID1"):
            self.popupID1=wx.NewId()
            self.popupID2=wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnDel, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnAdd, id=self.popupID2)
        self.tRow=evt.GetRow()
        menu = wx.Menu()
        item = wx.MenuItem(menu, self.popupID1,u"删除本行")
        menu.AppendItem(item)
        item = wx.MenuItem(menu, self.popupID2,u"新增一行")
        menu.AppendItem(item)
        self.PopupMenu(menu)
        #menu.Destroy()

    def OnDel(self,evt):

        self.DeleteRows(self.tRow)
        if self.GetNumberRows()==0:self.OnAdd(None)

    def OnAdd(self,evt):
        self.AppendLine(u'向下翻页','')
        r=self.GetNumberRows()
        self.SelectRow(r-1)



    def OnChar(self,evt):
        global key2str,str2key
        if not self.startKey:
            evt.Skip()
            return
        r=key2str(evt)
        key=str2key(r)['KEY']
        n=self.GetNumberRows()
        i=0
        while i<n:
            if i<>self.curRow:
                if self.GetCellValue(i,1)==r:
                    func_name=self.GetCellValue(i,0)
                    dlg = wx.MessageDialog(None, u'"'+func_name+u'" 已经使用了这个按键，请换一个',u"错误！",wx.OK|wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.SetCellValue(self.curRow,self.curCol,self.startKeyCell)
                    self.startKey=False
                    return
            i+=1
        self.SetCellValue(self.curRow,self.curCol,r)
        evt.Skip(False)
        evt.StopPropagation()
        self.startKey=False

        #self.AppendLine(u'上一个文件',r)


    def AppendLine(self,func,key):
        global func_list
        if func not in func_list:return False
        self.AppendRows()
        r=self.GetNumberRows()
        self.SetCellEditor(r-1,0,gridlib.GridCellChoiceEditor(func_list))
#        cedit=KeyEditor()
#        self.SetCellEditor(r-1,1,cedit)
#        self.SetCellEditor(r-1,1,mycell())
        self.SetCellValue(r-1,0,func)
        self.SetCellValue(r-1,1,key)
        self.SetReadOnly(r-1,1)
        self.MakeCellVisible(r-1,0)




    def Load(self,klist):
        r=self.GetNumberRows()
        if r>0:self.DeleteRows(0,r)

        i=1
        tl=len(klist)
        while i<tl:
            self.AppendLine(klist[i][0],klist[i][1])
            i+=1
        if tl==0:self.OnAdd(None)
        if r==0:self.AutoSize()
        self.MakeCellVisible(0,0)






class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.grid_1 = KeyConfigGrid(self)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("frame_1")
        self.grid_1.AppendLine(u'上一个文件','1')
        self.grid_1.AppendLine(u'上一个文件','2')
        self.grid_1.AppendLine(u'上一个文件','3')

        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_26 = wx.BoxSizer(wx.VERTICAL)
        sizer_26.Add(self.grid_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_26)
        sizer_26.Fit(self)
        self.Layout()
        # end wxGlade

# end of class MyFrame


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
