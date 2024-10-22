from enum import Enum


class StatusCodeEnum(Enum):
    """状态码枚举类, 返回给前端处理"""

    OK = (0, 'ok')  # 成功
    ERROR = (-1, '错误')
    SERVER_ERR = (500, '服务器异常')

    # 数据库相关错误码
    DB_COMMON_ERR = (2000, '数据库错误')
    DB_CREATE_ERR = (2001, '数据库写入数据错误')
    DB_DELETE_ERR = (2002, '数据库删除数据错误')
    DB_UPDATE_ERR = (2003, '数据库更新数据错误')
    DB_QUERY_ERR = (2004, '数据库查询数据错误')

    # HTTP相关错误
    REQUEST_PARAMS_ERR = (3001, 'http请求入参错误')

    # 用户相关错误
    USER_NOT_EXIST = (4000, "用户未查找到")
    PWD_ERR = (4005, '密码错误')
    MOBILE_ERR = (4007, '手机号错误')
    SMS_CODE_ERR = (4008, '短信验证码有误')


    @property
    def code(self):
        """获取状态码"""
        return self.value[0]

    @property
    def errmsg(self):
        """获取状态码信息"""
        return self.value[1]


class ReturnCodeEnum(Enum):
    """返回码枚举类"""
    OK = (0, '成功')  # 成功
    FAILED = (-1, '错误')  # 失败，通用

    @property
    def code(self):
        """获取状态码"""
        return self.value[0]

    @property
    def errmsg(self):
        """获取状态码信息"""
        return self.value[1]
