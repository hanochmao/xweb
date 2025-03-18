import json
from openai import OpenAI


def llm_get_passage(content):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="xxx",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", # 填写DashScope服务的base_url
    )
    completion = client.chat.completions.create(
        model="qwen-max-0125",  # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
                {'role': 'system', 'content': 'You are a IELTS assistant.give me a passage, the format is JSON'},
                {'role': 'user', 'content': content},
        ],
        response_format={"type": "json_object"},
        )
    return completion


def llm_get_info(system_content, user_content):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="xxx",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务的base_url
    )
    completion = client.chat.completions.create(
        model="qwen-max-0125",
        # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content},
        ],
        response_format={"type": "json_object"},
    )
    return completion


if __name__ == '__main__':
    dic_content = {
        'list': ['you', 'helpful', 'think', 'car'],
        'style': 'IELTS',
        'requirement': 'use the words in the list I provide, give me a 100 words english passage, the words in the list should be all used.just give me the passage,do not give me other information.'
    }
    content = json.dumps(dic_content)
    print(llm_get_passage(content).choices[0].message.content)

