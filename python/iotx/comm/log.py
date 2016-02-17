"""
logClass is a singleto class
"""
import time

import iotx.comm.util as util


class logClass():
    _fp = 0
    _LOG_MSG_ = 0x1
    _LOG_INFO_ = 0x2
    _LOG_WARN_ = 0x4
    _LOG_ERR_ = 0x8
    _LOG_FATAL_ = 0x10

    BG = '\033[40m'
    BBG = '\033[37m'
    CORLOR_RED = '\033[91m'
    CORLOR_YELLOW = '\033[93m'
    CORLOR_BLACK = '\033[90m'
    CORLOR_GREEN = '\033[92m'
    ENDC = '\033[0m'

    _PRINT_SWITCH_ = 0xffffffff

    def __init__(self):
        timeFormat = "%Y%m%d%H%M%S"
        fileName = time.strftime(timeFormat, time.localtime())
        self._fp = open('../../log/'+fileName+'.log','w')
        if (0 == self._fp):
            util.safeExit()
        self.p(self._LOG_INFO_,"log module init success...")
    def p(self,level,str):
        if (self._LOG_INFO_ == level):
            levelStr = "INFO   "
            corlor = self.CORLOR_BLACK
        elif (self._LOG_WARN_ == level):
            levelStr = "WARNING"
            corlor = self.CORLOR_YELLOW
        elif (self._LOG_ERR_ == level):
            levelStr = "ERROR  "
            corlor = self.CORLOR_RED
        elif (self._LOG_FATAL_ == level):
            levelStr = "FATAL  "
            corlor = self.CORLOR_RED
        elif (self._LOG_MSG_ == level):
            levelStr = "MSG    "
            corlor = self.CORLOR_GREEN
        else:
            return
        self._fp.writelines("["+levelStr+"] "+str+"\r")
        self._fp.flush()
        if self._PRINT_SWITCH_&level == level:
             print self.BG+self.BBG+corlor+"["+levelStr+"] "+str+self.ENDC
    def switch(self, paras):
        if len(paras) <=0:
            return;
        s = paras[0]
        if s == 'close':
            self._PRINT_SWITCH_ = 0
        elif s == 'msg':
            self._PRINT_SWITCH_ |= self._LOG_MSG_
        elif s == 'info':
            self._PRINT_SWITCH_ |= self._LOG_INFO_
        elif s == 'warning':
            self._PRINT_SWITCH_ |= self._LOG_WARN_
        elif s == 'error':
            self._PRINT_SWITCH_ |= self._LOG_ERR_
        elif s == 'fatal':
            self._PRINT_SWITCH_ |= self._LOG_FATAL_
        elif s == 'all':
            self._PRINT_SWITCH_ = 0xffffffff
        elif s == 'show':
            print "debug show switch is: "+str(self._PRINT_SWITCH_)
        else:
            return
        return

iotxLog = logClass()