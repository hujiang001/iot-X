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
import json
import sys

from tornado import web,escape
import configure
import authManager
import database
import msgbuilder
import privilegeM
import restDef
from tools import error
from tools import log

reload(sys)
sys.setdefaultencoding('utf8')

#TODO api中是否应该定义一些返回码??
class baseHandle(web.RequestHandler):
    __ERRCODE__ = {
        'innererr':{'status':500, 'code':'SERVER_INNER_ERROR'},
        'offline':{'status':401, 'code':'USER_OFFLINE'},
        'privilege':{'status':401, 'code':'NO_PRIVILEGE'},
        'pwdwrong':{'status':401, 'code':'OLD_PWD_INVALID'},
        'notfound':{'status':500, 'code':'OBJECT_NOT_FOUND'},
        'keyinvalid':{'status':500, 'code':'ACCESSKEY_INVALID'},
        'notaccess':{'status':500, 'code':'DEVICE_NOT_ACCESS'},
        'bothauth':{'status':500, 'code':'BOTH_KEY_USER_INVALID'},
        'loginfail':{'status':401, 'code':'LOGIN_FAIL'},
        'parainvalid':{'status':401, 'code':'PARAM_INVALID'},
        'accessmax':{'status':401, 'code':'ACCESS_MAX'},
        'userexist':{'status':401, 'code':'USER_EXIST'},
        'keyconflict':{'status':401, 'code':'KEY_CONFLICT'},
    }

    #Cross-Origin Resource Sharing (CORS) support
    def write(self, chunk):
        self.set_header('Server','iotX-1.0')
        self.set_header('Access-Control-Allow-Origin', configure.accessControlAllowOrigin)
        self.set_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT,DELETE')
        self.set_header('Access-Control-Allow-Headers', 'user,pwd,accessKey')
        self.set_header('Access-Control-Expose-Headers','retcode')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Max-Age','1800')
        super(baseHandle, self).write(chunk)

    def options(self, *args, **kwargs):
        self.write("")

    def toString(self,codingStr):
        if type(codingStr) is not str:
            return codingStr
        return codingStr.decode('unicode-escape')

    def toUnicode(self,codingStr):
        if type(codingStr) is not str:
            return codingStr
        return codingStr.encode('unicode-escape')

    """
    http protocal can use uri or body to carry arguments. iotx support both methods.
    you can modify argument_carrier to control it.
    'body': carried by body . as default. should be json format string.
    'uri': carried by uri ? methods
    """

    def _getAllArguments(self, apiRequest):
        """function to get all argument from request msg.
        """
        r = apiRequest
        argument_carrier = self.get_argument('arg_carrier','body')
        if type(r) is not dict:
            return
        if argument_carrier == 'uri':
            for k in r.keys():
                if k != 'userDefArea':
                    r[k] = self.get_argument(k,default=r[k])
            if r.has_key('userDefArea'):
                r['userDefArea'] = self.get_argument('userDefArea',None)
        else:
            for k in r.keys():
                r[k] = self._getArgumentFromBody(k,default=r[k])
                if k == 'userDefArea' and (r[k] is not None):
                    try:
                        r[k] = json.dumps(r[k])
                    except:
                        pass

    def _getArgumentFromBody(self,key,default=None):
        """
        get argument from body. body should be json format
        """
        #print self.request.body
        try:
            bodyDecode = json.loads(self.request.body)
            #print bodyDecode
        except Exception,e:
            log.logError("_getArgumentFromBody load body to json fail,exception: "+e.message)
            return default
        if type(bodyDecode) is not dict:
            log.logError("_getArgumentFromBody body is not a dict type ")
            return default
        if not bodyDecode.has_key(key):
            return default
        return bodyDecode[key]

    def _getResponse(self, request, pathParas):
        """this is a interface, subclass should implement it.
        request get from request msg.
        pathParas get form path, is a list type
        """
        return {}

    def get_current_user_from_header(self):
        user = self.request.headers.get('user')
        pwd = self.request.headers.get('pwd')
        if (user is None) or (pwd is None):
            return 0
        user = self.toString(user)
        pwd = self.toString(pwd)
        ret,userId = authManager.userAuthByNamePwd(user,pwd)
        if error.ERR_CODE_OK_ != ret:
            return 0
        return userId

    def get_current_user_from_cookie(self):
        try:
            userId = int(self.get_secure_cookie('user'))
        except Exception,e:
            return 0
        return userId

    def get_current_user(self):
        """get current user from cookie.
        if cookie is not supported, para in header will be used.
        """
        userId = self.get_current_user_from_cookie()
        if userId==0:
            return self.get_current_user_from_header()
        return 0

    def send_error_msg(self,err,body={}):
        """
        err:  self.__ERRCODE__['']
        """
        log.logError("send_error_msg: status="+str(err['status'])+", retcode="+err['code'])
        self.set_header('retcode',err['code'])
        self.set_status(err['status'])
        self.write(escape.json_encode(body))
        self.finish()

    # some operation require user login, this function should be called before it
    def userLoginCheck(self):
        if self.current_user==0:
            self.send_error_msg(self.__ERRCODE__['offline'])
            return error.ERR_CODE_ERR_

        if self.get_current_user_from_cookie()!= 0:
            if authManager.userGetStatus(int(self.current_user))!='online':
                #容错处理,看sockie中的已经登录用户在数据库中的状态是否正确,如果不正确,那么踢掉用户
                self.clear_cookie('user')
                self.send_error_msg(self.__ERRCODE__['offline'])
                return error.ERR_CODE_ERR_
        return error.ERR_CODE_OK_

    def privilegeCheck(self,masterId=None,object=None,objectId=None,operation=None,master='user'):
        if privilegeM.priv_check(masterId,object,objectId,operation,master) is not error.ERR_CODE_OK_:
            self.send_error_msg(self.__ERRCODE__['privilege'])
            return error.ERR_CODE_ERR_
        return error.ERR_CODE_OK_

    # device oper use accesskey to auth
    def accessKeyCheck(self, deviceId):
        key = self.request.headers.get('accessKey')
        if (key is None) or (key is ''):
            self.send_error_msg(self.__ERRCODE__['keyinvalid'])
            return error.ERR_CODE_ERR_
        if not authManager.deviceIsAccessed(deviceId,key):
            self.send_error_msg(self.__ERRCODE__['notaccess'])
            return error.ERR_CODE_ERR_
        return error.ERR_CODE_OK_

    # both user or accesskey auth
    def userOrAccessKeyCheck(self,deviceId):
        accessKey = self.request.headers.get('accessKey')
        if (accessKey is not None) or (accessKey is not ''): #accessKey
            if authManager.deviceIsAccessed(deviceId,accessKey):
                return error.ERR_CODE_ACCESSKEY_CHECK_OK
        #user
        if self.current_user != 0:
            return error.ERR_CODE_USER_CHECK_OK
        self.send_error_msg(self.__ERRCODE__['bothauth'])
        return error.ERR_CODE_ERR_

    # delete one sensor
    def deleteOneSensor(self,deviceId,sensorId):
        #delete all dataset and command
        database.db_delete_dataset(deviceId,sensorId)
        database.db_delete_commandset(deviceId,sensorId)

    # delete one device
    def deleteOneDevice(self,deviceId,userId):
        rows,isEof = database.db_select_sensor(deviceId=deviceId)
        for item in rows:
            self.deleteOneSensor(deviceId,item[0])
        authManager.deviceRemove(deviceId) #remove from accessKey
        database.db_delete_device(deviceId)
        database.db_delete_deviceauth(userId,deviceId)
        privilegeM.priv_del(masterId=userId,object='device',objectId=deviceId,master='user')

    # delete one user
    def deleteOneUser(self,userId):
        # delete device which created by this user
        deviceList = database.db_select_owner_devicelist_by_userid(userId)
        for deviceId in deviceList:
            self.deleteOneDevice(deviceId,userId)
        database.db_delete_user(userId)
        privilegeM.priv_del(master='user',masterId=self.current_user,object='user',objectId=userId)

