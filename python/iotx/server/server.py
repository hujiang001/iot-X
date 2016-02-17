#-*-coding=utf8-*-
"""
server实现
server要支持多个client连接,并且要给不同的client分配唯一的ID
"""
# outer import
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import Protocol,ServerFactory

# inner import,注意不要造成导入循环
from iotx.comm.log import iotxLog
import iotx.server.database as DB
from iotx.comm.keybuilder import KEYB
import iotx.comm.datasyn as SYN
from iotx.comm.singleton import Singleton


class iotxServerProtocol(Protocol):
    clientId = 0  #连接ID
    userId = 0 #用户ID,对于iotx,这里填的是controllerId.在controller注册时server分配.

    def dataReceived(self, data):
        import iotx.server.msgproc as msgproc
        #split the msg
        dataSplit = str(data).split('\r')
        for s in dataSplit:
            if s != "":
                iotxLog.p(iotxLog._LOG_MSG_,"["+str(self.clientId)+"]: "+s)
                msgproc.receiveMsg(self, s)

    def connectionMade(self):
        if self.clientId==0:
            self.clientId = self.factory.clientIdAlloc() #分配一个id
            self.factory.clients.append(self) #将本实例添加到factory中
        iotxLog.p(iotxLog._LOG_INFO_, "one controller connected, clientid="+str(self.clientId)+", from "+str(self.transport.client))

    def connectionLost(self, reason):
        import iotx.server.msgproc as msgproc
        iotxLog.p(iotxLog._LOG_WARN_, "one controller lost, clientid="+str(self.clientId)+", from "+str(self.transport.client))
        #将数据库中的状态值为0
        msgproc.procCtrlOffline(self.userId)
        self.clientId = 0
        self.userId = 0
        self.factory.clients.remove(self)

    def sendMsg(self, msg):
        self.transport.getHandle().sendall(msg+'\r') #约定消息报文以'\r'作为结束符



class iotxServerFactory(ServerFactory):
    protocol = iotxServerProtocol
    clients = [] #存储所有的client
    ID_RES = 0

    def __init__(self, deferred):
        self.deferred = deferred

    #分配一个唯一的clientid
    def clientIdAlloc(self):
        self.ID_RES = self.ID_RES + 1
        return self.ID_RES


class iotxServer():
    __metaclass__ = Singleton
    port = 1234
    factory = None
    CTRLID_RES = 0

    def __init__(self):
        pass

    def start(self, port):
        iotxLog.p(iotxLog._LOG_INFO_, "start server, port="+str(port))
        self.port = port
        d = defer.Deferred()
        self.factory = iotxServerFactory(d)
        reactor.listenTCP(int(self.port), self.factory)
        reactor.run()

    #发送给一个指定的client
    def sendMsgToClient(self,data,userId):
        for c in self.factory.clients:
            if c.userId == userId:
                c.sendMsg(data)

    #发送给多个client,类似于组播
    def sendMsgToClientGrp(self,data,userIdList):
        for c in self.factory.clients:
            for i in userIdList:
                if c.userId == i:
                    c.sendMsg(data)

    #发送给所有的client,类似于广播
    def sendMsgToAll(self,data):
        for c in self.factory.clients:
            c.sendMsg(data)

    #分配一个ctrl 注册key
    def userAllocCtrlRegistKey(self):
        return KEYB.allocOneKey()

    #分配一个controller id
    def allocControllerId(self, id, key):
        #如果id在数据库中存在,并且key能匹配上,那么继续使用原来的ID.否则重新分配一个
        cursor = DB.DBINST.conn().cursor()
        try:
            cursor.execute(DB._SQL_FIND_CTRL_CTX_BY_CTRLID_,(id,))
            #print cursor.fetchall()
            rows = cursor.fetchall()
            if 0 == len(rows):  #没有被使用,那么可以使用
                cursor.close()
                return id
            elif 1 == len(rows): #使用了,要看使用者的key是否匹配
                if key == rows[0][0]:
                    cursor.close()
                    return id
            else: #TODO:流程走到这里了!!!!这里可以打断言了,说明出现了重复的id. 后续可以考虑将这些重复ID的CTRL全部通知释放掉,重新注册
                iotxLog.p(iotxLog._LOG_FATAL_,"same controller id exsit!!!")

        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "find ctrl id from database failed, except:" + e.message)

        cursor.close()

        while True:
            self.CTRLID_RES = self.CTRLID_RES + 1
            cursor = DB.DBINST.conn().cursor()
            try:
                cursor.execute(DB._SQL_FIND_CTRL_CTX_BY_CTRLID_,(self.CTRLID_RES,))
            except Exception,e:
                iotxLog.p(iotxLog._LOG_ERR_, "find ctrl id from database failed2, except:" + e.message)

            if 0 == len(cursor.fetchall()):
                cursor.close()
                break
            cursor.close()

        return self.CTRLID_RES

#define server instance
SERVERINS = iotxServer()
SYN.setSendMsgHandle(SYN._SYN_ROLE_SERVER, SERVERINS)



