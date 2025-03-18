from loguru import logger

from app import create_app
from flask import session, g
import os

logger.add("./log/run.log", rotation="10 MB", retention="3 days", level="INFO")

app = create_app()


# 定义一个全局变量
@app.context_processor
def inject_global_variable():
    if os.environ.get('FLASK_ENV') == 'development':
        base_url = "http://127.0.0.1:5000"
    else:
        base_url = "http://www.eggmuscle.cn"
    logger.info("base_url={}".format(base_url))
    return dict(home_addr=base_url)


@app.before_request
def before_request():
    email = session.get('email')
    username = session.get('user_name')
    if email:
        user = {
            'email': email,
            'username': username
        }
        setattr(g, 'user', user)
    else:
        setattr(g, 'user', None)


@app.context_processor
def context_processor():
    return {'user': g.user}


if __name__ == "__main__":
    app.run()