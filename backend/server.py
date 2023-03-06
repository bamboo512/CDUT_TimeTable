from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from util import generate_md5
from dao.UserDAO import UserDAO
from vo.user import User
from util import get_config
import os
import aiohttp
from crawler.login.LoginHelper import LoginHelper
from timetable import getCalendar

BACKEND_URL = get_config().get("backendUrl")


app = FastAPI()
userDb = UserDAO()

# 防止 POST 请求变成 OPTIONS 请求后被 ban（405 错误）
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/signup")
async def sign_up(payload: User):
    userName = payload.userName
    password = payload.password
    md5 = generate_md5(userName)
    user = User(userName=userName, password=password, md5=md5)

    session = aiohttp.ClientSession()
    loginHelper = LoginHelper(session)
    isSccessful = await loginHelper.login(userName, password)
    if isSccessful:
        print("登录成功")
    else:
        return {"code": -1, "message": "新教务处学号或密码错误"}

    result = userDb.insertUser(user)

    if result is True:
        return {
            "code": 0,
            "message": "登录成功",
            "url": f"{BACKEND_URL}/ics/{md5}",
        }
    else:
        return {"code": -2, "message": "登录失败，无法将用户信息写入数据库"}


@app.get("/api/ics/{md5}")
async def get_icalendar(md5: str):
    user = userDb.getUserByMd5(md5)
    filePath = f"timetable/{md5}.ics"
    print(user.userName)

    if user is None:
        return {"code": -1, "message": "用户不存在"}

    elif (
        user.lastRefreshTime is None
        or abs(user.lastRefreshTime - datetime.now()) > timedelta(days=0)
        or not os.path.exists(filePath)
    ):
        now = datetime.now()

        # 刷新时间超过两天，重新生成日历，并更新数据库上次刷新时间
        print(f"开始更新 {user.userName} 的日历")
        isSuccessful = await getCalendar(user.userName, user.password, user.md5)

        if isSuccessful:
            print(f"更新 {user.userName} 的日历完成")
            userDb.updateLastRefreshTime(user.userName, now)

            return FileResponse(filePath)
        else:
            return False

    else:
        # 刷新时间未超过 7 天，且存在文件 => 返回已有日历

        return FileResponse(filePath)
