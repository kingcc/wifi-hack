#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Start:
#   $ sudo apt-get install wireless-tools python-pip
#   $ sudo pip install requests pycrypto
# 
# Usage:
#   ./wifi_hack.py -h
#   
# Author:
#   <md5_salt [AT] qq.com> 
#        https://github.com/5alt/lianwifi
#   <root@kings-way.info> 
#       https://github.com/kings-way/WiFi-MasterKey-in-Linux
#   <laikinfox@gmail.com> 
#       https://github.com/kingcc/wifi-hack   

import md5
from Crypto.Cipher import AES
import requests
import random
import re
import commands
import time
import sys
import os
import getopt
reload(sys)
sys.setdefaultencoding('utf-8')

class wifi:
    aesKey = 'k%7Ve#8Ie!5Fb&8E'
    aesIV = 'y!0Oe#2Wj#6Pw!3V'
    aesMode = AES.MODE_CBC

    dhid = ''
    mac = ''
    ii = ''

    salt = ''#from server

    def __init__(self):
            self.RegisterNewDevice()

    def __sign(self, data, salt):
            request_str = ''
            for key in sorted(data):
                    request_str += data[key]
            return md5.md5(request_str + salt).hexdigest().upper()

    def __decrypt(self, ciphertext):
            #[length][password][timestamp]
            decryptor = AES.new(self.aesKey, self.aesMode, IV=self.aesIV)
            return decryptor.decrypt(ciphertext.decode('hex')).strip()[3:-13]

    def RegisterNewDevice(self):
            salt = '1Hf%5Yh&7Og$1Wh!6Vr&7Rs!3Nj#1Aa$'
            data = {}
            data['appid'] = '0008'
            data['chanid'] = 'gw'
            data['ii'] = md5.md5(str(random.randint(1,10000))).hexdigest()
            data['imei'] = data['ii']
            data['lang'] = 'cn'
            data['mac'] = data['ii'][:12]#md5.md5(str(random.randint(1,10000))).hexdigest()[:12]
            data['manuf'] = 'Apple'
            data['method'] = 'getTouristSwitch'
            data['misc'] = 'Mac OS'
            data['model'] = '10.10.3'
            data['os'] = 'Mac OS'
            data['osver'] = '10.10.3'
            data['osvercd'] = '10.10.3'
            data['pid'] = 'initdev:commonswitch'
            data['scrl'] = '813'
            data['scrs'] = '1440'
            data['wkver'] = '324'
            data['st'] = 'm'
            data['v'] = '324'
            data['sign'] = self.__sign(data, salt)

            url = 'http://wifiapi02.51y5.net/wifiapi/fa.cmd'

            useragent = 'WiFiMasterKey/1.1.0 (Mac OS X Version 10.10.3 (Build 14D136))'
            headers = {'User-Agent': useragent}

            r = requests.post(url, data=data, headers=headers).json()

            if r['retCd'] == '0' and r['initdev']['retCd'] == '0':
                    self.imei = data['imei']
                    self.ii = data['ii']
                    self.mac = data['mac']
                    self.dhid = r['initdev']['dhid']
                    self.salt = salt
                    return True
            else:
                    return False

    def __query(self, ssid, bssid):
            data = {}
            data['appid'] = '0008'
            data['bssid'] = ','.join(bssid)
            data['chanid'] = 'gw'
            data['dhid'] = self.dhid
            data['ii'] = self.ii
            data['lang'] = 'cn'
            data['mac'] = self.mac
            data['method'] = 'getSecurityCheckSwitch'
            data['pid'] = 'qryapwithoutpwd:commonswitch'
            data['ssid'] = ','.join(ssid)
            data['st'] = 'm'
            data['uhid'] = 'a0000000000000000000000000000001'
            data['v'] = '324'
            data['sign'] = self.__sign(data, self.salt)

            url = 'http://wifiapi02.51y5.net/wifiapi/fa.cmd'

            useragent = 'WiFiMasterKey/1.1.0 (Mac OS X Version 10.10.3 (Build 14D136))'
            headers = {'User-Agent': useragent}

            r = requests.post(url, data=data, headers=headers).json()

            self.salt = r['retSn']

            if r['retCd'] == '-1111':
                    return self.__request(ssid, bssid)#maybe some problem

            ret = {}
            ret['flag'] = False
            ret['ssid'] = []
            ret['bssid'] = []

            if r['retCd'] == '0':
                    if r['qryapwithoutpwd']['retCd'] == '0':
                            for d in r['qryapwithoutpwd']['psws']:
                                    wifi = r['qryapwithoutpwd']['psws'][d]
                                    if wifi['bssid'] in bssid:
                                            ret['ssid'].append(wifi['ssid'])
                                            ret['bssid'].append(wifi['bssid'])
                            ret['flag'] = True
                    else:
                            ret['msg'] = r['qryapwithoutpwd']['retMsg']
            else:
                    ret['msg'] = r['retMsg']
            return ret


    def query(self, ssid, bssid):
            wifi = self.__query(ssid, bssid)
            if wifi['flag']:
                    ret = '+' + '-'*18 + '+' + '\n'
                    for i in xrange(len(wifi['ssid'])):
                            time.sleep(2)
                            rsp = self.__request(wifi['ssid'][i], wifi['bssid'][i])
                            if rsp['flag']:
                                    del rsp['flag']
                                    del rsp['msg']
                                    ret += '\n'.join([x + ' : ' + str(rsp[x]) for x in rsp])
                                    ret += '\n' + '+' + '-'*18 + '+' + '\n'
                    print ret
            else:
                    print wifi['msg']

    def queryall(self, ssid, bssid):
            wifi = self.__query(ssid, bssid)
            if wifi['flag']:
                    ret = '+' + '-'*18 + '+' + '\n'
                    for i in xrange(len(wifi['ssid'])):
                            time.sleep(2)
                            rsp = self.__request(wifi['ssid'][i], wifi['bssid'][i])
                            if rsp['flag']:
                                    del rsp['flag']
                                    del rsp['msg']
                                    ret += '\n'.join([x + ' : ' + str(rsp[x]) for x in rsp])
                                    ret += '\n' + '+' + '-'*18 + '+' + '\n'
                            else:
                                    del rsp['flag']
                                    ret += '\n'.join([x + ' : ' + str(rsp[x]) for x in rsp])
                                    ret += '\n' + '+' + '-'*18 + '+' + '\n'
                    print ret
            else:
                    print wifi['msg']


    def __request(self, ssid, bssid):
            data = {}
            data['appid'] = '0008'
            data['bssid'] = bssid
            data['chanid'] = 'gw'
            data['dhid'] = self.dhid
            data['ii'] = self.ii
            data['lang'] = 'cn'
            data['mac'] = self.mac
            data['method'] = 'getDeepSecChkSwitch'
            data['pid'] = 'qryapwd:commonswitch'
            data['ssid'] = ssid
            data['st'] = 'm'
            data['uhid'] = 'a0000000000000000000000000000001'
            data['v'] = '324'
            data['sign'] = self.__sign(data, self.salt)

            url = 'http://wifiapi02.51y5.net/wifiapi/fa.cmd'

            useragent = 'WiFiMasterKey/1.1.0 (Mac OS X Version 10.10.3 (Build 14D136))'
            headers = {'User-Agent': useragent}

            r = requests.post(url, data=data, headers=headers).json()

            self.salt = r['retSn']

            if r['retCd'] == '-1111':
                    return self.__request(ssid, bssid)#maybe some problem

            ret = {}
            ret['flag'] = False
            ret['msg'] = 'empty'
            ret['ssid'] = ssid
            ret['bssid'] = bssid
            if r['retCd'] == '0':
                    if r['qryapwd']['retCd'] == '0':
                            for d in r['qryapwd']['psws']:
                                    wifi = r['qryapwd']['psws'][d]
                                    if wifi['pwd']:
                                            ret['pwd'] = self.__decrypt(wifi['pwd'])
                                            ret['flag'] = True
                                    if wifi['xUser']:
                                            ret['xUser'] = wifi['xUser']
                                            ret['xPwd'] = ['xPwd']
                                            ret['flag'] = True
                    elif r['qryapwd']['retCd'] == '-9998':
                            time.sleep(5)
                            return self.__request(ssid, bssid)#maybe some problem
                    else:
                            ret['msg'] = r['qryapwd']['retCd'] + ': ' + r['qryapwd']['retMsg']
            else:
                    ret['msg'] = r['retCd'] + ': ' + r['retMsg']

            return ret

    def request(self, ssid, bssid):
            wifi = self.__request(ssid, bssid)
            if wifi['flag']:
                    del wifi['flag']
                    del wifi['msg']
                    ret = '+' + '-'*18 + '+' + '\n'
                    ret += '\n'.join([x + ' : ' + str(wifi[x]) for x in wifi])
                    ret += '\n' + '+' + '-'*18 + '+' + '\n'
                    print ret
            else:
                    print wifi['msg']

