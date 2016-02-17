#-*-coding=utf8-*-
"""
key值用于server\controller\equipment之间进行认证.
该文件定义了一个通用的key生成器,key生成后,通过数据库KEY.db进行保存.
key需要保证全局唯一,并且分配的key必须在24小时之内使用,否则将失效.
key一旦被使用过后将被永久保留在KEY.db中.

该文件是相对比较独立的,可以单独运行,而不需要启动iotX.
"""

import string,random,sqlite3,time,datetime,threading,thread

from iotx.comm.log import iotxLog
import iotx.comm.util as util


class keyBuilder():
    dbPath = "../../db/KEY.db"
    isNeedAging = False
    conns = {}

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
            myconn.executescript(""" CREATE TABLE IF NOT EXISTS [KEYTBL] (
                                              [KEY] CHAR(60) NOT NULL,
                                              [ALLOC_TIME] TIME,
                                              [USE_FLAG] INT); """)
            myconn.commit()
            self.conns[str(id)] = myconn
        except Exception,e:
            iotxLog.p(iotxLog._LOG_FATAL_, "init database fail,exception:" + e.message )
            util.safeExit()
            return

    def allocRandomKey(self):
        sampleStr = string.ascii_letters+string.digits
        return ''.join(random.sample(sampleStr,60))

    def checkKeyIsAlloced(self, key):
        cursor = self.conn().cursor()
        cursor.execute(" SELECT [KEY] FROM [KEYTBL] WHERE [KEY]=?", (key,))
        if 0 < len(cursor.fetchall()):
            cursor.close()
            return True
        cursor.close()
        return False

    def addKeyToDB(self, key):
        cursor = self.conn().cursor()
        try:
            cursor.execute(" INSERT INTO [KEYTBL] (KEY, ALLOC_TIME, USE_FLAG) VALUES (?,?,?)",
                       (key, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),0))
            self.conn().commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "alloc key failed for add key to DB fail, exception:" + e.message)
            return util._ERR_CODE_ERR_
        cursor.close()
        return util._ERR_CODE_OK_

    # return None while alloc key fail
    def allocOneKey(self):
        key = self.allocRandomKey()
        while self.checkKeyIsAlloced(key):
            key = self.allocRandomKey()
        if util._ERR_CODE_OK_ != self.addKeyToDB(key):
            return None
        return key

    def agingProc(self, agingConn):
        print "aging start..."
        #当前时间前推24小时,就是老化的时间点.这个时间点之前的需要老化.
        nowTime = datetime.datetime.now()
        agingTime = nowTime - datetime.timedelta(minutes=24*60)
        agingStrTime = agingTime.strftime("%Y-%m-%d %H:%M:%S")
        print agingStrTime
        try:
            cursor = agingConn.cursor()
            cursor.execute("DELETE FROM [KEYTBL] WHERE USE_FLAG=0 AND ALLOC_TIME<=?",(agingStrTime,)) #超过24小时没有使用,则回收
            agingConn.commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_,"key builder aging process fail, exception:"+e.message)
            return
        return

    def agingTimer(self):
        try:
            agingConn = sqlite3.connect(self.dbPath)
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "conn to sqlite fail while aging, exception"+e.message)
            return
        while self.isNeedAging:
            time.sleep(30*60) #半小时check一次
            self.agingProc(agingConn)
        agingConn.close()

    # 调用该函数启动24小时key值老化检查.半小时检查一次,24小时内未使用的key将被回收.
    # 由于key为60字符的随机数,一般情况下都是够用的,所以通常不需要启用定时老化功能.
    def agingStart(self):
        self.isNeedAging = True
        th = threading.Thread(target=self.agingTimer, name="Th_keyAging")
        th.start()

    def agingStop(self):
        self.isNeedAging = False

    def setUseFlag(self, key, flag):
        try:
            self.conn().execute("UPDATE [KEYTBL] SET USE_FLAG=? WHERE KEY=?", (flag, key))
            self.conn().commit()
        except Exception,e:
            iotxLog.p(iotxLog._LOG_ERR_, "set use flag fail, exception:" + e.message)
            return util._ERR_CODE_ERR_
        return util._ERR_CODE_OK_

KEYB = keyBuilder()

