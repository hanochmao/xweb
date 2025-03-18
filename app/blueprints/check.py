import random

from flask import Blueprint, render_template, jsonify, session, redirect, url_for, request
from loguru import logger

from app.db import get_db_connection

bp_check = Blueprint('bp_check', __name__, url_prefix='/check')


# 模拟的单词数据
words_data = [
    {"word": "apple", "meaning": "苹果", "example": "I ate an apple for breakfast."},
    {"word": "banana", "meaning": "香蕉", "example": "She likes to eat bananas with peanut butter."},
    {"word": "cherry", "meaning": "樱桃", "example": "The cherry blossoms are beautiful in spring."},
    {"word": "date", "meaning": "日期", "example": "What's the date today?"},
    {"word": "elderberry", "meaning": "接骨木莓", "example": "Elderberry is often used in herbal medicine."},
    {"word": "fig", "meaning": "无花果", "example": "He brought a basket of fresh figs."},
    {"word": "grape", "meaning": "葡萄", "example": "We made grape juice from the harvest."},
    {"word": "honeydew", "meaning": "蜜瓜", "example": "Honeydew melon is very refreshing in summer."},
    {"word": "kiwi", "meaning": "猕猴桃", "example": "She added kiwi to the fruit salad."},
    {"word": "lemon", "meaning": "柠檬", "example": "He squeezed a lemon into his tea."},
    {"word": "mango", "meaning": "芒果", "example": "Mango is my favorite tropical fruit."},
    {"word": "nectarine", "meaning": "油桃", "example": "Nectarines are similar to peaches but without the fuzz."},
    {"word": "orange", "meaning": "橙子", "example": "She drank a glass of fresh orange juice."},
    {"word": "papaya", "meaning": "木瓜", "example": "Papaya is rich in vitamins and enzymes."},
    {"word": "quince", "meaning": "榅桲", "example": "Quince is often used to make jams and jellies."},
    {"word": "raspberry", "meaning": "树莓", "example": "She picked raspberries from the garden."},
    {"word": "strawberry", "meaning": "草莓", "example": "Strawberries are delicious with whipped cream."},
    {"word": "tangerine", "meaning": "橘子", "example": "He peeled a tangerine for a quick snack."},
    {"word": "ugli", "meaning": "丑橘", "example": "Ugli fruit is a hybrid of grapefruit and tangerine."},
    {"word": "watermelon", "meaning": "西瓜", "example": "We enjoyed watermelon at the picnic."}
]

@bp_check.route('/')
def words_detail():
    if not session.get('email'):  # 检查用户是否已登录
        return redirect(url_for('bp_user.login'))
    return render_template('words_detail.html')

@bp_check.route('/words/batch', methods=['GET', 'POST'])
def get_words_batch():
    connection = get_db_connection()
    uid = session.get('uid')
    word_selections = request.json['range_option']
    word_state = request.json['word_state']
    print(word_selections,word_state)

    if word_selections is None:
        up_no = 10001
        down_no = 0
        try:
            with connection.cursor() as cursor:
                # 从数据库按规则获取单词
                sql = "select fword,fmeaning,fsentence as fscentence,famerican_voice,fenglish_voice from t_word_see where frank > %s and frank < %s and fsentence != 'this is the example scentence' and fword not in( select fword from t_word_see_log WHERE fuid = %s and foperation = 1 GROUP BY fword ) order by rand() limit 10"
                params = (down_no, up_no, uid)
                logger.info(f"Executing SQL: {sql} | Parameters: {params}")
                cursor.execute(sql, params)
                result = cursor.fetchall()

        finally:
            connection.close()
        return jsonify(result)
    else:
        up_no = 10001
        down_no = 0
        if int(word_selections) != 0:
            up_no = int(word_selections) * 1000 + 1
            down_no = (int(word_selections) - 1) * 1000

        for item in word_state:
            item['fuid'] = uid
            item['fword'] = item.pop('word')
            item['foperation'] = 0 if item.pop('selected') is False else 1

        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO t_word_see_log (fuid, fword, foperation) VALUES (%(fuid)s, %(fword)s, %(foperation)s)"
                cursor.executemany(sql, word_state)
                connection.commit()
                # 从数据库按规则获取单词
                sql = "select fword,fmeaning,fsentence as fscentence,famerican_voice,fenglish_voice from t_word_see where frank > %s and frank < %s and fsentence != 'this is the example scentence' and fword not in( select fword from t_word_see_log WHERE fuid = %s and foperation = 1 GROUP BY fword ) order by rand() limit 10"
                params = (down_no, up_no, uid)
                logger.info(f"Executing SQL: {sql} | Parameters: {params}")
                cursor.execute(sql, params)
                result = cursor.fetchall()

        finally:
            connection.close()
        return jsonify(result)