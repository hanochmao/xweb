from loguru import logger

from app.config import Config
from openai import OpenAI
logger.add("./log/dpsk_model.log", rotation="10 MB", retention="3 days", level="INFO")

DPSK_API_KEY = Config.DPSK_API_KEY


# Please install OpenAI SDK first: `pip3 install openai`

def get_ans_from_dpsk(sys_content, content):
    client = OpenAI(api_key=DPSK_API_KEY, base_url="https://api.deepseek.com")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": sys_content},
                {"role": "user", "content": content},
            ],
            stream=False
        )
        result = response.choices[0].message.content
        return result
    except Exception as e:
        logger.info("dpsk get sentence failed: {}".format(e))