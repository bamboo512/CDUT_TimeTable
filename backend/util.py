"""
    工具
"""

import json
from hashlib import md5
import base64
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA

import ddddocr


def get_config():
    """从 config.json 获取配置信息"""
    with open("config.json", "r", encoding="UTF-8") as f:
        config = json.load(f)
    return config


config = get_config()


async def get_verify_code(session):
    """获取验证码"""
    # ocr = ddddocr.DdddOcr(show_ad=False)

    url = "https://jw.cdut.edu.cn/verifycode.servlet?t=0.5"
    async with session.get(url) as resp:
        if resp.status == 200:
            image = await resp.read()
            payload = {"image": image}
            # res = ocr.classification(image)
            # return res
            async with session.post(config["ddddocr_path"], data=payload) as resp1:
                result = await resp1.text()
                return result
        else:
            print(resp.status)
            return None


def generate_md5(original: str):
    """生成 md5"""

    # 创建 md5 对象
    hash_md5 = md5()

    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
    hash_md5.update(original.encode(encoding="utf-8"))

    return hash_md5.hexdigest()


def encryptPassword(password, public_key):
    rsakey = RSA.importKey(public_key)
    cipher = Cipher_pksc1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(password.encode()))
    return "__RSA__" + cipher_text.decode()
