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

import copy

import database
import restDef


def respBuilder_get_oneuser(dbRecord):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['userOne']]['@GET']['RESP'])
    responseApi['id']=dbRecord[0]
    responseApi['name']=dbRecord[1]
    responseApi['regTime']=dbRecord[3]
    responseApi['lastLoginTime']=dbRecord[4]
    responseApi['state']=dbRecord[5]
    responseApi['userDefArea']=dbRecord[6]
    responseApi['deviceList'] = database.db_select_devicelist_by_userid(responseApi['id'])
    return responseApi

def respBuilder_get_user(dbRecords,isEof):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['user']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_oneuser(r))
    return responseApi

def respBuilder_get_onedevice(dbRecord):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceOne']]['@GET']['RESP'])
    responseApi['id']=dbRecord[0]
    responseApi['name']=dbRecord[1]
    responseApi['description']=dbRecord[2]
    responseApi['regTime']=dbRecord[3]
    responseApi['local']=dbRecord[4]
    responseApi['latitude']=dbRecord[5]
    responseApi['longitude']=dbRecord[6]
    responseApi['userDefArea']=dbRecord[7]
    responseApi['userIdList'] = database.db_select_userlist_by_deviceid(responseApi['id'])
    (rows,isEof) = database.db_select_sensor(deviceId=responseApi['id'],num=100)
    for item in rows:
        responseApi['sensorList'].append(item[0])
    responseApi['key'] = dbRecord[8]
    return responseApi

def respBuilder_get_device(dbRecords,isEof):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['device']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_onedevice(r))
    return responseApi

def respBuilder_get_onesensor(dbRecord):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensorOne']]['@GET']['RESP'])
    responseApi['id']=dbRecord[0]
    responseApi['name']=dbRecord[1]
    responseApi['description']=dbRecord[2]
    responseApi['regTime']=dbRecord[3]
    responseApi['deviceId']=dbRecord[4]
    responseApi['userDefArea']=dbRecord[5]
    return responseApi

def respBuilder_get_sensor(dbRecords,isEof):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensor']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_onesensor(r))
    return responseApi

def respBuilder_get_onedata(dbRecord):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@GET']['DATAONE'])
    responseApi['createTime']=dbRecord[2]
    responseApi['lastUpdateTime']=dbRecord[3]
    responseApi['key']=dbRecord[4]
    responseApi['value']=dbRecord[5]
    return responseApi

def respBuilder_get_dataset(dbRecords,isEof):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_onedata(r))
    return responseApi

def respBuilder_get_onecommand(dbRecord):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSetOne']]['@GET']['RESP'])
    responseApi['command']=dbRecord[2]
    responseApi['value']=dbRecord[3]
    responseApi['createTime']=dbRecord[4]
    responseApi['lastUpdateTime']=dbRecord[5]
    return responseApi

def respBuilder_get_commandset(dbRecords,isEof):
    responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSet']]['@GET']['RESP'])
    responseApi['num'] = len(dbRecords)
    responseApi['isEof'] = isEof
    for r in dbRecords:
        responseApi['list'].append(respBuilder_get_onecommand(r))
    return responseApi