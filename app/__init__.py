from flask import Flask, session, g
from .config import Config
from app.blueprints.home import bp_home
from app.blueprints.user import bp_user
from app.blueprints.statis import bp_statis
from app.blueprints.passage import bp_passage
from app.blueprints.forgetpw import bp_forgetpw
from app.blueprints.speaking import bp_sk
from app.blueprints.future import bp_future
from app.blueprints.vip import bp_vip
from app.blueprints.check import bp_check
from app.blueprints.write import bp_write

from app.smail import mail
import logging
from logging.handlers import RotatingFileHandler


def create_app():
    app = Flask(__name__, static_folder='static')
    # 配置日志记录器
    log_file = 'app_info.log'
    log_level = logging.ERROR  # 根据需求设置日志级别，例如 DEBUG, INFO, WARNING, ERROR, CRITICAL

    # 创建日志处理器（带日志轮换）
    handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    handler.setLevel(log_level)

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # 将处理器添加到应用的日志记录器中
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    app.config.from_object(Config)
    # 注册蓝图
    app.register_blueprint(bp_home)
    app.register_blueprint(bp_user)
    app.register_blueprint(bp_statis)
    app.register_blueprint(bp_passage)
    app.register_blueprint(bp_forgetpw)
    app.register_blueprint(bp_sk)
    app.register_blueprint(bp_future)
    app.register_blueprint(bp_vip)
    app.register_blueprint(bp_check)
    app.register_blueprint(bp_write)
    mail.init_app(app)
    return app