def autoscan():
    wlan=commands.getoutput('ifconfig | grep wl').split(' ')[0]
    scanStr='iwlist '+wlan+' scan | grep -E "Addr|ESSID|level"| cut -c 21-'
    scan=commands.getoutput(scanStr)

#    BSSID=re.findall('(([0-9A-F]{2}:){5}[0-9A-F]{2})',scan)
#   No idea about why this regular expression doesn't work
    BSSID=re.findall('[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}',scan)
    ESSID=re.findall('(?<=").*(?=")',scan)
    dBm=re.findall('[-]\d+ dBm',scan)

    print "====================="
    print "  ",len(BSSID),"APs detected..."
    print "====================="
    i=0
    while(i<len(BSSID)):
        print i+1," ",dBm[i],"\t",BSSID[i],"\t",ESSID[i]
        i=i+1
    
    print "\n"
    print "====================="
    print " Passwords cracked..."
    print "====================="
    wifi().query(ESSID,BSSID)

def help_usage():
    print "====================="
    print "Usage:"
    print "   ./wifi_hack.py    \t\trun automaticly  "
    print "   ./wifi_hack.py  [ESSID] [BSSID]\tquery the specific ssid"
    print "   ./wifi_hack.py  -h\t\tshow this help info"
    print "====================="
            
if __name__ == '__main__':
    
    len_argv=len(sys.argv)
    if len_argv == 1:
        autoscan()

    elif len_argv == 2:
        options,args=getopt.getopt(sys.argv[1:],"h")
        for opt,value in options:
            if opt == "-h":
                help_usage()
    
    elif len_argv == 3:
        ESSID=[]
        BSSID=[]
        ESSID.append(sys.argv[1])
        BSSID.append(sys.argv[2])
        wifi().query(ESSID,BSSID)

    else:
        help_usage()