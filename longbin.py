#-------------------------------------------------------------------------------
# Name:        LongBin
# Purpose:      For long binary number manipulation
#
# Author:      Hu Jun
#
# Created:     16/09/2011
# Copyright:   (c) Hu Jun 2011
# Licence:     GPLv3
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import hashlib
import struct


class LongBin:
    """This class represent a long number, bigger than long type number
    self.val: str that store the value
    self.nlen: self.val length in bytes
    """
    def __init__(self,copyval=None,nlen=20,binstr=None):
        """
        binstr's format is "01010101000..."
        copyval is actuall binary str
        if binstr is not spcified, then use copyval;
        otherwise covert binstr(1010101..)
        """
        if binstr == None:
            if isinstance(copyval,str) and copyval<>None:
                if len(copyval)<>nlen:
                    raise ValueError('the length of copyval doesnt equal to '
                                            +str(nlen))
            else:
                raise TypeError('copyval must be a str')

            self.val = copyval
            self.nlen=nlen
        else:
            blen=len(binstr)
            if blen % 8 != 0:
                raise ValueError("the len of binstr must be times of 8")
            self.nlen=blen/8
            self.val=''
            for i in range(self.nlen):
                self.val+=chr(int(binstr[i*8:i*8+8],2))


    def __xor__(self,b):
        i=0
        rstr=''
        if self.nlen<>b.nlen:
            raise ValueError("these two LongBin have different length")

        while i<self.nlen:
            x=ord(self.val[i])
            y=ord(b.val[i])
            z=x^y
            rstr+=chr(z)
            i+=1
        return LongBin(rstr,self.nlen)

    def __eq__(self,b):
        if self.nlen<>b.nlen:
            return False
        if self.val<>b.val:
            return False
        return True

    def __ne__(self,b):
        if type(self)<>type(b):
            return True
        if self.nlen<>b.nlen:
            return True
        if self.val<>b.val:
            return True
        return False

    def __gt__(self,b):
        i=0
        while i<self.nlen:
            if ord(self.val[i])>ord(b.val[i]):
                return True
            elif ord(self.val[i])<ord(b.val[i]):
                return False
            i+=1
        return False

    def __ge__(self,b):
        i=0
        while i<self.nlen:
            if ord(self.val[i])>ord(b.val[i]):
                return True
            elif ord(self.val[i])<ord(b.val[i]):
                return False
            i+=1
        return True

    def __lt__(self,b):
        i=0
        while i<self.nlen:
            if ord(self.val[i])>ord(b.val[i]):
                return False
            elif ord(self.val[i])<ord(b.val[i]):
                return True
            i+=1
        return False

    def __le__(self,b):
        i=0
        while i<self.nlen:
            if ord(self.val[i])>ord(b.val[i]):
                return False
            elif ord(self.val[i])<ord(b.val[i]):
                return True
            i+=1
        return True

    def __str__(self):
        """ convert val to string of 1010101..."""
        i=0
        rstr=''
        while i<self.nlen:
            rstr+='{0:08b}'.format(ord(self.val[i]))
            i+=1
        return rstr

    def hexstr(self):
        return "0x"+self.val.encode('hex_codec')






if __name__ == '__main__':
    h1=hashlib.sha1()
    h2=hashlib.sha1()
    h1.update('1')
    h2.update('2')
    x=LongBin(h1.digest())
    y=LongBin(h2.digest())

    print x
    print y
    print x^y

    print x>=y