class rootHandle(baseHandle):
    def get(self):
        self.render('templete/index.html')

class usersHandle(baseHandle):
    def get(self):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='user',objectId=None,operation='get') != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['user']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        self.write(escape.json_encode(self._getResponse(requestApi,[])))

    def post(self):
        if self.privilegeCheck(master='user',masterId=None,\
                              object='user',objectId=None,operation='add') != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['user']]['@POST']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['user']]['@POST']['RESP'])
        self._getAllArguments(requestApi)
        #print requestApi
        id = None
        if requestApi['name'] != '':
            id = database.db_insert_user(requestApi['name'], requestApi['pwd'], requestApi['userDefArea'])
            responseApi['id'] = id
            if id is not None:
                #该user对自己拥有管理员权限
                privilegeM.priv_add(masterRole='administrator',masterId=id,object='user',objectId=id)
        else:
            log.logInfo("name is null")
            responseApi['id'] = 0

        if id is None:
            responseApi['id'] = 0
            self.send_error_msg(self.__ERRCODE__['userexist'],escape.json_encode(responseApi))
            return

        self.write(escape.json_encode(responseApi))

    def _getResponse(self, request, pathPara):
        (rows,isEof) = database.db_select_user(request['sort'], request['maxNum'], request['skipNum'])
        return msgbuilder.respBuilder_get_user(rows, isEof)

