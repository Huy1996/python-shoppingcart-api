from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if identity["isAdmin"]:
                return fn(*args, **kwargs)
            else:
                return {"message": "Invalid admin token"}, 403
        return decorator
    return wrapper