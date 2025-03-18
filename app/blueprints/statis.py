from datetime import date, timedelta, datetime

from flask import Blueprint, render_template, jsonify, session, redirect, url_for
from app.db import get_db_connection
from loguru import logger



logger.add("./log/statis.log", rotation="10 MB", retention="7 days", level="INFO")



bp_statis = Blueprint('bp_statis', __name__, url_prefix='/statis')


@bp_statis.route('/', methods=['GET'])
def statis():
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('bp_statis.login'))
    return render_template('statis.html')



@bp_statis.route('/today', methods=['GET'])
def today():
    time_today = date.today()
    time_tomorrow = time_today + timedelta(days=1)
    time_weekly = time_tomorrow - timedelta(days=7)
    seven_data_category = [(datetime.now() - timedelta(days=6 - i)).strftime('%Y-%m-%d') for i in range(7)]
    print(seven_data_category)

    print(time_today, time_tomorrow)
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('bp_statis.login'))
    db = get_db_connection()
    words_num_list = []
    passage_num_list = []
    with db.cursor() as cursor:
        # 查询单词
        sql = "SELECT count(1) as ftotal,COALESCE(SUM(foperation), 0) as fknow FROM t_word_see_log WHERE fuid = %s and fupdate_time >= %s and fupdate_time < %s"
        params = (uid, time_today, time_tomorrow)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        print(result)
        words_num_list.append(result[0]['ftotal'])
        words_num_list.append(result[0]['fknow'])
        # 查询文章
        sql = "SELECT count(1) as ftotal FROM t_word_llm_passage WHERE fuid = %s and fupdate_time >= %s and fupdate_time < %s"
        params = (uid, time_today, time_tomorrow)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        print(result)
        passage_num_list.append(result[0]['ftotal'])

        sql = "SELECT count(1) as ftotal FROM t_ielts_speaking_question_log WHERE fuid = %s and ftime >= %s and ftime < %s"
        params = (uid, time_today, time_tomorrow)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        print(result)
        passage_num_list.append(result[0]['ftotal'])


        sql = "SELECT date(fupdate_time) as fdate, count(1) as ftotal, COALESCE(SUM(foperation), 0) as fknow FROM t_word_see_log WHERE fuid = %s and fupdate_time >= %s and fupdate_time < %s group by date(fupdate_time) ORDER BY date(fupdate_time)"
        params = (uid, time_weekly, time_tomorrow)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        print(result)
        result_dict_total = {item['fdate'].strftime('%Y-%m-%d'): item['ftotal'] for item in result}
        result_dict_know = {item['fdate'].strftime('%Y-%m-%d'): item['fknow'] for item in result}
        seven_word_browsed = []
        seven_word_mastered = []
        for category in seven_data_category:
            seven_word_browsed.append(result_dict_total.get(category, 0))
            seven_word_mastered.append(result_dict_know.get(category, 0))
        print(seven_word_browsed)
        print(seven_word_mastered)


        sql = "SELECT date(fupdate_time) as fdate, count(1) as ftotal FROM t_word_llm_passage WHERE fuid = %s and fupdate_time >= %s and fupdate_time < %s group by date(fupdate_time) ORDER BY date(fupdate_time)"
        params = (uid, time_weekly, time_tomorrow)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        print(result)
        result_dict_ps_words = {item['fdate'].strftime('%Y-%m-%d'): item['ftotal'] for item in result}

        sql = "SELECT date(ftime) as fdate, count(1) as ftotal FROM t_ielts_speaking_question_log WHERE fuid = %s and ftime >= %s and ftime < %s group by date(ftime) ORDER BY date(ftime)"
        params = (uid, time_weekly, time_tomorrow)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        print(result)
        result_dict_ps_speaking = {item['fdate'].strftime('%Y-%m-%d'): item['ftotal'] for item in result}

        seven_word_browsed = []
        seven_word_mastered = []
        seven_ps_words = []
        seven_ps_speaking = []
        for category in seven_data_category:
            seven_word_browsed.append(result_dict_total.get(category, 0))
            seven_word_mastered.append(result_dict_know.get(category, 0))
            seven_ps_words.append(result_dict_ps_words.get(category, 0))
            seven_ps_speaking.append(result_dict_ps_speaking.get(category, 0))
        print(seven_word_browsed)
        print(seven_word_mastered)
        print(seven_ps_words)
        print(seven_ps_speaking)



    words_category_list = ["browsed", "mastered"]
    passage_category_list = ["words-gen-passage", "speaking-gen-passage"]

    seven_words = [
        {
            "name": 'browsed',
            "data": seven_word_browsed
        },
        {
            "name": 'mastered',
            "data": seven_word_mastered
        }
    ]
    seven_passages = [
        {
            "name": 'words_gen-passage',
            "data": seven_ps_words
        },
        {
            "name": 'speaking-gen-passage',
            "data": seven_ps_speaking
        }
    ]
    data = {
        "words_category": words_category_list,
        "words_num": words_num_list,
        "passage_category": passage_category_list,
        "passage_num": passage_num_list,
        "seven_data": {
            "category": seven_data_category,
            "seven_words": seven_words,
            "seven_passages": seven_passages
        }
    }
    return jsonify(data)


