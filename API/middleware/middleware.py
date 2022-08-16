from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def validate_request(*, admin_only=False):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            authorize = identity["isAdmin"] if admin_only else \
                identity["isAdmin"] or identity["_id"] == kwargs["user_id"]
            if authorize:
                return fn(*args, **kwargs)
            else:
                return {"message": "Unauthorized request"}, 401
        return decorator
    return wrapper

