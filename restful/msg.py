#-*-coding=utf8-*-
"""
description: iotx restful msg process
author: hujiang001@gmail.com
2016-02-19 created
LICENCE: GPLV2
"""
import copy
from api import httpapi
import database
def respBuilder_get_oneuser(dbRecord):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['userOne']]['@GET']['RESP'])
    responseApi['id']=dbRecord[0]
    responseApi['name']=dbRecord[1]
    responseApi['regTime']=dbRecord[3]
    responseApi['lastLoginTime']=dbRecord[4]
    responseApi['state']=dbRecord[5]
    responseApi['userDefArea']=dbRecord[6]
    #TODO:list all device
    return responseApi

def respBuilder_get_user(dbRecords,isEof):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['user']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_oneuser(r))
    return responseApi

def respBuilder_get_onedevice(dbRecord):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['deviceOne']]['@GET']['RESP'])
    responseApi['id']=dbRecord[0]
    responseApi['name']=dbRecord[1]
    responseApi['description']=dbRecord[2]
    responseApi['regTime']=dbRecord[3]
    responseApi['local']=dbRecord[4]
    responseApi['latitude']=dbRecord[5]
    responseApi['longitude']=dbRecord[6]
    responseApi['userDefArea']=dbRecord[7]
    #TODO:list all sensor
    #TODO:list all users
    return responseApi

def respBuilder_get_device(dbRecords,isEof):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['device']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_onedevice(r))
    return responseApi

def respBuilder_get_onesensor(dbRecord):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['sensorOne']]['@GET']['RESP'])
    responseApi['id']=dbRecord[0]
    responseApi['name']=dbRecord[1]
    responseApi['description']=dbRecord[2]
    responseApi['regTime']=dbRecord[3]
    responseApi['deviceId']=dbRecord[4]
    responseApi['userDefArea']=dbRecord[5]
    return responseApi

def respBuilder_get_sensor(dbRecords,isEof):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['sensor']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_onesensor(r))
    return responseApi

def respBuilder_get_onedata(dbRecord):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['dataSet']]['@GET']['DATAONE'])
    responseApi['createTime']=dbRecord[2]
    responseApi['lastUpdateTime']=dbRecord[3]
    responseApi['key']=dbRecord[4]
    responseApi['value']=dbRecord[5]
    return responseApi

def respBuilder_get_dataset(dbRecords,isEof):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['dataSet']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_onedata(r))
    return responseApi

def respBuilder_get_onecommand(dbRecord):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['commandSetOne']]['@GET']['RESP'])
    responseApi['command']=dbRecord[2]
    responseApi['value']=dbRecord[3]
    responseApi['createTime']=dbRecord[4]
    responseApi['lastUpdateTime']=dbRecord[5]
    return responseApi

def respBuilder_get_commandset(dbRecords,isEof):
    responseApi = copy.deepcopy(httpapi.RESTFUL_API[httpapi.HTTP_RES['commandSet']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_onecommand(r))
    return responseApi