@bp_statis.route('/login')
def login():
    return render_template('login.html')


@bp_statis.route('/future')
def future():
    return render_template('future.html')


@bp_statis.route('/data', methods=['GET', 'POST'])
def statis_data():
    # 示例数据，可以从数据库或其他来源获取
    data = {
        "words_category": ["browsed", "", "mastered"],
        "words_num": [256, 145],
        "passage_category": ["words-gen-passage", "speaking-gen-passage"],
        "passage_num": [45, 66],
    }
    return jsonify(data)


@bp_statis.route('/data/words', methods=['GET', 'POST'])
def statis_data_words():
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('bp_statis.login'))
    # 获取words数据
    return render_template('statis_data_words.html')



@bp_statis.route('/overall', methods=['GET', 'POST'])
def statis_overall():
    return render_template('statis_overall.html')



@bp_statis.route('/data/overall', methods=['GET', 'POST'])
def statis_overall_words():
    db = get_db_connection()
    uid = session.get('uid')
    total_words = 1000
    group = ["1-1000", "1001-2000", "2001-3000", "3001-4000", "4001-5000", "5001-6000", "6001-7000", "7001-8000", "8001-9000", "9001-10000"]
    mastered_words_list = {}
    with db.cursor() as cursor:
        sql = "SELECT frank_category,SUM(foperation) as fmastered from ( SELECT CASE WHEN t_word_see.frank >= 1 AND t_word_see.frank < 1001 THEN '1-1000' WHEN t_word_see.frank >= 1001 AND t_word_see.frank < 2001 THEN '1001-2000' WHEN t_word_see.frank >= 2001 AND t_word_see.frank < 3001 THEN '2001-3000' WHEN t_word_see.frank >= 3001 AND t_word_see.frank < 4001 THEN '3001-4000' WHEN t_word_see.frank >= 4001 AND t_word_see.frank < 5001 THEN '4001-5000' WHEN t_word_see.frank >= 5001 AND t_word_see.frank < 6001 THEN '5001-6000' WHEN t_word_see.frank >= 6001 AND t_word_see.frank < 7001 THEN '6001-7000' WHEN t_word_see.frank >= 7001 AND t_word_see.frank < 8001 THEN '7001-8000' WHEN t_word_see.frank >= 8001 AND t_word_see.frank < 9001 THEN '8001-9000' WHEN t_word_see.frank >= 9001 AND t_word_see.frank < 10001 THEN '9001-10000' ELSE '0' END AS frank_category, case when sum(t_word_see_log.foperation) > 0 then 1 else 0 end as foperation FROM t_word_see_log LEFT JOIN t_word_see on (t_word_see_log.fword = t_word_see.fword) WHERE t_word_see_log.fuid = %s group by frank) as t group by frank_category"
        params = (uid,)
        logger.info(f"Executing SQL: {sql} | Parameters: {params}")
        cursor.execute(sql, params)
        result = cursor.fetchall()
        print(result)
        data = []
        for category in group:
            cat_dict = {
                "group": category,
                "total_words": total_words,
                "mastered_words": 0
            }
            for item in result:
                if category == item['frank_category']:
                    cat_dict['mastered_words'] = item['fmastered']
            data.append(cat_dict)
        print(data)
    return jsonify(data)