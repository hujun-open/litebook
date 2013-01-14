#-------------------------------------------------------------------------------
# Name:        A UPNP Client to add port forward mapping on 1st respond router
# Purpose:
#
# Author:      Hu Jun
#
# Created:     23/12/2012
# Copyright:   (c) Hu Jun 2012
# Licence:     GPLv2
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import socket
import struct
import time
import urllib2
from StringIO import StringIO
from httplib import HTTPResponse
from xml.dom import minidom
from urlparse import urlparse
import re
import traceback
import netifaces

def insubnet(ip1,mask1,ip2):
    """
    return True if ip2 is in ip1's subnet
    """
    bs1 = socket.inet_aton(ip1)
    bs2 = socket.inet_aton(ip2)
    mask = socket.inet_aton(mask1)
    subnet1=''
    for n in range(4):
        subnet1+=chr(ord(bs1[n]) & ord(mask[n]))
    subnet2=''
    for n in range(4):
        subnet2+=chr(ord(bs2[n]) & ord(mask[n]))
    if subnet1 == subnet2:
        return True
    else:
        return False

def getDRIntIP(gwip):
    """
    return the 1st interface ip that in the the same subnet of gwip
    """
    for ifname in netifaces.interfaces(): #return addr of 1st network interface
        if 2 in netifaces.ifaddresses(ifname):
            if_addr = netifaces.ifaddresses(ifname)[2][0]['addr']
            if if_addr != '127.0.0.1' and if_addr != None and if_addr != '':
                if_mask = netifaces.ifaddresses(ifname)[2][0]['netmask']
                if insubnet(if_addr,if_mask,gwip) == True:
                    return if_addr
    return False

def checkLocalIP(cip):
    """
    check if the cip is within the same subnet of any local address
    """
    if cip == '127.0.0.1':return True
    for ifname in netifaces.interfaces():
        if 2 in netifaces.ifaddresses(ifname):
            if_addr = netifaces.ifaddresses(ifname)[2][0]['addr']
            if if_addr != '127.0.0.1' and if_addr != None and if_addr != '':
                if_mask = netifaces.ifaddresses(ifname)[2][0]['netmask']
                if insubnet(if_addr,if_mask,cip) == True:
                    return True
    return False


class FakeSocket(StringIO):
    def makefile(self, *args, **kw):
        return self

def httpparse(fp):
    socket = FakeSocket(fp.read())
    response = HTTPResponse(socket)
    response.begin()
    return response

#sendSOAP is based on part of source code from miranda-upnp.
def sendSOAP(hostName,serviceType,controlURL,actionName,actionArguments):
        argList = ''
        soapResponse = ''

        if '://' in controlURL:
                urlArray = controlURL.split('/',3)
                if len(urlArray) < 4:
                        controlURL = '/'
                else:
                        controlURL = '/' + urlArray[3]


        soapRequest = 'POST %s HTTP/1.1\r\n' % controlURL

        #Check if a port number was specified in the host name; default is port 80
        if ':' in hostName:
                hostNameArray = hostName.split(':')
                host = hostNameArray[0]
                try:
                        port = int(hostNameArray[1])
                except:
                        print 'Invalid port specified for host connection:',hostName[1]
                        return False
        else:
                host = hostName
                port = 80

        #Create a string containing all of the SOAP action's arguments and values
        for arg,(val,dt) in actionArguments.iteritems():
                argList += '<%s>%s</%s>' % (arg,val,arg)

        #Create the SOAP request
        soapBody =      '<?xml version="1.0"?>\n'\
                        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n'\
                        '<SOAP-ENV:Body>\n'\
                        '\t<m:%s xmlns:m="%s">\n'\
                        '%s\n'\
                        '\t</m:%s>\n'\
                        '</SOAP-ENV:Body>\n'\
                        '</SOAP-ENV:Envelope>' % (actionName,serviceType,argList,actionName)

        #Specify the headers to send with the request
        headers =       {
                        'Host':hostName,
                        'Content-Length':len(soapBody),
                        'Content-Type':'text/xml',
                        'SOAPAction':'"%s#%s"' % (serviceType,actionName)
                        }

        #Generate the final payload
        for head,value in headers.iteritems():
                soapRequest += '%s: %s\r\n' % (head,value)
        soapRequest += '\r\n%s' % soapBody

        #Send data and go into recieve loop
        try:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.connect((host,port))