class userOneHandle(baseHandle):
    def get(self,userId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='user',objectId=userId,operation='get') != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['userOne']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        self.write(escape.json_encode(self._getResponse(requestApi,[userId,])))

    def delete(self,userId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='user',objectId=userId,operation='del') != error.ERR_CODE_OK_:
            return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['userOne']]['@DELETE']['RESP'])
        self.deleteOneUser(userId)
        self.write(escape.json_encode(responseApi))

    def put(self,userId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='user',objectId=userId,operation='upd') != error.ERR_CODE_OK_:
            return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['userOne']]['@PUT']['RESP'])
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['userOne']]['@PUT']['REQUEST'])
        self._getAllArguments(requestApi)
        #print requestApi
        #we must check oldpwd, while change the pwd
        if requestApi['pwd'] is not None:
            if requestApi['oldpwd'] is None:
                self.send_error_msg(self.__ERRCODE__['pwdwrong'])
                return
            else:
                if authManager.userAuthByIdPwd(userId,requestApi['oldpwd']) != error.ERR_CODE_OK_:
                    self.send_error_msg(self.__ERRCODE__['pwdwrong'])
                    return

        if database.db_update_user(userId, requestApi['pwd'], requestApi['userDefArea']) != error.ERR_CODE_OK_:
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        else:
            self.write(escape.json_encode(responseApi))

    def _getResponse(self, request, pathPara):
        (rows,isEof) = database.db_select_user(id=pathPara[0])
        if len(rows)<=0:
            return {}
        return msgbuilder.respBuilder_get_oneuser(rows[0])

class devicesHandle(baseHandle):
    def get(self):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=None,operation='get') != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['device']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        self.write(escape.json_encode(self._getResponse(requestApi,[])))

    def post(self):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=None,operation='add') != error.ERR_CODE_OK_:
            return
        key = self.request.headers.get('accessKey')
        if (key is None) or (key is ''):
            self.send_error_msg(self.__ERRCODE__['keyinvalid'])
            return error.ERR_CODE_ERR_
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['device']]['@POST']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['device']]['@POST']['RESP'])
        self._getAllArguments(requestApi)

        if requestApi['name'] != '':
            id = database.db_insert_device(requestApi['name'], requestApi['description'],
                                           requestApi['local'], requestApi['latitude'],
                                           requestApi['longitude'], requestApi['userDefArea'],key)
            if id is not None:
                #device access
                ret = authManager.deviceAccess(id,key)
                if ret == error.ERR_CODE_OK_:
                    #将device和user关联,并且添加user对该device的管理员权限
                    privilegeM.priv_add(masterRole='administrator',master='user',masterId=self.current_user,
                                        object='device',objectId=id)
                    database.db_insert_deviceauth(self.current_user,id)
                    responseApi['id'] = id
                    self.write(escape.json_encode(responseApi))
                    return
                elif ret == error.ERR_CODE_ACCESS_MAX:
                    errcode = 'accessmax'
                elif ret == error.ERR_CODE_PARAINVALID:
                    errcode = 'keyinvalid'
                else:
                    errcode = 'innererr'
                #delete the device
                database.db_delete_device(id)
            else:
                errcode = 'innererr'
        else:
            errcode = 'parainvalid'

        #error branch
        responseApi['id'] = 0
        self.send_error_msg(self.__ERRCODE__[errcode],body=responseApi)
        return

    def _getResponse(self, request, pathPara):
        (rows,isEof) = database.db_select_device(request['sort'], request['maxNum'], request['skipNum'])
        return msgbuilder.respBuilder_get_device(rows, isEof)

