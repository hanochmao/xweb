import json
from app.utils.http_llm import llm_get_passage

word_list = ['car', 'sun', 'water', 'bird', 'fish', 'mountain', 'sea', 'wind']

dic_content = {
    'list': word_list,
    'style': 'IELTS',
    'requirement': 'use the words in the list I provide, give me a 100 words english passage, the words in the list should be all used.'
}

content = json.dumps(dic_content)
passage = llm_get_passage(content)['output']['choices'][0]['message']['content']
print(passage)