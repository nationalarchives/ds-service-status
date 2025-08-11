from flask import Blueprint

bp = Blueprint("status", __name__)

from app.status import routes  # noqa: E402,F401
