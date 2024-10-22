import hashlib
import os


def encrypt_password(password):
    """
    用户密码加密
    :param password: 用户密码
    :return: 加密后的密码，和加密的盐值
    """
    # 生成随机盐值
    salt = os.urandom(16)  # 长度为16字节的随机字符串
    # 使用盐值与密码进行加密
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # 返回加密后的密码和盐值
    return hashed_password, salt


def verify_password(password, hashed_password, salt):
    """
    用户密码验证
    :param password: 用户输入的密码
    :param hashed_password: 用户注册保存的加密后的密码
    :param salt: 存储的密码加密盐值
    :return: 是否验证通过
    """
    # 使用盐值与密码进行加密
    new_hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # 验证密码是否匹配
    return new_hashed_password == hashed_password
