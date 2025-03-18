import json

from loguru import logger

from app.db import get_db_connection

from app.utils.qianwen_max_0125 import llm_get_info
import multiprocessing



def get_voice(user_content):
    system_content = '返回给我对应单词的英式音标和美式音标；音标要带有双斜线；一个音标如果有多个结果，随机给出一个就行，每个音标只返回一个美式音标和一个英式音标，不要返回给我其他的东西；格式json样式，示例是这样的[{"fword":"xxx","famerican_voice":"xxx","fenglish_voice":"xxx"}]'
    result = llm_get_info(system_content, user_content)
    data = json.loads(result.choices[0].message.content)
    return data



def write_into_db(start_num,end_num):
    connection = get_db_connection()
    for t in range(40):
        print("t:%s"%t)
        start_num = start_num
        end_num = end_num
        with connection.cursor() as cursor:
            # 从数据库按规则获取单词
            sql = "SELECT t_word_see.fword FROM t_word_see left join t_word_voice on (t_word_see.fword = t_word_voice.fword) WHERE t_word_see.frank > %s and t_word_see.frank <= %s and t_word_voice.fword is null ORDER BY frank ASC LIMIT 50"
            params = (start_num, end_num)
            logger.info(f"Executing SQL: {sql} || Params: {params}")
            cursor.execute(sql, params)
            result = cursor.fetchall()
            words_string = "[" + ", ".join(f"'{item['fword']}'" for item in result) + "]"
            print(words_string)
            data = get_voice(words_string)
            print(data)
            sql = "INSERT INTO t_word_voice (fword, famerican_voice,fenglish_voice) VALUES (%(fword)s, %(famerican_voice)s, %(fenglish_voice)s)"
            cursor.executemany(sql, data)
            connection.commit()
            if len(result) < 50:
                return




if __name__ == '__main__':
    processes = []
    for i in range(5):
        print(i)
        start_num = i*2000
        end_num = (i+1)*2000
        process = multiprocessing.Process(target=write_into_db, args=(start_num, end_num))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print("所有进程执行完毕")