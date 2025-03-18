import random

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db_connection

bp_forgetpw = Blueprint('bp_forgetpw', __name__, url_prefix='/forgetpw')

logger.add("./log/forgetpw.log", rotation="10 MB", retention="3 days", level="INFO")
@bp_forgetpw.route('/')
def forget_pw():
    return render_template('modifypw.html')


@bp_forgetpw.route('/modify/code', methods=['POST'])
def modify_code():
    data = request.get_json()
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # 查询email是否存在
        sql = "select fuid from t_user_register where femail=%s"
        params = (email,)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        if not result:
            response = {"state": 'fail'}
            return jsonify(response)
        else:
            sql = "UPDATE t_user_register SET fpassword = %s WHERE femail = %s"
            params = (password, email)
            cursor.execute(sql, params)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            connection.commit()
            response = {"state": 'success'}
            return jsonify(response)