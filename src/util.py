"""
    工具
"""

import json
from hashlib import md5


def get_config():
    """生成MD5"""
    with open("config.json", "r", encoding="UTF-8") as f:
        config = json.load(f)
    return config


def generate_md5(original: str):
    """生成 md5"""

    # 创建 md5 对象
    hash_md5 = md5()

    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
    hash_md5.update(original.encode(encoding="utf-8"))

    return hash_md5.hexdigest()
