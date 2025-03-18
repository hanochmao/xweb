from loguru import logger

from app.db import get_db_connection


def check_pay(email):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT fstate FROM t_user_pay WHERE femail = %s"
            params = (email,)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            cursor.execute(sql, params)
            result = cursor.fetchall()
            state = 0
            if result:
                state = result[0]['fstate']
    finally:
        connection.close()
    return state


if __name__ == '__main__':
    email = 'xxx@qq.com'
    print(check_pay(email))