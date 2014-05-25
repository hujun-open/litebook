#!/usr/bin/env py32
# -*- coding: utf-8 -*-
#
import codecs

jfdb=codecs.open('jf.dat','r','utf-8')
j2f=f2j={}
for line in jfdb:
    j,f=line.strip().split()
    j2f[j]=f
    f2j[f]=j


j2ftable = dict((ord(char),j2f[char]) for char in j2f.keys())
f2jtable = dict((ord(char),f2j[char]) for char in f2j.keys())

def jtof(instr):
    """
    instr must be unicode
    """
    return instr.translate(j2ftable)

def ftoj(instr):
    """
    instr must be unicode
    """
    return instr.translate(f2jtable)


