from util import get_config
import mysql.connector
from vo.user import User


class UserDAO:

    config = get_config().get("db")

    def __init__(self):
        db = mysql.connector.connect(**self.config)
        cursor = db.cursor()

        sql = """
            create table if not exists 
                accounts(
                        userName varchar(32) primary key not null, 
                        password varchar(32),
                        lastRefreshTime datetime, 
                        isUniLogin boolean,
                        retryTimes int,
                        md5 varchar(32)
                );
        """

        try:
            cursor.execute(sql)
            # 提交事务
            db.commit()

        except Exception:
            db.rollback()

        cursor.close()
        db.close()

    def updateLastRefreshTime(self, userName, lastRefreshTime):
        db = mysql.connector.connect(**self.config)
        cursor = db.cursor()
        sql = "update accounts set lastRefreshTime = '{}' where userName = '{}'".format(
            lastRefreshTime, userName
        )
        try:
            # 执行 sql 语句
            cursor.execute(sql)
            # 提交事务
            db.commit()

        except Exception:
            # Rollback in case there is any error
            db.rollback()

        cursor.close()
        db.close()
        return cursor.rowcount

    def getUserByMd5(self, md5):
        db = mysql.connector.connect(**self.config)
        cursor = db.cursor()
        sql = "select userName,password,md5,lastRefreshTime from accounts where md5 = '{}'".format(
            md5
        )
        # 若连接失效，自动重连数据库
        db.ping(reconnect=True)

        # 执行sql语句
        cursor.execute(sql)
        # 如果有用户的话
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result:

            user = User(
                userName=result[0],
                password=result[1],
                md5=result[2],
                lastRefreshTime=result[3],
            )

            cursor.close()
            db.close()

            return user
        else:
            return None

    def getUserByName(self, userName):
        db = mysql.connector.connect(**self.config)
        cursor = db.cursor()
        sql = "select userName,password,md5,lastRefreshTime from accounts where userName = '{}'".format(
            userName
        )
        # 若连接失效，自动重连数据库
        db.ping(reconnect=True)

        # 执行sql语句
        cursor.execute(sql)
        # 如果有用户的话
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result:
            user = User(
                userName=result[0],
                password=result[1],
                md5=result[2],
                lastRefreshTime=result[3],
            )
            return user
        else:
            return None

    def insertUser(self, user):
        sql = f"insert into accounts (userName,password,md5) values ('{user.userName}','{ user.password}','{user.md5}')"

        # 如果存在同名用户，就更新
        if self.getUserByName(user.userName):
            sql = f"update accounts set password='{user.password}' where userName = '{user.userName}'"

        db = mysql.connector.connect(**self.config)
        cursor = db.cursor()

        try:
            # 执行 sql 语句
            cursor.execute(sql)
            # 提交事务
            db.commit()

        except Exception:
            # Rollback in case there is any error
            db.rollback()
            return False

        cursor.close()
        db.close()
        return True

    def deleteUser(self, userName):
        db = mysql.connector.connect(**self.config)
        cursor = db.cursor()
        sql = "delete from accounts where userName = {}".format(userName)
        try:
            # 执行 sql 语句
            cursor.execute(sql)
            # 提交事务
            db.commit()

        except Exception:
            # Rollback in case there is any error
            db.rollback()

        cursor.close()
        db.close()
        return cursor.rowcount  # 返回受 sql 语句影响后变更的列数
