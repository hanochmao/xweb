import random

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from loguru import logger

from app.db import get_db_connection
import json
from app.utils.qianwen_max_0125 import llm_get_passage
from app.utils.check_pay import check_pay

bp_write = Blueprint('bp_writing', __name__, url_prefix='/writing')
logger.add("./log/writing.log", rotation="10 MB", retention="3 days", level="INFO")

@bp_write.route('/', methods=['GET', 'POST'])
def speaking():
    if not session.get('email'):  # 检查用户是否已登录
        return redirect(url_for('bp_user.login'))
    else:
        return render_template('writing.html')