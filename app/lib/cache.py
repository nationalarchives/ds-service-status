from flask import request
from flask_caching import Cache

cache = Cache()


def cache_key_prefix():
    """Make a key that includes GET parameters."""
    return f"{request.path}{'+refresh' if 'refresh' in request.args else ''}"
