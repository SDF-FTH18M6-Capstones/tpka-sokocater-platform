from flask_jwt_extended import get_jwt, get_jwt_identity

from extensions import db
from models import User


def get_authenticated_user():
    """
    Return the authenticated user only if the JWT role
    matches the user's current database role.

    Returns None if the identity is invalid, the user
    does not exist, or the token contains a stale role.
    """

    identity = get_jwt_identity()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None

    user = db.session.get(User, user_id)

    if user is None:
        return None

    token_role = get_jwt().get("role")

    if token_role != user.role:
        return None

    return user
