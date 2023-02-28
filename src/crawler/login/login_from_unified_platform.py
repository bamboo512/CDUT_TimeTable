import aiohttp
from util import encryptPassword, get_config, get_verify_code
import asyncio

config = get_config()

# ! 统一身份认证的密码是用 RSA 加密的，需要先获取 Public Key 才能加密
# ! 统一身份认证 - 获取 Public Key
async def uni_get_public_key():
    url = config["统一身份认证"]["publicKeyUrl"]

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = await resp.text()
            print(result)
            return result


# 从砚湖易办 的统一身份认证登录
async def uni_login(username, password):
    url = config["统一身份认证"]["loginUrl"]

    publicKey = await uni_get_public_key()
    password = encryptPassword(password, publicKey)

    formData = aiohttp.FormData()
    formData.add_field("username", username)
    formData.add_field("password", password)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=formData) as resp:
            result = await resp.text()

            print(session.cookie_jar.filter_cookies("https://jw.cdut.edu.cn"))
            return session.cookie_jar


def main():
    asyncio.run(uni_login(config["userName"], config["password"]))


if __name__ == "__main__":
    main()
