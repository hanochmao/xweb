import socket


class Config:
    # 数据库配置
    # 获取本地主机名
    host_name = socket.gethostname()
    # 根据主机名获取本地 IP 地址
    ip_address = socket.gethostbyname(host_name)
    if ip_address == 'xxx':
        MYSQL_HOST = 'xxx'
        API_BASE_URL = 'http://www.eggmuscle.cn'
    else:
        MYSQL_HOST = 'xxx'
        API_BASE_URL = 'http://127.0.0.1: 5000'
    MYSQL_USER = 'xxx'
    MYSQL_PASSWORD = 'xxx'
    MYSQL_DB = 'flask'
    MYSQL_CHARSET = 'utf8mb4'


    # session加密
    SECRET_KEY = "xxx"

    # 邮箱配置
    # 邮箱配置
    MAIL_SERVER = "smtp.qq.com"
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = "xxx"
    MAIL_PASSWORD = "xxx"
    MAIL_DEFAULT_SENDER = "xxx"


    DPSK_API_KEY = "xxx"

