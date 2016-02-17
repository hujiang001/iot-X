#-*-coding=utf8-*-
"""
create a link to server
we will make a heartbeat between c-s, for checking link-error and make the link is online
"""
# outer import
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import Protocol,ClientFactory
# inner import,注意不要造成导入循环
from iotx.comm import util
from iotx.comm.log import iotxLog
from iotx.comm.singleton import Singleton
from iotx.comm import datasyn


def clientConnectErr(result):
    reactor.stop()
    util.safeExit()

class iotxClientProtocol(Protocol):
    def dataReceived(self, data):
        #split the msg
        dataSplit = str(data).split('\r')
        for s in dataSplit:
            if s != "":
                iotxLog.p(iotxLog._LOG_MSG_,s)
                self.factory.callback_msgProc(s)

    def connectionMade(self):
        self.factory.conn = self
        util.doProcessBar.stop()
        iotxLog.p(iotxLog._LOG_INFO_,"connect to server success")
        from iotx.controller.fsm import LINK_FSM #局部导入,规避导入循环
        LINK_FSM.fsmRun(LINK_FSM.LINK_FSM_EVENT_CONNECT_SUCCESS_)

    def sendMsg(self, msg):
        self.transport.getHandle().sendall(msg)



class iotxClientFactory(ClientFactory):
    protocol = iotxClientProtocol
    conn = None #protocol instance
    p = None
    callback_msgProc = None
    def __init__(self, deferred):
        self.deferred = deferred

    def clientConnectionFailed(self, connector, reason):
        util.doProcessBar.stop()
        iotxLog.p(iotxLog._LOG_ERR_,"connect to server failed, reason: "+ reason.getErrorMessage())
        from iotx.controller.fsm import LINK_FSM #局部导入,规避导入循环
        LINK_FSM.fsmRun(LINK_FSM.LINK_FSM_EVENT_CONNECT_FAIL_OR_LOST_, connector, reactor)


    def clientConnectionLost(self, connector, reason):
        util.doProcessBar.stop()
        iotxLog.p(iotxLog._LOG_ERR_,"connection lost, reason: "+ reason.getErrorMessage())
        from iotx.controller.fsm import LINK_FSM #局部导入,规避导入循环
        LINK_FSM.fsmRun(LINK_FSM.LINK_FSM_EVENT_CONNECT_FAIL_OR_LOST_, connector, reactor)


class iotxClient():
    __metaclass__ = Singleton  #只能创建一个实例
    ipadd = "127.0.0.1";
    port = 1234;
    factory = None
    def __init__(self):
        pass

    def start(self, ipadd, port, msgHandle):

        self.ipadd = ipadd
        self.port = port
        iotxLog.p(iotxLog._LOG_INFO_, "create controller link:"+ipadd+":"+port)
        util.doProcessBar.start()
        d = defer.Deferred()
        d.addErrback(clientConnectErr)
        self.factory = iotxClientFactory(d)
        self.factory.callback_msgProc = msgHandle
        reactor.connectTCP(self.ipadd, int(self.port), self.factory)
        reactor.run()

    def sendMsg(self,data):
        self.factory.conn.sendMsg(data+'\r')

from sys import modules
#define controller instance
CLIENTINS = iotxClient()