class deviceOneHandle(baseHandle):
    def get(self,deviceId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=deviceId,operation='get') != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceOne']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        self.write(escape.json_encode(self._getResponse(requestApi,[deviceId,])))

    def delete(self,deviceId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=deviceId,operation='del') != error.ERR_CODE_OK_:
            return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceOne']]['@DELETE']['RESP'])
        self.deleteOneDevice(deviceId,self.current_user)
        self.write(escape.json_encode(responseApi))

    def put(self,deviceId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
            return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceOne']]['@PUT']['RESP'])
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceOne']]['@PUT']['REQUEST'])
        self._getAllArguments(requestApi)
        if error.ERR_CODE_OK_ != database.db_update_device(deviceId,
                                                           requestApi['name'], requestApi['description'], requestApi['local'],
                                                           requestApi['latitude'], requestApi['longitude'], requestApi['userDefArea']):
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        else:
            self.write(escape.json_encode(responseApi))

    def _getResponse(self, request, pathPara):
        (rows,isEof) = database.db_select_device(id=pathPara[0])
        if len(rows)<=0:
            return {}
        return msgbuilder.respBuilder_get_onedevice(rows[0])

class sensorsHandle(baseHandle):
    def get(self,deviceId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        #sensor的权限,需要先判断其所属的device是否拥有权限
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=deviceId,operation='get') != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensor']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        self.write(escape.json_encode(self._getResponse(requestApi,[deviceId,])))

    def post(self,deviceId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        #sensor的权限,需要先判断其所属的device是否拥有权限
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
            return
        #device是否存在
        rows,isEof = database.db_select_device(num=1,id=deviceId)
        if len(rows)<=0:
            self.send_error_msg(self.__ERRCODE__['notfound'])
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensor']]['@POST']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensor']]['@POST']['RESP'])
        self._getAllArguments(requestApi)
        if requestApi['name'] != '':
            id = database.db_insert_sensor(requestApi['name'], requestApi['description'],
                                           deviceId, requestApi['userDefArea'])
            responseApi['id'] = id
        else:
            responseApi['id'] = None
        if responseApi['id'] is not None:
            #add privilege to this sennor
            privilegeM.priv_add(master='user',masterId=self.current_user,
                                object='sensor',objectId=responseApi['id'],
                                masterRole='administrator')
        #print responseApi
        self.write(escape.json_encode(responseApi))

    def _getResponse(self, request, pathPara):
        (rows,isEof) = database.db_select_sensor(request['sort'], request['maxNum'], request['skipNum'], deviceId=pathPara[0])
        return msgbuilder.respBuilder_get_sensor(rows, isEof)

class sensorOneHandle(baseHandle):
    def get(self,deviceId,sensorId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        #sensor的权限,需要先判断其所属的device是否拥有权限
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=deviceId,operation='get') != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensorOne']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        self.write(escape.json_encode(self._getResponse(requestApi,[deviceId,sensorId])))

    def delete(self,deviceId,sensorId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        #sensor的权限,需要先判断其所属的device是否拥有权限
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
            return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensorOne']]['@DELETE']['RESP'])
        self.deleteOneSensor(deviceId,sensorId)
        self.write(escape.json_encode(responseApi))

    def put(self,deviceId,sensorId):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        #sensor的权限,需要先判断其所属的device是否拥有权限
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
            return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensorOne']]['@PUT']['RESP'])
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['sensorOne']]['@PUT']['REQUEST'])
        self._getAllArguments(requestApi)
        if error.ERR_CODE_OK_ != database.db_update_sensor(sensorId,deviceId,
                                                           requestApi['name'], requestApi['description'], requestApi['userDefArea']):
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        else:
            self.write(escape.json_encode(responseApi))

    def _getResponse(self, request, pathPara):
        (rows,isEof) = database.db_select_sensor(id=pathPara[1],deviceId=pathPara[0])
        if len(rows)<=0:
            return {}
        return msgbuilder.respBuilder_get_onesensor(rows[0])

