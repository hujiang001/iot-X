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

import time
import util

LOG_LEVEL_MSG = 0x1
LOG_LEVEL_INFO = 0x2
LOG_LEVEL_WARN = 0x4
LOG_LEVEL_ERR = 0x8
LOG_LEVEL_FATAL = 0x10
__fp__ = None
__switch__ = 0xffffffff

def __logInit():
    global __fp__
    import configure,os
    logDir = configure.path_root + '/log/'
    if not os.path.exists(logDir):
        os.mkdir(logDir)
    timeFormat = "%Y%m%d%H%M%S"
    fileName = time.strftime(timeFormat, time.localtime())
    __fp__ = open(logDir+fileName+'.log','w')
    if (0 == __fp__):
        util.safeExit()

def logPrint(level, str):
    BG = '\033[40m'
    BBG = '\033[37m'
    CORLOR_RED = '\033[91m'
    CORLOR_YELLOW = '\033[93m'
    CORLOR_BLACK = '\033[90m'
    CORLOR_GREEN = '\033[92m'
    ENDC = '\033[0m'
    global __fp__,__switch__
    if __fp__ is None:
        __logInit()

    if (LOG_LEVEL_INFO == level):
        levelStr = "INFO   "
        corlor = CORLOR_BLACK
    elif (LOG_LEVEL_WARN == level):
        levelStr = "WARNING"
        corlor = CORLOR_YELLOW
    elif (LOG_LEVEL_ERR == level):
        levelStr = "ERROR  "
        corlor = CORLOR_RED
    elif (LOG_LEVEL_FATAL == level):
        levelStr = "FATAL  "
        corlor = CORLOR_RED
    elif (LOG_LEVEL_MSG == level):
        levelStr = "MSG    "
        corlor = CORLOR_GREEN
    else:
        return
    __fp__.writelines("["+levelStr+"] "+str+"\r")
    __fp__.flush()
    if __switch__&level == level:
        print BG+BBG+corlor+"["+levelStr+"] "+str+ENDC

def logFatal(str):
    logPrint(LOG_LEVEL_FATAL,str)

def logError(str):
    logPrint(LOG_LEVEL_ERR,str)

def logWarning(str):
    logPrint(LOG_LEVEL_WARN,str)

def logInfo(str):
    logPrint(LOG_LEVEL_INFO,str)

def logMsg(str):
    logPrint(LOG_LEVEL_MSG,str)

def logSwitch(s):
    global __switch__
    if s == 'close':
        __switch__ = 0
    elif s == 'msg':
        __switch__ |= LOG_LEVEL_MSG
    elif s == 'info':
        __switch__ |= LOG_LEVEL_INFO
    elif s == 'warning':
        __switch__ |= LOG_LEVEL_WARN
    elif s == 'error':
        __switch__ |= LOG_LEVEL_ERR
    elif s == 'fatal':
        __switch__ |= LOG_LEVEL_FATAL
    elif s == 'all':
        __switch__ = 0xffffffff
    elif s == 'show':
        print "debug show switch is: "+str(__switch__)
    else:
        return
    return
