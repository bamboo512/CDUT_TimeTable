from backend.util import encryptPassword, get_config
import asyncio

config = get_config()

# ! 暂时没能搞定从砚湖易办那里，通过统一认证平台进入新教务。所以这个文件暂时未被启用。


# ! 统一身份认证的密码是用 RSA 加密的，需要先获取 Public Key 才能加密
# ! 统一身份认证 - 获取 Public Key
async def uni_get_public_key(session):
    url = config["统一身份认证"]["publicKeyUrl"]

    async with session.get(url) as resp:
        result = await resp.text()
        # print(result)
        return result


# 从砚湖易办 的统一身份认证登录
async def uni_login(session, publicKey, username, password):
    url = config["统一身份认证"]["loginUrl"]

    password = encryptPassword(password, publicKey)
    print(password)

    payload = {
        "username": username,
        "password": password,
        "submit": "Login1",
        "_eventId": "submit",
        "execution": "e1s1",
        "captcha": "",
        "currentMenu": "1",
        "failN": "0",
        "mfaState": "",
        "geolocation": "",
    }

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
    }

    async with session.post(url, data=payload, headers=headers) as resp:
        await resp.text()
        url = resp.url

        print(url)
        return True
