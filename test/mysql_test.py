import socket
import pymysql
from app.db import get_db_connection
def get_local_ip():
    # 获取本地主机名
    host_name = socket.gethostname()
    # 根据主机名获取本地 IP 地址
    ip_address = socket.gethostbyname(host_name)
    MYSQL_HOST = ''
    if ip_address =='172.22.82.125':
        MYSQL_HOST = 'rm-wz99jd7p3r7c248h5.mysql.rds.aliyuncs.com'
    else:
        MYSQL_HOST = 'rm-wz99jd7p3r7c248h5ko.mysql.rds.aliyuncs.com'
    MYSQL_USER = 'xxx'
    MYSQL_PASSWORD = 'xxx'
    MYSQL_DB = 'flask'
    MYSQL_CHARSET = 'utf8mb4'

    config = {
        'host': MYSQL_HOST,  # 数据库服务器地址
        'user': MYSQL_USER,  # 数据库用户名
        'password': MYSQL_PASSWORD,  # 数据库密码
        'database': MYSQL_DB,  # 数据库名
        'charset': MYSQL_CHARSET,  # 字符编码
        'cursorclass': pymysql.cursors.DictCursor  # 使用字典模式获取查询结果
    }

    # 连接数据库
    connection = pymysql.connect(**config)

    try:
        # 创建游标对象
        with connection.cursor() as cursor:
            # 执行SQL语句
            sql = "SELECT count(1) FROM test"
            cursor.execute(sql)
            # 获取查询结果
            results = cursor.fetchall()
            for r in results:
                print(r)
    finally:
        connection.close()  # 关闭数据库连接
    return config


def db_write():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        sql = "insert into t_captcha(femail,fcaptcha) values(%s,%s)"
        cursor.execute(sql, ('xxx@a', 'test'))
        connection.commit()
    print("Email sent successfully!")



if __name__ == '__main__':
    print(get_local_ip())
    # db_write()

