from flask import Blueprint

bp = Blueprint("blogs", __name__)


@bp.route("/")
def index():
    return "Hello"
