import random


def generate_captcha(length=4):
    captcha = ''
    for i in range(length):
        num = random.randint(0, 9)
        upper_case = chr(random.randint(65, 90))
        lower_case = chr(random.randint(97, 122))
        char = random.choice([str(num), upper_case, lower_case])
        captcha += char
    return captcha


