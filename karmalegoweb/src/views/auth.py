import functools
import datetime

from flask import Blueprint, request, jsonify, make_response, current_app, g, abort
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import re

from karmalegoweb.src.db import get_db
from karmalegoweb.src import models
from karmalegoweb.src import tasks

# TODO: Switch later
# bp = Blueprint("auth", __name__, url_prefix="/auth")
bp = Blueprint("auth", __name__, url_prefix="")


@bp.route("/register", methods=["POST"])
def register():
    """
    This route handles registration of a new user in the system
    :param firstName- the firstname of the user, string
    :param lastName - the last name of the user, string
    :param institute - his institute, string
    :param degree - his degree, string
    :param - his email, string
    :param pass - the password that he wants for himself, string
    :return:
    400 (BAD REQUEST) if:
    # the email is not valid
    # the email already exists
    # an unexpected error occurred

    409 (CONFLICT) if:
    # the server cannot send an email

    200 (OK) if everything went good
    """

    data = request.form
    if "Email" not in data or "Password" not in data:
        return make_response("Email and password are needed", 400)

    if check_email(data["Email"]):
        return jsonify({"message": "Email is not valid"}), 400

    double_user = models.Users.query.filter_by(Email=data["Email"]).first()
    if double_user:
        return jsonify({"message": "There is already a user with that Email"}), 400

    hashed_password = generate_password_hash(data["Password"], method="sha256")
    new_user = models.Users(
        FName=data["Fname"],
        LName=data["Lname"],
        degree=data["Degree"],
        institute=data["Institute"],
        Email=data["Email"],
        Password=hashed_password,
    )

    db = get_db()
    db.session.add(new_user)
    db.session.commit()

    tasks.send_email(f"Welcome {new_user.FName} to Karma Lego Web", new_user.Email)

    return jsonify({"message": "Welcome!"})


@bp.route("/login", methods=["POST"])
def login():
    """
    This route handles a login attempt of an apparent user to the system
    send with key value like x-access-token in the header
    :param: Email - the email of the user, string
    :param: password: the password of the user
    :return:
    400 (BAD REQUEST) if:
    # one of the fields was left empty
    # the email is incorrect
    # the password doesn't match the email

    200 (OK) if everything went good, also returns a token (jwt) that allows a user access to the website
    """
    db = get_db()

    data = request.form
    if "Email" not in data or "Password" not in data:
        return make_response("Email and password are needed", 400)

    # Checks credentials
    user = models.Users.query.filter_by(Email=data["Email"]).first()
    if not user:
        db.session.close()
        return make_response({"message": "Email or password are not correct"}, 400)

    if not check_password_hash(user.Password, data["Password"]):
        return jsonify({"message": "Email or password are not correct"}), 400

    token = jwt.encode(
        {
            "Email": user.Email,
            "exp": (datetime.datetime.utcnow() + datetime.timedelta(minutes=3000)),
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return jsonify({"token": token})


@bp.before_app_request
def load_logged_in_user():
    g.user = None

    if "x-access-token" in request.headers:
        token = request.headers["x-access-token"]
        if token:
            try:
                data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
                email = data["Email"]
                current_user = models.Users.query.filter_by(Email=email).first()

                g.user = current_user
            except jwt.exceptions.ExpiredSignatureError:
                pass
            except jwt.exceptions.DecodeError:
                pass


def login_required(view):
    """
    this function checks if the user is connected by checking the token
    :param f: the token
    :return:
    """

    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return "Required authentication", 401

        return view(*args, **kwargs)

    return wrapped_view


def check_email(email):
    return not re.search("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email)
