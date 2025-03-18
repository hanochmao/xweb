import requests


def llm_get_passage(content):
    api_key = 'xxx'
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {api_key}'}
    body = {
        'model': 'qwen-turbo',
        "input": {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": content   # 这里替换不同的问题
                }
            ]
        },
        "parameters": {
            "result_format": "message"
        }
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()