class datasetHandle(baseHandle):
    # user or device
    def get(self,deviceId,sensorId):
        # device和user都可以使用该method
        ret = self.userOrAccessKeyCheck(deviceId)
        #拥有该sensor的get权限,即可查询数据
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='get') != error.ERR_CODE_OK_:
                return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        #print requestApi
        self.write(escape.json_encode(self._getResponse(requestApi,[deviceId,sensorId])))
    # device
    def post(self,deviceId,sensorId):
        ret = self.userOrAccessKeyCheck(deviceId)
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
                return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@POST']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@POST']['RESP'])
        self._getAllArguments(requestApi)
        #print requestApi
        if requestApi['key'] != '':
            createTime = database.db_insert_dataset(deviceId, sensorId,
                                                    requestApi['key'], requestApi['value'])
            responseApi['createTime'] = createTime
        else:
            responseApi['createTime'] = None
        #print responseApi
        self.write(escape.json_encode(responseApi))
    # device
    def delete(self,deviceId,sensorId):
        ret = self.userOrAccessKeyCheck(deviceId)
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
                return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@DELETE']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@DELETE']['RESP'])
        self._getAllArguments(requestApi)
        if error.ERR_CODE_OK_ != database.db_delete_dataset(deviceId, sensorId,
                                                            requestApi['createTimeStart'], requestApi['createTimeEnd'],
                                                            requestApi['key'], ):
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        else:
            self.write(escape.json_encode(responseApi))
    # device
    def put(self,deviceId,sensorId):
        ret = self.userOrAccessKeyCheck(deviceId)
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
                return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@PUT']['RESP'])
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['dataSet']]['@PUT']['REQUEST'])
        self._getAllArguments(requestApi)
        if error.ERR_CODE_OK_ != database.db_update_dataset(deviceId, sensorId,
                                                            requestApi['value'], requestApi['key'], requestApi['createTime']):
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        else:
            self.write(escape.json_encode(responseApi))

    def _getResponse(self, request, pathPara):
        #print request
        (rows,isEof) = database.db_select_dataset(pathPara[0], pathPara[1],
                                                  request['sort'], request['maxNum'], request['skipNum'], request['orderBy'],
                                                  request['createTimeStart'], request['createTimeEnd'], request['lastUpdateTimeStart'],
                                                  request['lastUpdateTimeEnd'], request['key'], request['valueMin'], request['valueMax'])
        return msgbuilder.respBuilder_get_dataset(rows, isEof)

class commandsetHandle(baseHandle):
    # user device
    def get(self,deviceId,sensorId):
        # device和user都可以使用该method
        ret = self.userOrAccessKeyCheck(deviceId)
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            #拥有该sensor的get权限,即可查询数据
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='get') != error.ERR_CODE_OK_:
                return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSet']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        self.write(escape.json_encode(self._getResponse(requestApi,[deviceId,sensorId])))
    # user
    def post(self,deviceId,sensorId):
        ret = self.userOrAccessKeyCheck(deviceId)
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
                return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSet']]['@POST']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSet']]['@POST']['RESP'])
        self._getAllArguments(requestApi)
        if error.ERR_CODE_OK_ != \
            database.db_insert_commandset(deviceId, sensorId, requestApi['command'], requestApi['value']):
            self.send_error_msg(self.__ERRCODE__['keyconflict'],responseApi)
            return
        self.write(escape.json_encode(responseApi))

    def _getResponse(self, request, pathPara):
        (rows,isEof) = database.db_select_commandset(pathPara[0], pathPara[1],
                                                     request['sort'], request['maxNum'], request['skipNum'])
        return msgbuilder.respBuilder_get_commandset(rows, isEof)

