#-*-coding=utf8-*-
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