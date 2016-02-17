#-*-coding=utf8-*-
"""
main file for iotX server
"""

from threading import Thread
from iotx.comm.cmdline import cmdLine
from iotx.comm.plugin import pluginM
import iotx.server.server as S


def iotXStartServer():
    #init runlog file
    from iotx.comm.log import iotxLog
    iotxLog.p(iotxLog._LOG_INFO_,"start iotx server...")

    #插件管理模块初始化
    plug = pluginM("iotx.test")
    #启动命令行
    cmds = {
        'debug':iotxLog.switch, #debug 开关, close\info\warning\error\fatal\msg\all\show
        'addtest':plug.runPlugin,  #添加一个test,参数[testName]
        'rmvtest':plug.rmvPlugin #删除一个test,参数[testName]
    }
    cmdLine(cmds).start()

    #start server listen


    #for test, user alloc a controller regist key
    #SERVERINS.userAllocCtrlRegistKey()

    S.SERVERINS.start(8100)

def iotXStartWebServer():
    #start webserver
    import webserver,configuration
    ws = webserver.webServer()
    ws.start(configuration.WEBSERVER_PORT)


if __name__ == "__main__":
    th = Thread(target=iotXStartWebServer)
    th.start()
    iotXStartServer()




