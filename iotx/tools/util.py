#!usr/bin/env python
#-*-coding=utf8-*-
"""
Author: hujiang001@gmail.com
ChangeLog: 2016-02-19 created

LICENCE: The MIT License (MIT)

Copyright (c) [2016] [iotX]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import random,string,os
import log,error

def safeExit():
    log.logFatal("iotX terminaed for fatal error, please check the log file for the reason")
    try:
        os._exit(0)
    except:
        pass

def checkIp(ipaddr):
        addr=ipaddr.strip().split('.')
        if len(addr) != 4:
                return error.ERR_CODE_ERR_
        for i in range(4):
                try:
                        addr[i]=int(addr[i])
                except:
                        return error._ERR_CODE_ERR_
                if addr[i]<=255 and addr[i]>=0:
                        pass
                else:
                        return error._ERR_CODE_ERR_
                i+=1
        return error._ERR_CODE_OK_

def checkPort(port):
    try:
        myPort=int(port)
    except:
        return error._ERR_CODE_ERR_
    if myPort<=65535 and myPort>=0:
        pass
    else:
        return error._ERR_CODE_ERR_
    return error._ERR_CODE_OK_