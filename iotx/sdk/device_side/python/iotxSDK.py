#!usr/bin/env python
#-*-coding=utf8-*-
"""
Author: hujiang001@gmail.com
ChangeLog: 2016-03-29 created

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
import json
import urllib,httplib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#user configure
protocal = "http" #http https
server = "127.0.0.1"
serverPort = 8888
version = "v1.0"

def toString(codingStr):
    '''
    transfer string to unicode, eg."\u5317\u4eac"->"北京"
    :param codingStr:unicode
    :return:string
    '''
    if not isinstance(codingStr,basestring):
        return codingStr
    return codingStr.decode('unicode-escape')

def toUnicode(codingStr):
    '''
    transfer unicode to string, eg."北京"->"\u5317\u4eac"
    :param codingStr: string
    :return:unicode
    '''
    if not isinstance(codingStr,basestring):
        return codingStr
    return codingStr.encode('unicode-escape')

def makeUrl(resName, paraList=None):
    global version
    url = '/'+version
    res = {
        'root': r'',
        'user': r'/users',
        'userOne': r'/user/{0[0]}',
        'device': r'/devices',
        'deviceOne': r'/device/{0[0]}',
        'sensor': r'/device/{0[0]}/sensors',
        'sensorOne': r'/device/{0[0]}/sensor/{0[1]}',
        'dataSet': r'/device/{0[0]}/sensor/{0[1]}/dataSet',
        'commandSet': r'/device/{0[0]}/sensor/{0[1]}/commandSet',
        'commandSetOne': r'/device/{0[0]}/sensor/{0[1]}/commandSet/{0[2]}',
        'accessKey': r'/accessKey',
        'deviceAuth': r'/deviceauth',
        'userLogin': r'/userLogin',
        'userLogout': r'/userLogout/{0[0]}'
    }
    url = url + res[resName].format(paraList)
    return url

def send(method,resource,carrier='uri',data=None,userAuth=None,accessKey=None):
    '''
    send data to iotx server
    :param method:GET\PUT\POST\DELETE
    :param resource:
    :param carrier:uri\body
    :param data: json format,the data you want to send.
    :param userAuth:user and pwd
    :param accessKey:
    :return:dict('status':None, 'retcode':None,'body':None)
    '''
    global server,serverPort
    #connect to server
    conn = httplib.HTTPConnection(server,serverPort,timeout=100)

    #make header
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    if userAuth:
        headers['user']=toUnicode(userAuth['user'])
        headers['pwd']=toUnicode(userAuth['pwd'])

    if accessKey:
        headers['accessKey']=accessKey

    #make data with body or uri
    myBody = None
    uri = resource
    if carrier is 'uri':
        uri = uri + '?' + 'arg_carrier=uri'
        if data is not None:
            uri = uri+'&'+urllib.urlencode(data)
            #print uri
        conn.request(method, uri, headers=headers)
    elif carrier is 'body':
        if data is not None:
            myBody = json.dumps(data)
            #print 'send:'+ myBody
        conn.request(method, uri, myBody,headers)
    else:
        assert 0

    #send to server and get response
    resp = conn.getresponse()

    #make response
    ret = {'status':None, 'retcode':None,'body':None}
    ret['status'] = resp.status
    ret['retcode'] = resp.getheader('retcode')
    respBody = resp.read()
    conn.close()
    if respBody is not '':
        try:
            #print respBody
            ret['body'] = json.loads(respBody)
        except:
            assert 0
    return ret
