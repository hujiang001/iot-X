#-*-coding=utf8-*-
"""
命令行实现,通过新建一个线程来实现
"""

from threading import Thread

class cmdLine():
    def __init__(self, cmdTbls):
        self.cmdTbl = cmdTbls
        self.cmdTbl['help']=self.helpInfo
        self.cmdTbl['errorcmd']=self.helpInfo

    def cmdProc(self):
        while True:
            cmdStr = raw_input('<iotX>:')
            splits = cmdStr.split()
            if len(splits) <= 0:
                continue
            cmds = splits[0]
            cmds = cmds.lower()
            if not self.cmdTbl.has_key(cmds):
                self.cmdTbl['errorcmd'](None)
                continue
            #去掉cmd,保留参数
            splits.remove(splits[0])
            self.cmdTbl[cmds](splits)

    def start(self):
        th = Thread(target=self.cmdProc,name='Th_cmdline')
        th.start()

    def helpInfo(self, paras):
        print "cmd line list:"
        for c in self.cmdTbl.keys():
            if c=='errorcmd':
                continue
            print c

