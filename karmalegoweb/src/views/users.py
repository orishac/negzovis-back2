from flask import Blueprint, jsonify, g

from karmalegoweb.src.views.auth import login_required

bp = Blueprint("users", __name__, "")


@bp.route("/getUserName", methods=["GET"])
@login_required
def get_user_name():
    """
    Returns the current user's username.
    :param current_user: The user which is currently logged in.
    :return:
    403 (FORBIDDEN) if:
    # The current user cannot get the information.

    200 (OK) if the user has permissions, returns the first name and last name of the user.
    """

    return f"{g.user.FName} {g.user.LName}"


@bp.route("/getEmail", methods=["GET"])
@login_required
def get_email():
    """
    Returns the current user's email address.
    :param current_user: The user which is currently logged in.
    :return:
    403 (FORBIDDEN) if:
    # The current user cannot get the information.

    200 (OK) if the user has permissions, returns the email of the user.
    """
    return jsonify({"Email": g.user.Email})
