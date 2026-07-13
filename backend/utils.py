from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User


def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            try:
                user_id = int(identity)
            except (TypeError, ValueError):
                return jsonify({"message": "Invalid token"}), 401

            user = User.query.get(user_id)
            if not user or user.role != required_role or not user.is_active or user.is_blacklisted:
                return jsonify({"message": "Unauthorized access"}), 403
            return fn(user, *args, **kwargs)
        return wrapper
    return decorator