import random

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from loguru import logger

from app.db import get_db_connection
import json
from app.utils.qianwen_max_0125 import llm_get_passage

bp_passage = Blueprint('bp_passage', __name__, url_prefix='/passage')

logger.add("./log/passage.log", rotation="10 MB", retention="3 days", level="INFO")
@bp_passage.route('/check')
def check_words():
    if not session.get('email'):  # 检查用户是否已登录
        return redirect(url_for('bp_user.login'))
    else:
        return render_template('passage.html')


@bp_passage.route('/words_check', methods=['POST'])
def words_check():
    uid = session.get('uid')
    connection = get_db_connection()
    word_state = request.json['wordState']
    word_selections = request.json['choice']
    print(word_selections, word_state)
    up_no = 10001
    down_no = 0
    if int(word_selections) != 0:
        up_no = int(word_selections)*1000 + 1
        down_no = (int(word_selections)-1)*1000
    # 单词状态打标
    word_see_log_list = []
    word_is_see = "("
    for word, state in word_state.items():
        word_see_log_dict = {}
        word_see_log_dict['fuid'] = uid
        word_see_log_dict['fword'] = word
        word_see_log_dict['foperation'] = state
        word_see_log_list.append(word_see_log_dict)
        if state == 1:
         word_is_see += "'"+word+"'"+","
    word_is_see += "'the')"

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO t_word_see_log (fuid, fword, foperation) VALUES (%(fuid)s, %(fword)s, %(foperation)s)"
            cursor.executemany(sql, word_see_log_list)
            connection.commit()
            # 从数据库按规则获取单词
            sql = "select fword from t_word_see where frank > %s and frank < %s and fsentence != 'this is the example scentence' and fword not in( select fword from t_word_see_log WHERE fuid = %s and foperation = 1 GROUP BY fword ) order by rand() limit 10"
            params = (down_no, up_no, uid)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            cursor.execute(sql, params)
            result = cursor.fetchall()
            if len(result) != 10:
                word_list = ['it', 'is', 'the', 'end', 'please', 'choose', 'the', 'next', 'new', 'range']
            else:
                word_list = []
                for word in result:
                    word_list.append(word['fword'])
    finally:
        connection.close()
    return jsonify({'newWords': word_list})



@bp_passage.route('/llm',methods=['POST'])
def llm():
    if not session.get('email'):  # 检查用户是否已登录
        return redirect(url_for('bp_user.login'))
    uid = session.get('uid')
    email = session.get('email')
    word_passage_total = get_word_passage_times(uid, email)
    print("单词文章调用次数: %s" % word_passage_total)
    if word_passage_total > 30:
        return
    print(request.json)
    word_selections = request.json['choice']
    up_no = 10001
    down_no = 0
    if int(word_selections) != 0:
        up_no = int(word_selections) * 1000 + 1
        down_no = (int(word_selections) - 1) * 1000
    # 获取陌生单词word_list
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT t_word_see_log.fword FROM t_word_see_log LEFT JOIN t_word_see on (t_word_see_log.fword = t_word_see.fword) WHERE fuid = %s and foperation = 0 and t_word_see.frank > %s and t_word_see.frank < %s GROUP BY fword ORDER BY rand() LIMIT 10"
            params = (uid, down_no, up_no)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            cursor.execute(sql, params)
            result = cursor.fetchall()
            word_list = []
            for word in result:
                word_list.append(word['fword'])
    finally:
        connection.close()
    if len(word_list) != 10:
        word_list = ['dream big, work hard, stay humble.']
    # 请求大模型获取文章
    words = ",".join(word_list)
    print(words)
    dic_content = {
        'list': word_list,
        'style': 'IELTS',
        'requirement': 'use the words in the list I provide, give me a 100 words english passage, the words in the list should be all used.just give me the passage,do not give me other information.'
    }
    content = json.dumps(dic_content)
    # 解析得到文章
    article = llm_get_passage(content).choices[0].message.content
    response = {"text_received": words+"\n\n"+article}
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "insert into t_word_llm_passage(fuid,fwords,fpassage)value(%s,%s,%s)"
            params = (uid, words, article)
            cursor.execute(sql,params)
            connection.commit()
    finally:
        connection.close()
    return jsonify(response)




# 大模型调用次数限制

def get_word_passage_times(uid, email):
    connection = get_db_connection()
    word_passage_total = 0
    try:
        with connection.cursor() as cursor:
            sql = "SELECT fstate FROM t_user_pay WHERE femail = %s"
            params = (email,)
            logger.info(f"Executing SQL: {sql} | Parameters: {params}")
            cursor.execute(sql, params)
            result = cursor.fetchall()
            if len(result) > 0:
                if result[0]['fstate'] == 1:
                    word_passage_total = 0
            else:
                sql = "SELECT COUNT(1)  as fword_passage_total FROM t_word_llm_passage WHERE fuid = %s"
                params = (uid, )
                logger.info(f"Executing SQL: {sql} | Parameters: {params}")
                cursor.execute(sql, params)
                result = cursor.fetchall()
                if len(result) != 0:
                    word_passage_total = result[0]['fword_passage_total']
    finally:
        connection.close()
    return word_passage_total

