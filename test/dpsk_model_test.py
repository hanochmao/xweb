import json

from app.utils.dpsk_model import get_ans_from_dpsk


if __name__ == '__main__':
    sys_content = "you are a IELTS assistant"
    pre_content = {
        "word_list": ['apology', 'sentiment', 'deadline', 'rage', 'Christianity', 'sexuality', 'whip', 'punch', 'icon', 'whale'],
        "requirement": "give a simple sentence for every word in the list",
        "output style": "the result is list, json style, like [{word：xxx, sentence: xxx}]"
    }
    content = json.dumps(pre_content)
    result = get_ans_from_dpsk(sys_content, content)
    print(result)