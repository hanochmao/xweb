import json
import sys

from openai import OpenAI
from app.db import get_db_connection

def llm_common_use(api_key, base_url, role, model, content):
    client=OpenAI(
        # 如果没有配置环境变量，请用百炼API Key替换：api_key="sk-xxx"
        api_key=api_key,
        base_url=base_url
    )
    completion = client.chat.completions.create(
        model=model,  # 此处以 qwq-32b 为例，可按需更换模型名称
        messages=[
            {
                "role": role,
                "content": content
            }
        ],
        stream=True,
    )
    return completion


def read_into_table():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # 从数据库按规则获取单词
        sql = "SELECT fword FROM t_word_failed_6000 where fsentence is null order by fword limit 10"
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) < 1:
            sys.exit()
        words_string = "[" + ", ".join(f"'{item['fword']}'" for item in result) + "]"
        return words_string

def write_into_table(content):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        data = content
        sql = "UPDATE t_word_failed_6000 set fsentence = %(fsentence)s where fword = %(fword)s"
        cursor.executemany(sql, data)
        connection.commit()



if __name__ == "__main__":
    api_key = "xxx"
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    role = "user"
    model = "qwq-plus"
    for i in range(100):
        print(i)
        word_string = read_into_table()
        content = 'list:%s,用list里面的单词，每个单词给出一个英文例句，格式json样式，示例是这样的[{"fword":"xxx","fsentence":"xxx"}]，不要返回给我其他的东西，不要带json这个单词' % word_string
        # print(content)
        completion = llm_common_use(api_key, base_url, role, model, content)
        reasoning_content = ""  # 定义完整思考过程
        answer_content = ""  # 定义完整回复
        is_answering = False  # 判断是否结束思考过程并开始回复
        for chunk in completion:
            # 如果chunk.choices为空，则打印usage
            if not chunk.choices:
                print("\nUsage:")
                print(chunk.usage)
            else:
                delta = chunk.choices[0].delta
                # 打印思考过程
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                    # print(delta.reasoning_content, end='', flush=True)
                    reasoning_content += delta.reasoning_content
                else:
                    # 开始回复
                    if delta.content != "" and is_answering is False:
                        # print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                        is_answering = True
                    # 打印回复过程
                    # print(delta.content, end='', flush=True)
                    answer_content += delta.content
        answer_content = json.loads(answer_content)
        write_into_table(answer_content)





