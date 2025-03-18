import time

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Message
from app.smail import mail
from app.db import get_db_connection
from app.utils.random_captcha import generate_captcha
from werkzeug.security import generate_password_hash, check_password_hash
from loguru import logger

from app.config import Config

logger.add("./log/user.log", rotation="10 MB", retention="7 days", level="INFO")

bp_user = Blueprint('bp_user', __name__, url_prefix='/user')


@bp_user.route('/register/mail', methods=['POST'])
def send_mail():
    logger.info('send_mail start!')
    data = request.get_json()
    email = data.get('email')
    recipients = []
    recipients.append(email)
    captcha = generate_captcha()
    msg = Message(
        subject="Hello from Flask-Mail",
        recipients=recipients,  # 收件人列表
        body="This is a email sent from eggmuscle.\n Code:%s" % captcha  # 邮件正文
    )
    logger.info(msg)
    connection = get_db_connection()
    try:
        mail.send(msg)  # 发送邮件
        # 数据库写入，用于校验
        with connection.cursor() as cursor:
            sql = "insert into t_captcha(femail,fcaptcha) values(%s,%s)"
            params = (email, captcha)
            cursor.execute(sql, params)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            connection.commit()
        return "success"
    except Exception as e:
        return f"Failed to send email: {e}"


@bp_user.route('/register/submit', methods=['POST'])
def register_submit():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = generate_password_hash(data.get('password'))
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # 查询email是否存在
        sql = "select fuid from t_user_register where femail=%s"
        params = (email,)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        if len(result) != 0:
            response = {"state": 'fail'}
            return jsonify(response)
        else:
            sql = "insert into t_user_register(femail,fuser_name,fpassword) values(%s,%s,%s)"
            params = (email, username, password)
            cursor.execute(sql, params)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            connection.commit()
            response = {"state": 'success'}
            return jsonify(response)


@bp_user.route('/register/verified', methods=['POST'])
def register_verified():
    data = request.get_json()
    email = data.get('email')
    connection = get_db_connection()
    with connection.cursor() as cursor:
        sql = "select fcaptcha from t_captcha where femail=%s order by fupdate_time desc limit 1"
        params = (email,)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        if result:
            verification_received = result[0]['fcaptcha']
        else:
            verification_received = None
    response = {"text_received": verification_received}
    return jsonify(response)




@bp_user.route('/register')
def register():
    logger.info("register start")
    return render_template('register.html')


@bp_user.route('/login')
def login():
    logger.info("login start")
    return render_template('login.html')


@bp_user.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bp_user.login'))



@bp_user.route('/login/submit', methods=['POST'])
def login_submit():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    connection = get_db_connection()
    with connection.cursor() as cursor:
        sql = "select fuid, fpassword, fuser_name from t_user_register where femail=%s"
        params = (email,)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        if len(result) != 0:
            password_received = result[0]['fpassword']
        else:
            password_received = "xxx" + str(int(time.time()))
        if check_password_hash(password_received, password):
            state_received = 'success'
            # 加密后存储在cookie中
            session['uid'] = result[0]['fuid']
            session['email'] = email
            session['user_name'] = result[0]['fuser_name']
            response = {"text_received": state_received}
        else:
            state_received = 'fail'
            response = {"text_received": state_received}
        return jsonify(response)

@bp_user.route('/config', methods=['GET'])
def get_config():
    return {'api_base_url': Config.API_BASE_URL}

