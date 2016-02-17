#-*-coding=utf8-*-
import sqlite3,thread

from iotx.comm.log import iotxLog
from iotx.comm import util

#define some SQL str
#创建一些全局性的,必须的表
_SQL_INIT_ = """
CREATE TABLE IF NOT EXISTS [CTRL_CTX] (
  [NAME] TEXT,
  [REG_KEY] CHAR(60) NOT NULL,
  [CTRL_ID] INT PRIMARY KEY,
  [POS_LONGITUDE] INT,
  [POS_ALTITUDE] INT,
  [FIRST_REG_TIME] TIME,
  [LAST_REG_TIME] TIME,
  [STATUS] INT
);

CREATE TABLE IF NOT EXISTS [USER_CTX] (
  [NAME] CHAR(32) PRIMARY KEY,
  [PWD]  CHAR(32),
  [USER_ID] INT,
  [LAST_LOGIN_TIME] TIME,
  [STATUS] INT
);

CREATE TABLE IF NOT EXISTS [EQUIPMENT_CTX] (
  [NAME] CHAR(32) PRIMARY KEY,
  [DESCRIPTIION] TEXT,
  [STATUS] INT,
  [SYN_TIME] TIME
);

CREATE TABLE IF NOT EXISTS [SUBSCRIBER] (
  [EVENT] CHAR(60),
  [USER_ID] INT
);

CREATE TABLE IF NOT EXISTS [USER_CTRL_MAPPING] (
  [CTRL_ID] INT NOT NULL ,
  [USER_ID] INT NOT NULL
);

CREATE TABLE IF NOT EXISTS [CTRL_EQUIPMENT_MAPPING] (
  [CTRL_ID] INT NOT NULL ,
  [EQUIPMENT_NAME] CHAR(32) NOT NULL ,
  [SYN_TIME] TIME,
  PRIMARY KEY (CTRL_ID, EQUIPMENT_NAME)
);

"""

_SQL_INS_CTRL_CTX_ = """
        REPLACE INTO CTRL_CTX (NAME, REG_KEY, CTRL_ID, POS_LONGITUDE, POS_ALTITUDE, FIRST_REG_TIME, LAST_REG_TIME, STATUS)
        VALUES (?,?,?,?,?,?,?,?)
"""

_SQL_UPDATE_CTRL_CTX_ = """
        UPDATE CTRL_CTX SET NAME=?,CTRL_ID=?,POS_LONGITUDE=?,POS_ALTITUDE=?,FIRST_REG_TIME=?,LAST_REG_TIME=?,STATUS=? WHERE REG_KEY=?
"""

_SQL_UPDATE_CTRL_CTX_STATUS_ = """
        UPDATE CTRL_CTX SET STATUS=? WHERE CTRL_ID=?
"""
_SQL_FIND_CTRL_CTX_BY_REGKEY_ = """
        SELECT * FROM CTRL_CTX WHERE REG_KEY=?
"""
_SQL_FIND_CTRL_CTX_BY_CTRLID_ = """
        SELECT REG_KEY FROM CTRL_CTX WHERE CTRL_ID=?
"""


class iotxServerDB():
    global _SQL_INIT_
    conns = {}
    dbPath = "../../db/SERVER.db"

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
            self.conns[str(id)] = myconn
        except Exception,e:
            iotxLog.p(iotxLog._LOG_FATAL_, "init database fail,exception:" + e.message )
            util.safeExit()
            return
    #检查用户名是否重复
    def checkUserNameIsConflict(self, name):
        cursor = self.conn().cursor()
        cursor.execute("SELECT * FROM USER_CTX WHERE NAME=?",(name,))
        rows = cursor.fetchall()
        if len(rows)>0:
            return util._ERR_CODE_NAME_CONFLICT_
        return util._ERR_CODE_OK_;
    def insertToUserCtx(self, name, pwd, userid):
        try:
            self.conn().execute("INSERT INTO USER_CTX (NAME,PWD,USER_ID,STATUS) VALUES (?,?,?,?)",(name,pwd,userid,0))
            self.conn().commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "insert to user ctx fail,exception:" + e.message)
            return
        return
    def updUserStatus(self, name, status):
        try:
            if name is None:
                self.conn().execute("UPDATE USER_CTX SET STATUS=? ",(status,))
            else:
                self.conn().execute("UPDATE USER_CTX SET STATUS=? WHERE NAME=?",(status,name))
            self.conn().commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "update user status fail,exception:"+e.message)
            return
        return

    #用户权限检查
    def userAuthCheck(self, name, pwd):
        cursor = self.conn().cursor()
        cursor.execute("SELECT NAME,PWD,USER_ID,STATUS FROM USER_CTX WHERE NAME=?",(name,))
        row = cursor.fetchone()
        if len(row) <= 0:
            return (util._ERR_CODE_USERNAME_NOT_EXSIT_, row)
        if row[1] != pwd:
            return (util._ERR_CODE_USERPWD_WRONG_, row)
        if row[3] == 1: #重复登录
            return (util._ERR_CODE_USER_ALREADY_LOGIN_, row)
        return (util._ERR_CODE_OK_, row)

    #根据controller name获取id
    def getCtrlIdByName(self, name):
        cursor = self.conn().cursor()
        cursor.execute("SELECT CTRL_ID,STATUS FROM CTRL_CTX WHERE NAME=?",(name,))
        row = cursor.fetchone()
        if len(row) <= 0:
            return (None,None)
        return (row[0], row[1])

DBINST = iotxServerDB()

# use CONN to oper database
"""
CONN = DBINST.conn
curs = CONN.cursor()
str = '36hPTHGRWBDLynSqkUxa5oQVzfcCmEI8M7gl9iNdOFrA40ZsJubwtv2eKXpj'
print _SQL_FIND_CTRL_CTX_,"a"
curs.execute(_SQL_FIND_CTRL_CTX_,(str,))
rows = curs.fetchall()
print len(rows)
print rows
"""

