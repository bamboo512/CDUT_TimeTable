from util import get_config, get_verify_code
import aiohttp


config = get_config()


async def main():
    session = aiohttp.ClientSession()
    loginHelper = LoginHelper(session)
    isSccessful = loginHelper.login(config["userName"], config["password"])
    if isSccessful:
        print("登录成功")


class LoginHelper:
    def __init__(self, session) -> None:
        self.session = session

    async def login(self, userName: str = None, password: str = None) -> dict:
        """获取教务处的 Cookies"""
        if userName is None or password is None:
            print("用户名和密码未输入")
            exit(-1)

        scode, sxh = await self.getPreconditionLoginCode()

        # 以下只是把新教务处官网登录的 JavaScript 源代码翻译过来。
        code = userName + "%%%" + password
        encoded = ""

        i = 0
        while i < len(code):
            if i < 20:
                encoded = encoded + code[i : i + 1] + scode[0 : int(sxh[i : i + 1])]
                scode = scode[int(sxh[i : i + 1]) : len(scode)]
            else:
                encoded = encoded + code[i : len(code)]
                i = len(code)
            i = i + 1

        # print(encoded)
        url = config["jw_api_path"]["baseUrl"] + config["jw_api_path"]["login"]

        capchaCode = await get_verify_code(self.session)

        data = {
            "userAccount": userName,
            "userPassword": "",
            "encoded": encoded,
            "RANDOMCODE": capchaCode,
        }

        async with self.session.post(url=url, data=data) as response:
            # 登录成功后 URL 会发生跳转，可依据此判断是否登录成功
            if response.status == 200:
                url = str(response.url)
                if url == "https://jw.cdut.edu.cn/jsxsd/framework/xsMainV.htmlx":
                    print(userName, "获取 Cookie 成功")
                    return True
                else:
                    print(userName, "获取 Cookie 失败")
                    return False

    # ! 需在登录之前先获取 Cookie 与 一些数据，以供登录时使用
    async def getPreconditionLoginCode(self):
        async with self.session.post(
            config["jw_api_path"]["baseUrl"] + config["jw_api_path"]["preconditionCode"]
        ) as response:
            text = await response.text()

            scode, sxh = text.split("#")
            # print(scode, sxh)

        return (scode, sxh)
