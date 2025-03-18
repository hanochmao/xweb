import json

from loguru import logger

from app.db import get_db_connection
from app.utils.dpsk_model import get_ans_from_dpsk

import multiprocessing


def write_sentence_into_db(start_num,end_num):
    connection = get_db_connection()
    for t in range(1):
        print("t:%s"%t)
        start_num = start_num
        end_num = end_num
        with connection.cursor() as cursor:
            # 从数据库按规则获取单词
            sql = "SELECT t_word_see.fword FROM t_word_see WHERE t_word_see.frank > %s and t_word_see.frank <= %s and fsentence != 'this is the example scentence' ORDER BY frank ASC LIMIT 20"
            params = (start_num, end_num)
            logger.info(f"Executing SQL: {sql} || Params: {params}")
            cursor.execute(sql, params)
            result = cursor.fetchall()
            words_string = "[" + ", ".join(f"'{item['fword']}'" for item in result) + "]"
            print(words_string)

            sys_content = "you are a IELTS assistant"
            pre_content = {
                "word_list": words_string,
                "requirement": "give a simple sentence for every word in the list",
                "output style": "the result is list, json style, like [{word:xxx, sentence:xxx}]"
            }
            content = json.dumps(pre_content)
            print(content)
            data = json(get_ans_from_dpsk(sys_content, content))
            print(data)
            sql = "update t_word_see set fsentence = %(sentence)s where fword = %(word)s "
            cursor.executemany(sql, data)
            connection.commit()
            if len(result) < 50:
                return




if __name__ == '__main__':
    processes = []
    for i in range(1):
        start_num = i*2000
        end_num = (i+1)*2000
        process = multiprocessing.Process(target=write_sentence_into_db, args=(start_num, end_num))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
    print("所有进程执行完毕")


