#!/usr/bin/python
#-*-coding=utf8-*-
from ctypes import *
import time,os
import httplib,json

def __TEST_RUN_(method='GET',resource='',paras=None):
    #print "------TEST(",method," ",resource,")--------"
    conn = httplib.HTTPConnection('192.168.1.199',8888,timeout=30)
    data = None
    if paras is not None:
        data = json.dumps(paras)
        #print data
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn.request(method, '/v1.0'+resource, data, headers)
    resp = conn.getresponse()
   # print 'STATUS:'+str(resp.status)+',REASON:'+resp.reason
    #print 'BODY:'+resp.read()
    conn.close()
    #print "\r\n\r\n"
def __TEST_CASE_DATASET_POST_(key,value):
    para = {
                'key':key,
                'value':value
    }
    __TEST_RUN_('POST','/device/1/sensor/1/dataSet',para)

def __TEST_CASE_DATASET_DELETE_():
    para = {
                #'deviceId':'@PATH',
                #'sensorId':'@PATH'
                #'createTimeStart':'',
                #'createTimeEnd':'',
                'key':'temp'
            }
    __TEST_RUN_('DELETE','/device/1/sensor/1/dataSet',para)

def __TEST_CASE_DATASET_PUT_(key,value):
    para = {
                'key':key,
                'value':value
    }
    __TEST_RUN_('PUT','/device/1/sensor/1/dataSet',para)

if __name__=="__main__":
    __TEST_CASE_DATASET_POST_('temperature',0)
    __TEST_CASE_DATASET_POST_('humidity',0)

    while True:
        time.sleep(1)
        DHT11 = cdll.LoadLibrary(os.getcwd()+'/DHT11_C.so')
        errcode = DHT11.dht11_read_val()
        if 1 == errcode:
            temp = DHT11.getTemperature()
            rh = DHT11.getRh()
            #print str(temp) +" "+ str(rh)
            __TEST_CASE_DATASET_PUT_('temperature',temp)
            __TEST_CASE_DATASET_PUT_('humidity',rh)
