import uvicorn
from datetime import datetime, timedelta
from typing import Optional
import mysql.connector
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from hashlib import md5
import timetable
from timetable import getCookies


# 生成MD5


def genearteMD5(original: str):
    # 创建md5对象
    hl = md5()

    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
    hl.update(original.encode(encoding='utf-8'))

    return hl.hexdigest()


class UserCreate(BaseModel):
    userName: str
    password: str


class User(BaseModel):
    userName: Optional[str] = None
    md5: str = None
    password: Optional[str] = None
    lastRefreshTime: Optional[datetime] = None


class UserDAO:
    config = {
        'host': "localhost",    # 本地数据库测试
        "password": "Bamboo@314",

        "user": "root",
        'port': 3306,
        'database': "timetable",
    }

    def updateLastRefreshTime(self, userName, lastRefreshTime):
        db = mysql.connector.connect(**self.config)
        cursor = db.cursor()
        sql = "update account set lastRefreshTime = '{}' where userName = '{}'".format(
            lastRefreshTime, userName)
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
        sql = "select * from account where md5 = '{}'".format(md5)
        # 若连接失效，自动重连数据库
        db.ping(reconnect=True)

        # 执行sql语句
        cursor.execute(sql)
        # 如果有用户的话
        result = cursor.fetchone()
        if result:

            user = User(userName=result[0], password=result[1],
                        md5=result[2], lastRefreshTime=result[3])
            return user
        else:
            return None

    def getUserByUserName(self, userName):
        db = mysql.connector.connect(**self.config)
        cursor = db.cursor()
        sql = "select * from account where userName = '{}'".format(userName)
        # 若连接失效，自动重连数据库
        db.ping(reconnect=True)

        # 执行sql语句
        cursor.execute(sql)
        # 如果有用户的话
        result = cursor.fetchone()
        if result:
            user = User(userName=result[0], password=result[1],
                        md5=result[2], lastRefreshTime=result[3])
            return user
        else:
            return None

    def insertUser(self, user):
        sql = f"insert into account (userName,password,md5) values ('{user.userName}','{ user.password}','{user.md5}')"

        # 如果存在同名用户，只就好更新
        if self.getUserByUserName(user.userName):
            sql = f"update account set password='{user.password}' where userName = '{user.userName}'"

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
        sql = "delete from account where userName = {}".format(userName)
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


app = FastAPI()

# 防止 POST 请求变成 OPTIONS 请求后被 ban（405 错误）
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(HTTPSRedirectMiddleware)


@app.post("/signup")
# async def signUp(userName: str = Form(...), password: str = Form(...)):
#     md5 = genearteMD5(userName)
#     user = User(userName=userName, password=password,
#                 md5=md5)
async def signUp(payload: UserCreate):
    userName = payload.userName
    password = payload.password
    md5 = genearteMD5(userName)
    user = User(userName=userName, password=password,
                md5=md5)

    isPasswordCorrect = getCookies(userName, password)
    if isPasswordCorrect == False:
        return {"code": -1, "message": "新教务处学号或密码错误"}

    result = UserDAO().insertUser(user)

    if result == True:
        return {"code": 0, "message": "登录成功", "url": f"webcal://time.pytbt.xyz/api/iCalendar/{md5}"}
    else:
        return {"code": -2, "message": "登录失败，无法将用户信息写入数据库"}


@app.get("/iCalendar/{md5}")
async def getiCalendar(md5: str):

    user = UserDAO().getUserByMd5(md5)

    print(user.userName)

    if user is None:
        return {"code": -1, "message": "用户不存在"}

    elif user.lastRefreshTime is None or abs(user.lastRefreshTime-datetime.now()) > timedelta(days=2):
        now = datetime.now()

        # 刷新时间超过两天，重新生成日历，并更新数据库上次刷新时间
        print(f"开始更新 {user.userName} 的日历")
        timetable.getCalendar(user.userName, user.password, user.md5)
        print(f"更新 {user.userName} 的日历完成")
        UserDAO().updateLastRefreshTime(user.userName, now)
        filePath = f"timetable/{md5}.ics"
        return FileResponse(filePath)

    else:
        # 刷新时间未超过两天，直接返回已有日历

        filePath = f"timetable/{md5}.ics"
        return FileResponse(filePath)


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, host='0.0.0.0',
                reload=True, reload_dirs=["html_files"])
