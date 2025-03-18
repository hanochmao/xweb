import time
from flask import Blueprint, render_template, session, redirect, url_for
from loguru import logger


logger.add("./log/vip.log", rotation="10 MB", retention="7 days", level="INFO")

bp_vip = Blueprint('bp_vip', __name__, url_prefix='/vip')


@bp_vip.route('/')
def user_vip():
    if not session.get('email'):  # 检查用户是否已登录
        return redirect(url_for('bp_user.login'))
    return render_template("vip.html")