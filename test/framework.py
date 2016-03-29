#-*-coding=utf8-*-
"""
iotx test-automated framework
"""
import sys
sys.path.append("../iotx")
import httplib,json,urllib,unittest
import threading
import configure
from server import ServerClass
import database
import privilegeM

reload(sys)
sys.setdefaultencoding('utf8')


class TestFrameworkClass(unittest.TestCase):
    th = None
    @staticmethod
    def instance():
        if not hasattr(TestFrameworkClass,'_instance'):
            TestFrameworkClass._instance = TestFrameworkClass()
        return TestFrameworkClass._instance
    def toString(self,codingStr):
        if not isinstance(codingStr,basestring):
            return codingStr
        return codingStr.decode('unicode-escape')

    def toUnicode(self,codingStr):
        if not isinstance(codingStr,basestring):
            return codingStr
        return codingStr.encode('unicode-escape')

    def serverThread(self):
        #close log output
        from tools import log
        log.logSwitch('close')
        ServerClass.instance().run()

    def runFramework(self):
        if self.th:
            return
        # start server in a thread
        self.th = threading.Thread(target=self.serverThread)
        self.th.setDaemon(True)
        self.th.start()
        import time
        time.sleep(0.05) #主线程延迟10ms,让上面的线程先得到调度

    def stopFramework(self):
        #清空数据库
        database.db_clear()
        database.db_init()
        #添加超级用户
        privilegeM.priv_add_superuser()
        #初始化权限管理模块
        privilegeM.priv_init()

    def send(self,method,resource,carrier='uri',body=None,userAuth=None,isSuperUser=False,accessKey=None):
        ret = {'status':None, 'retcode':None,'body':None}
        #header
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        if isSuperUser:
            headers['user']=self.toUnicode(configure.super_user_name)
            headers['pwd']=self.toUnicode(configure.super_user_password)
        elif userAuth:
            headers['user']=self.toUnicode(userAuth['user'])
            headers['pwd']=self.toUnicode(userAuth['pwd'])

        if accessKey:
            headers['accessKey']=accessKey
        #print headers
        conn = httplib.HTTPConnection(configure.server_ip,configure.server_port,timeout=100)

        myBody = None
        uri = resource
        if carrier is 'uri':
            uri = uri + '?' + 'arg_carrier=uri'
            if body is not None:
                uri = uri+'&'+urllib.urlencode(body)
                #print uri
            conn.request(method, uri, headers=headers)
        elif carrier is 'body':
            if body is not None:
                myBody = json.dumps(body)
                #print 'send:'+ myBody
            conn.request(method, uri, myBody,headers)
        else:
            assert 0

        resp = conn.getresponse()
        ret['status'] = resp.status
        ret['retcode'] = resp.getheader('retcode')
        respBody = resp.read()
        conn.close()
        if respBody is not '':
            try:
                #print respBody
                ret['body'] = json.loads(respBody)
            except:
                print respBody
                assert 0
        return ret

    def superUserSendMsgWithBody(self,method,resource,body=None):
        return self.send(method,resource,carrier='body',body=body,isSuperUser=True)

    def superUserSendMsgWithUri(self,method,resource,uriPara=None):
        return self.send(method,resource,body=uriPara,isSuperUser=True)

    def deviceSendMsgWithBody(self,method,resource,accessKey,body=None,auth=None):
        return self.send(method,resource,carrier='body',body=body,accessKey=accessKey,userAuth=auth)

    def deviceSendMsgWithUri(self,method,resource,accessKey,uriPara=None,auth=None):
        return self.send(method,resource,body=uriPara,accessKey=accessKey,userAuth=auth)

    def normalUserSendMsgWithBody(self,method,resource,userAuth,body=None):
        return self.send(method,resource,carrier='body',body=body,userAuth=userAuth)

    def normalUserSendMsgWithUri(self,method,resource,userAuth,uriPara=None):
        return self.send(method,resource,body=uriPara,userAuth=userAuth)

    def createOneUser(self,user,isUrl=True):
        if isUrl:
            ret = self.normalUserSendMsgWithUri('POST',"/v1.0/users",None,user)
        else:
            ret = self.normalUserSendMsgWithBody('POST',"/v1.0/users",None,user)
        self.assertEqual(200,ret['status'])
        self.assertIsNone(ret['retcode'])
        self.assertIsNotNone(ret['body'])
        self.assertIsNot(0,ret['body']['id'])
        return ret['body']['id']

    def createOneUserAndLogin(self,user,isUrl=True):
        ret = self.createOneUser(user,isUrl)
        self.userLogin(user)
        return ret

    def userLogin(self,user):
        login = {
            'name':user['name'],
            'pwd':user['pwd']
        }
        ret = self.normalUserSendMsgWithBody('POST','/v1.0/userLogin',None,body=login)
        self.assertEqual(200,ret['status'])

    def createOneDevice(self,device,user,accessKey,isUri=True):
        auth = {
            'user':user['name'],
            'pwd':user['pwd']
        }
        if isUri:
            ret = self.deviceSendMsgWithUri('POST',"/v1.0/devices",accessKey,uriPara=device,auth=auth)
        else:
            ret = self.deviceSendMsgWithBody('POST',"/v1.0/devices",accessKey,body=device,auth=auth)
        #print ret
        self.assertEqual(200,ret['status'])
        self.assertIsNone(ret['retcode'])
        self.assertIsNotNone(ret['body'])
        self.assertIsNot(0,ret['body']['id'])
        return ret['body']['id']

    def getOneKey(self,userId,user):
        keyAlloc = {
            'id':userId
        }
        auth = {
            'user':user['name'],
            'pwd':user['pwd']
        }
        ret = self.normalUserSendMsgWithBody('GET','/v1.0/accessKey',auth,body=keyAlloc)
        return ret['body']['key']

    def makeSensorsPath(self,deviceId):
        return '/v1.0/device/'+str(deviceId)+'/sensors'

    def makeSensorOnePath(self,deviceId,sensorId):
        return '/v1.0/device/'+str(deviceId)+'/sensor/'+str(sensorId)

    def createOneSensor(self,user,deviceId,sensor,isUri=True):
        auth = {
            'user':user['name'],
            'pwd':user['pwd']
        }
        if isUri:
            ret = self.normalUserSendMsgWithUri('POST',self.makeSensorsPath(deviceId),auth,sensor)
        else:
            ret = self.normalUserSendMsgWithBody('POST',self.makeSensorsPath(deviceId),auth,sensor)
        #print ret
        self.assertEqual(200,ret['status'])
        self.assertIsNone(ret['retcode'])
        self.assertIsNotNone(ret['body'])
        self.assertNotEqual(0,ret['body']['id'])
        return ret['body']['id']

    def makeDatasetPath(self,deviceId,sensorId):
        return "/v1.0/device/"+str(deviceId)+"/sensor/"+str(sensorId)+"/dataSet"

    def createOneData(self,deviceId,sensorId,data,user=None,key=None,isUri=True):
        auth = {
            'user':'','pwd':''
        }
        if user is not None:
            auth['user'] = user['name']
            auth['pwd'] = user['pwd']
            if isUri:
                ret = self.normalUserSendMsgWithUri('POST',self.makeDatasetPath(deviceId,sensorId),auth,data)
            else:
                ret = self.normalUserSendMsgWithBody('POST',self.makeDatasetPath(deviceId,sensorId),auth,data)
        else:
            if isUri:
                ret = self.deviceSendMsgWithUri('POST',self.makeDatasetPath(deviceId,sensorId),key,data)
            else:
                ret = self.deviceSendMsgWithBody('POST',self.makeDatasetPath(deviceId,sensorId),key,data)
        self.assertEqual(200,ret['status'])
        #print ret
        return ret['body']['createTime']

    def makeCmdPath(self,deviceId,sensorId):
        return "/v1.0/device/"+str(deviceId)+"/sensor/"+str(sensorId)+"/commandSet"

    def makeCmdOnePath(self,deviceId,sensorId,cmdName):
        return "/v1.0/device/"+str(deviceId)+"/sensor/"+str(sensorId)+"/commandSet/"+cmdName

    def createOneCmd(self,deviceId,sensorId,cmdBody,user=None,key=None,isUri=True,expect=200):
        auth = {
            'user':'','pwd':''
        }
        if user is not None:
            auth['user'] = user['name']
            auth['pwd'] = user['pwd']
            if isUri:
                ret = self.normalUserSendMsgWithUri('POST',self.makeCmdPath(deviceId,sensorId),auth,cmdBody)
            else:
                ret = self.normalUserSendMsgWithBody('POST',self.makeCmdPath(deviceId,sensorId),auth,cmdBody)
        else:
            if isUri:
                ret = self.deviceSendMsgWithUri('POST',self.makeCmdPath(deviceId,sensorId),key,cmdBody)
            else:
                ret = self.deviceSendMsgWithBody('POST',self.makeCmdPath(deviceId,sensorId),key,cmdBody)
        #print ret
        self.assertEqual(expect,ret['status'])

    def deleteOneCmd(self,deviceId,sensorId,cmdName,user=None,key=None,isUri=True,expect=200):
        auth = {
            'user':'','pwd':''
        }
        if user is not None:
            auth['user'] = user['name']
            auth['pwd'] = user['pwd']
            if isUri:
                ret = self.normalUserSendMsgWithUri('DELETE',self.makeCmdOnePath(deviceId,sensorId,cmdName),auth)
            else:
                ret = self.normalUserSendMsgWithBody('DELETE',self.makeCmdOnePath(deviceId,sensorId,cmdName),auth)
        else:
            if isUri:
                ret = self.deviceSendMsgWithUri('DELETE',self.makeCmdOnePath(deviceId,sensorId,cmdName),key)
            else:
                ret = self.deviceSendMsgWithBody('DELETE',self.makeCmdOnePath(deviceId,sensorId,cmdName),key)
        #print ret
        self.assertEqual(expect,ret['status'])
