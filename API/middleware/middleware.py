from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from datetime import datetime
from bson import ObjectId
from flask import json


def validate_request(*, admin_only=False):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            authorize = identity["isAdmin"] if admin_only else \
                identity["isAdmin"] or identity["_id"] == kwargs.get("user_id")
            if authorize:
                return fn(*args, **kwargs)
            else:
                return {"message": "Unauthorized request"}, 401
        return decorator
    return wrapper


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, arg):
        if isinstance(arg, datetime):
            return arg.isoformat()
        elif isinstance(arg, ObjectId):
            return str(arg)
        else:
            super().default(arg)