class commandsetOneHandle(baseHandle):
    # user device
    def get(self,deviceId,sensorId,command):
        # device和user都可以使用该method
        ret = self.userOrAccessKeyCheck(deviceId)
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            #拥有该sensor的get权限,即可查询数据
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='get') != error.ERR_CODE_OK_:
                return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSetOne']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        self.write(escape.json_encode(self._getResponse(requestApi,[deviceId,sensorId,command])))
    # user device
    def delete(self,deviceId,sensorId,command):
        # device和user都可以使用该method
        ret = self.userOrAccessKeyCheck(deviceId)
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            #拥有该sensor的get权限,即可查询数据
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
                return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSetOne']]['@DELETE']['RESP'])
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSetOne']]['@GET']['REQUEST'])
        self._getAllArguments(requestApi)
        if database.db_delete_commandset(deviceId, sensorId, command) != error.ERR_CODE_OK_:
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        else:
            self.write(escape.json_encode(responseApi))
    # user device
    def put(self,deviceId,sensorId,command):
        # device和user都可以使用该method
        ret = self.userOrAccessKeyCheck(deviceId)
        if error.ERR_CODE_ERR_ == ret:
            return
        if error.ERR_CODE_USER_CHECK_OK == ret:
            #拥有该sensor的get权限,即可查询数据
            if self.privilegeCheck(master='user',masterId=self.current_user,\
                                  object='device',objectId=deviceId,operation='upd') != error.ERR_CODE_OK_:
                return
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSetOne']]['@PUT']['RESP'])
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['commandSetOne']]['@PUT']['REQUEST'])
        self._getAllArguments(requestApi)
        if error.ERR_CODE_OK_ != database.db_update_commandset(deviceId, sensorId, command, requestApi['value']):
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        else:
            self.write(escape.json_encode(responseApi))

    def _getResponse(self, request, pathPara):
        (rows,isEof) = database.db_select_commandset(pathPara[0], pathPara[1], command=pathPara[2])
        if len(rows)<=0:
            return {}
        return msgbuilder.respBuilder_get_onecommand(rows[0])

class deviceauthHandle(baseHandle):
    def post(self):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceAuth']]['@POST']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceAuth']]['@POST']['RESP'])
        self._getAllArguments(requestApi)
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=requestApi['deviceId'],\
                               operation='privilege_add') != error.ERR_CODE_OK_:
            return
        database.db_insert_deviceauth(requestApi['userId'], requestApi['deviceId'])
        privilegeM.priv_add(masterRole=requestApi['role'],masterId=requestApi['userId'],
                            object='device',objectId=requestApi['deviceId'],operList=requestApi['privilege'])
        self.write(escape.json_encode(responseApi))
    def delete(self):
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceAuth']]['@DELETE']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['deviceAuth']]['@DELETE']['RESP'])
        self._getAllArguments(requestApi)
        if self.privilegeCheck(master='user',masterId=self.current_user,\
                              object='device',objectId=requestApi['deviceId'],\
                               operation='privilege_del') != error.ERR_CODE_OK_:
            return
        database.db_delete_deviceauth(requestApi['userId'], requestApi['deviceId'])
        privilegeM.priv_del(masterId=requestApi['userId'],object='device',objectId=requestApi['deviceId'])
        self.write(escape.json_encode(responseApi))

class accessKeyHandle(baseHandle):
    def get(self):
        #登录用户即可申请accessKey
        if self.userLoginCheck() != error.ERR_CODE_OK_:
            return
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['accessKey']]['@GET']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['accessKey']]['@GET']['RESP'])
        self._getAllArguments(requestApi)
        responseApi['key']=authManager.allocAccessKey(requestApi['userId'])
        self.write(escape.json_encode(responseApi))

class userLoginHandle(baseHandle):
    def post(self):
        requestApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['userLogin']]['@POST']['REQUEST'])
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['userLogin']]['@POST']['RESP'])
        self._getAllArguments(requestApi)
        retcode,userId = authManager.userAuthByNamePwd(requestApi['name'],requestApi['pwd'])
        if retcode!=error.ERR_CODE_OK_\
            or userId is None:
            self.send_error_msg(self.__ERRCODE__['loginfail'])
            return
        # change user state
        if error.ERR_CODE_OK_!=authManager.userChangeStatus(userId,'online'):
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        # set cookie
        self.set_secure_cookie('user',str(userId),expires_days=None)
        responseApi['id'] = userId
        self.write(escape.json_encode(responseApi))

class userLogoutHandle(baseHandle):
    def post(self,userId):
        self.userLoginCheck()
        responseApi = copy.deepcopy(restDef.RESTFUL_API[restDef.HTTP_RES['userLogout']]['@POST']['RESP'])
        # change user state
        if error.ERR_CODE_OK_!=authManager.userChangeStatus(userId,'offline'):
            self.send_error_msg(self.__ERRCODE__['innererr'])
            return
        # clear cookie
        self.clear_cookie('user')
        self.write(escape.json_encode(responseApi))