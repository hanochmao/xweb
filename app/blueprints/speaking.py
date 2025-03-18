import random

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from loguru import logger

from app.db import get_db_connection
import json
from app.utils.qianwen_max_0125 import llm_get_passage
from app.utils.check_pay import check_pay

bp_sk = Blueprint('bp_skeaking', __name__, url_prefix='/speaking')
logger.add("./log/speaking.log", rotation="10 MB", retention="3 days", level="INFO")

@bp_sk.route('/', methods=['GET', 'POST'])
def speaking():
    if not session.get('email'):  # 检查用户是否已登录
        return redirect(url_for('bp_user.login'))
    else:
        return render_template('speaking.html')


@bp_sk.route('/back', methods=['GET', 'POST'])
def sk_back():
    if not session.get('email'):
        return redirect(url_for('bp_user.login'))
    else:
        qs = request.json['qs_value']
        text = request.json['text_value']
        print(qs, text)

        if qs == "here is the question":
            qs_no = 1
        else:
            qs_no = int(qs.split(":")[0].replace("Question", ""))
            qs_no -= 1
        if qs_no < 1:
            qs_no = 1
        # 数据库查询题目和预设的提示信息
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT fid,fquestion,fre_prompt FROM t_ielts_speaking_question WHERE fid = %s"
                params = (qs_no,)
                cursor.execute(sql, params)
                result = cursor.fetchall()
                question = "Question" + str(result[0]["fid"]) + ":" + result[0]["fquestion"]
                prompt_info = result[0]["fre_prompt"]
        finally:
            connection.close()
        response = {"question": question, "prompt_info": prompt_info}
        return jsonify(response)


@bp_sk.route('/next', methods=['GET', 'POST'])
def sk_next():
    print("start")
    if not session.get('email'):
        return redirect(url_for('bp_user.login'))
    else:
        """
        email = session.get('email')
        state = check_pay(email)
        if state == 0:
            return redirect(url_for('bp_user.login'))
        qs = request.json['qs_value']
        text = request.json['text_value']
        print(qs, text)
        """
        qs = request.json['qs_value']
        if qs == "here is the question":
            qs_no = 1
        else:
            qs_no = int(qs.split(":")[0].replace("Question", ""))
            qs_no += 1
        if qs_no > 75:
            qs_no = 1
        # 数据库查询题目和预设的提示信息
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT fid,fquestion,fre_prompt FROM t_ielts_speaking_question WHERE fid = %s"
                params = (qs_no,)
                cursor.execute(sql, params)
                result = cursor.fetchall()
                question = "Question" + str(result[0]["fid"]) + ":" + result[0]["fquestion"]
                prompt_info = result[0]["fre_prompt"]
        finally:
            connection.close()
        response = {"question": question, "prompt_info": prompt_info}
        return jsonify(response)




@bp_sk.route('/generate', methods=['GET', 'POST'])
def sk_generate():
    if not session.get('email'):
        return redirect(url_for('bp_user.login'))
    else:
        uid = session.get('uid')
        email = session.get('email')
        speaking_passage_total = get_speaking_passage_times(uid,email)
        print("口语话题文章调用次数：%s" % speaking_passage_total)
        if speaking_passage_total > 30:
            return
        qs = request.json['qs_value']
        qs_no = int(qs.split(":")[0].replace("Question", ""))
        text = request.json['text_value']
        # 请求大模型得到答案
        dic_content = {
            'question': qs,
            "prompt_info": text,
            'style': 'IELTS Speaking',
            'requirement': 'give me a oral english passage, just give me the passage,do not give me other information.'
        }
        content = json.dumps(dic_content)
        # 解析得到文章
        article = llm_get_passage(content).choices[0].message.content
        response = {"passage": article}
        # 日志写入数据库
        connection = get_db_connection()
        uid = session.get('uid')
        try:
            with connection.cursor() as cursor:
                sql = "insert into t_ielts_speaking_question_log(fuid,fquestion_no,fuser_prompt,fpassage)value(%s,%s,%s,%s)"
                params = (uid, qs_no, text, article)
                cursor.execute(sql, params)
                connection.commit()
        finally:
            connection.close()
        return jsonify(response)


def get_speaking_passage_times(uid,email):
    connection = get_db_connection()
    speaking_passage_total = 0
    try:
        with connection.cursor() as cursor:
            sql = "SELECT fstate FROM t_user_pay WHERE femail = %s"
            params = (email,)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            cursor.execute(sql, params)
            result = cursor.fetchall()
            if len(result) > 0:
                if result[0]['fstate'] == 1:
                    speaking_passage_total = 0
            else:
                sql = "SELECT COUNT(1)  as fspeaking_passage_total FROM t_ielts_speaking_question_log WHERE fuid = %s"
                params = (uid, )
                logger.info(f"Executing SQL: {sql} | Parameters: {params}")
                cursor.execute(sql, params)
                result = cursor.fetchall()
                if len(result) != 0:
                    speaking_passage_total = result[0]['fspeaking_passage_total']
    finally:
        connection.close()
    return speaking_passage_total