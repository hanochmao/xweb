from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from loguru import logger

from app.db import get_db_connection

bp_home = Blueprint('bp_home', __name__)


@bp_home.route('/')
def home():
    return render_template('home.html')



@bp_home.route('/rnn')
def rnn():
    return render_template('tmp_rnn_demo.html')


@bp_home.route('/pdf')
def pdf():
    pdf_files = [
        {"name": "PDF 1", "path": "pdf/python高级特性.pdf"},
        {"name": "PDF 2", "path": "pdf/python高级特性.pdf"},
        {"name": "PDF 3", "path": "pdf/python高级特性.pdf"},
    ]
    return render_template('pdf.html', pdf_files=pdf_files)



@bp_home.route('/contact')
def contact():
    if not session.get('email'):  # 检查用户是否已登录
        return redirect(url_for('bp_user.login'))
    return render_template('contact.html')


@bp_home.route('/feedback', methods=['POST'])
def feedback():
    text = request.json['text']
    uid = session.get('uid')
    if not uid:
        uid = 0
    # 写入数据库中
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 从数据库按规则获取单词
            sql = "INSERT INTO  t_user_suggest(fuid,ftext) VALUES (%s,%s)"
            params = (uid, text)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            cursor.execute(sql, params)
            connection.commit()
    finally:
        connection.close()
    response = {"state": 1}
    return jsonify(response)