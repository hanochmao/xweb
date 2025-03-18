from flask import Blueprint, render_template

bp_future = Blueprint('bp_future', __name__, url_prefix='/future')

@bp_future.route('/')
def future():
    return render_template("future.html")