##                if self.DEBUG:
##                        print self.STARS
##                        print soapRequest
##                        print self.STARS
##                        print ''

                sock.send(soapRequest)
                while True:
                        data = sock.recv(8192)
                        if not data:
                                break
                        else:
                                soapResponse += data
                                if re.compile('<\/.*:envelope>').search(soapResponse.lower()) != None:
                                        break
                sock.close()
                (header,body) = soapResponse.split('\r\n\r\n',1)
                if not header.upper().startswith('HTTP/1.') or not ' 200 ' in header.split('\r\n')[0]:
                    raise RuntimeError('SOAP request failed with error code:',header.split('\r\n')[0].split(' ',1)[1])
##                        errorMsg = self.extractSingleTag(body,'errorDescription')
##                        if errorMsg:
##                                print 'SOAP error message:',errorMsg
##                        return False
                else:
                        return body
        except Exception, e:
                print 'Caught socket exception:',e
                print traceback.format_exc()
                sock.close()
                return False
        except KeyboardInterrupt:
                print ""
                sock.close()
                return False

#def changePortMapping(PM_proto,internal_port,external_port,PM_desc="",method='add'):
def changePortMapping(mapping_list,method='add'):
    """
    add or remove PortMapping on 1st respond router via UPNP
    mapping_list is a list of dict:
        {'desc':str,'port':int,'proto':str}
    method: 'add' or 'remove'
    note: the internal ip is auto-detected via:
        - find the 1st interface address that are in the same subnet of
            upnp-server's addr
    """
    up_disc='M-SEARCH * HTTP/1.1\r\nHOST:239.255.255.250:1900\r\nST:upnp:rootdevice\r\nMX:2\r\nMAN:"ssdp:discover"\r\n\r\n'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.bind(('',1910))
    sock.sendto(up_disc, ("239.255.255.250", 1900))
    sock.settimeout(3.0)
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    internal_ip = getDRIntIP(addr[0])
##    print "internal_ip is ",internal_ip
##    print "received message:", data
    descURL=httpparse(StringIO(data)).getheader('location')
##    print "descURL is ",descURL
    descXMLs=urllib2.urlopen(descURL).read()
    pr=urlparse(descURL)
    baseURL=pr.scheme+"://"+pr.netloc
##    print descXMLs
    dom=minidom.parseString(descXMLs)
    ctrlURL=None
    for e in dom.getElementsByTagName('service'):
        stn=e.getElementsByTagName('serviceType')
        if stn != []:
            if stn[0].firstChild.nodeValue == 'urn:schemas-upnp-org:service:WANIPConnection:1':
                cun=e.getElementsByTagName('controlURL')
                ctrlURL=baseURL+cun[0].firstChild.nodeValue
                break
##    print "ctrlURL is ",ctrlURL
    if ctrlURL != None:
        for mapping in mapping_list:
            if method=='add':
                upnp_method='AddPortMapping'
                sendArgs = {'NewPortMappingDescription': (mapping['desc'], 'string'),
        			'NewLeaseDuration': ('0', 'ui4'),
        			'NewInternalClient': (internal_ip, 'string'),
        			'NewEnabled': ('1', 'boolean'),
        			'NewExternalPort': (mapping['port'], 'ui2'),
        			'NewRemoteHost': ('', 'string'),
        			'NewProtocol': (mapping['proto'], 'string'),
        			'NewInternalPort': (mapping['port'], 'ui2')}
            else:
                upnp_method='DeletePortMapping'
                sendArgs = {
        			'NewExternalPort': (mapping['port'], 'ui2'),
        			'NewRemoteHost': ('', 'string'),
        			'NewProtocol': (mapping['proto'], 'string'),}

            sendSOAP(pr.netloc,'urn:schemas-upnp-org:service:WANIPConnection:1',
                        ctrlURL,upnp_method,sendArgs)



if __name__ == '__main__':
    changePortMapping([{'port':50210,'proto':'UDP','desc':"testFromScript"}],'add')


