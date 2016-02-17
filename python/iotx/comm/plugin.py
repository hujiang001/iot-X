#-*-coding=utf8-*-
"""
插件管理模块,iotx中,equipment以插件的方式动态加载到controller中
插件.py中必须包含下面两个方法定义:
def install()
def unstall()
"""
import os
from iotx.comm.log import iotxLog

class pluginM():
    def __init__(self,plugin_path):
        self.path = plugin_path
        self.plugins = {}

    def runPlugin(self, filename):
        if len(filename) <=0:
            iotxLog.p(iotxLog._LOG_ERR_,"load plugin fail for para is null")
            return
        pluginName=os.path.splitext(filename[0])[0]
        if self.plugins.has_key(pluginName):
            if self.plugins[pluginName][1]==1:
                iotxLog.p(iotxLog._LOG_WARN_, "plugin already loaded, name="+pluginName)
                return
            else:#reload
                reload(self.plugins[pluginName][0])
                self.plugins[pluginName][0].install()
                self.plugins[pluginName][1] = 1
                iotxLog.p(iotxLog._LOG_INFO_,"install(reload) plugin success. name="+ pluginName)
                return

        # first load...
        fileN = self.path+'.'+pluginName
        try:
            plugin=__import__(fileN,fromlist=[pluginName])
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_,"load plugin fail: name="+fileN+",relt="+e.message)
            return
        plugin.install()
        self.plugins[pluginName]=[plugin,1]
        iotxLog.p(iotxLog._LOG_INFO_,"install plugin success. name="+fileN)

    def rmvPlugin(self, filename):
        if len(filename) <=0:
            iotxLog.p(iotxLog._LOG_ERR_,"rmv plugin fail for para is null")
            return
        pluginName=os.path.splitext(filename[0])[0]
        if not self.plugins.has_key(pluginName):
            iotxLog.p(iotxLog._LOG_WARN_, "no plugin need to remove, name="+pluginName)
            return
        self.plugins[pluginName][0].unstall()
        self.plugins[pluginName][1]=0
        iotxLog.p(iotxLog._LOG_INFO_,"unstall plugin success. name="+pluginName)



