#-*-coding=utf8-*-
import random,string,os

import iotx.comm.log

#error code
_ERR_CODE_UPDATE_ = 1
_ERR_CODE_OK_ = 0
_ERR_CODE_ERR_ = -1
_ERR_CODE_REGKEY_INVALID_ = -2
_ERR_CODE_NAME_CONFLICT_ = -3
_ERR_CODE_TYPE_INVALID_ = -4
_ERR_CODE_FSM_NOTREADY_ = -5
_ERR_CODE_CTRL_CLOSE_ = -6
_ERR_CODE_MSG_FORMAT_INVALID_ = -7
_ERR_CODE_EQUIPMENT_NOT_EXSIT_ = -8
_ERR_CODE_UNSUPPORTED_EVENT_ = -9
_ERR_CODE_CALLBACK_NOT_REG_ = -10
_ERR_CODE_USERNAME_NOT_EXSIT_ = -11
_ERR_CODE_USERPWD_WRONG_ = -12
_ERR_CODE_USER_ALREADY_LOGIN_ = -13
_ERR_CODE_INVALID_COMMAND_ = -14

#util function
def checkIp(ipaddr):
        addr=ipaddr.strip().split('.')
        if len(addr) != 4:
                return _ERR_CODE_ERR_
        for i in range(4): 
                try: 
                        addr[i]=int(addr[i])
                except: 
                        return _ERR_CODE_ERR_
                if addr[i]<=255 and addr[i]>=0:
                        pass
                else: 
                        return _ERR_CODE_ERR_
                i+=1
        return _ERR_CODE_OK_

def checkPort(port):
    try:
        myPort=int(port)
    except:
        return _ERR_CODE_ERR_
    if myPort<=65535 and myPort>=0:
        pass
    else:
        return _ERR_CODE_ERR_
    return _ERR_CODE_OK_

def safeExit():
    iotx.comm.log.iotxLog.p(iotx.comm.log.iotxLog._LOG_FATAL_, "iotX terminaed for fatal error, please check the log file for the reason")
    try:
        os._exit(0)
    except:
        pass

#process bar
import threading,time
class processBarClass():
    status = 0
    def p(self):
        if (1 != self.status):
            self.status = 0
            return
        while(1 == self.status):
            print ">",
            time.sleep(1)
        self.status = 0
        print ""
        return

    def start(self):
        if (0 != self.status):
            pass
        pTh = threading.Thread(target=self.p,name='Th_processBar')
        self.status = 1
        pTh.start()
        return

    def stop(self):
        self.status = 0
        print "\r"

doProcessBar = processBarClass()

#分配一个随机验证码
def allocRegistKey():
    sampleStr = string.ascii_letters+string.digits
    return ''.join(random.sample(sampleStr,60))
