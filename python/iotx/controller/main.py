#-*-coding=utf8-*-
"""
main file for iotX client
"""
from iotx.comm.log import iotxLog
from iotx.comm.cmdline import cmdLine
from iotx.comm.plugin import pluginM
from iotx.controller.fsm import LINK_FSM

def addEquip(paras):
    print paras

def iotXStart():
    #init runlog file
    iotxLog.p(iotxLog._LOG_INFO_,"start iotx controller...")
    #插件管理模块初始化
    plug = pluginM("iotx.test")
    #启动命令行
    cmds = {
        'debug':iotxLog.switch, #debug 开关, close\info\warning\error\fatal\msg\all\show
        'addeq':plug.runPlugin,  #添加一个equipment,参数[equipmentName]
        'rmveq':plug.rmvPlugin #删除一个equipment,参数[equipmentName]
    }
    cmdLine(cmds).start()
    #connect to server
    LINK_FSM.fsmRun(LINK_FSM.LINK_FSM_EVENT_CONNECT_)


if __name__ == "__main__":
    iotXStart()



