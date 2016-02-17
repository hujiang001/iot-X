#-*-coding=utf8-*-
# outer import
import sqlite3,thread

# inner import,注意不要造成导入循环
from iotx.comm.log import iotxLog
from iotx.comm import util

#define some SQL str
#创建一些全局性的,必须的表
#SERVER_CTX只能存在一条记录
_SQL_INIT_ = """
    CREATE TABLE IF NOT EXISTS [SERVER_CTX](
      [ID]          INT PRIMARY KEY,
      [CTRL_ID]     INT,
      [LAST_REG_TIME] TIME
    );

    CREATE TABLE IF NOT EXISTS EQUIPMENT(
      [NAME]    CHAR(32) PRIMARY KEY,
      [DESCRIPTIION]   TEXT,
      [REG_KEY] CHAR(60) NOT NULL,
      [STATUS]  INT
    );
"""

_SQL_UPD_SERVERCTX = """
    UPDATE SERVER_CTX SET CTRL_ID=?,LAST_REG_TIME=? WHERE ID=0;
"""

_SQL_INS_SERVERCTX = """
    INSERT INTO SERVER_CTX (ID, CTRL_ID, LAST_REG_TIME) VALUES (0,?,?);
"""

class iotxControllerDB():
    global _SQL_INIT_
    conns = {} #'thread-id':conn
    dbPath = "../../db/CONTROLLER.db"
    #sqlite一个线程中建立的连接不能给另外一个线程使用,为了解决这一问题,我们封装conn()方法,给每个线程自动分配对应的sqlite连接
    def conn(self):
        id = thread.get_ident()
        if self.conns.has_key(str(id)):
            return self.conns[str(id)]
        myconn = sqlite3.connect(self.dbPath)
        self.conns[str(id)] = myconn
        return myconn

    def __init__(self):
        id = thread.get_ident()
        if self.conns.has_key(str(id)):
            return

        try:
            myconn = sqlite3.connect(self.dbPath)
            myconn.executescript(_SQL_INIT_)
            myconn.commit()
            self.conns[str(id)]=myconn
        except Exception,e:
            iotxLog.p(iotxLog._LOG_FATAL_, "init database fail,exception:" + e.message )
            util.safeExit()
            return
        try:
            myconn.execute(_SQL_INS_SERVERCTX,(0,0))
            myconn.commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_WARN_, "maybe the record in serverctx is exsited, exception:" + e.message)

    def checkEquipName(self, name, key):
        if name is "":
            return util._ERR_CODE_ERR_
        cursor = self.conn().execute("SELECT [REG_KEY] FROM EQUIPMENT WHERE NAME=?",(name,))
        rows = cursor.fetchall()
        if 0 >= len(rows): # new name
            cursor.close()
            return util._ERR_CODE_OK_
        if rows[0][0] == key: # update
            cursor.close()
            return util._ERR_CODE_UPDATE_
        else:
            cursor.close()
            return util._ERR_CODE_NAME_CONFLICT_

    def addEquipment(self,name,desp,key):
        if name is "":
            return util._ERR_CODE_ERR_
        try:
            self.conn().execute('INSERT INTO EQUIPMENT (NAME,DESCRIPTIION,REG_KEY,STATUS) VALUES (?,?,?,0)', (name, desp, key))
            self.conn().commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "add equipment to DB fail, exception:"+e.message)
            return util._ERR_CODE_ERR_
        return util._ERR_CODE_OK_

    def updateEquipment(self,name,desp=None,status=None):
        try:
            if (desp is not None) and (status is not None):
                self.conn().execute("UPDATE EQUIPMENT SET DESCRIPTIION=?,STATUS=? WHERE NAME=?",(desp,status,name))
            elif (desp is not None) and (status is None):
                self.conn().execute("UPDATE EQUIPMENT SET DESCRIPTIION=? WHERE NAME=?",(desp,name))
            elif (desp is None) and (status is not None):
                self.conn().execute("UPDATE EQUIPMENT SET STATUS=? WHERE NAME=?",(status,name))
            else:
                return util._ERR_CODE_OK_ #nothing to update
            self.conn().commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "update equipment to DB fail, exception:"+e.message)
            return util._ERR_CODE_ERR_

        return util._ERR_CODE_OK_

    def getControllerId(self):
        try:
            cursor = self.conn().cursor()
            cursor.execute("SELECT CTRL_ID FROM [SERVER_CTX] WHERE ID=0")
            row = cursor.fetchone()
            return row[0]
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "get controllerId from DB fail, exception:"+e.message)
            return 0
    def updateServerCtx(self, controllerId, regTime):
        try:
            self.conn().execute(_SQL_UPD_SERVERCTX,(controllerId,regTime))
            self.conn().commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "update server ctx to DB fail, exception:"+e.message)
            return util._ERR_CODE_ERR_
        return util._ERR_CODE_OK_

DBINST = iotxControllerDB()
