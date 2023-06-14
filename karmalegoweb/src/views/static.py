from flask import Blueprint, send_from_directory, current_app

bp = Blueprint("static", __name__, "/")


@bp.route("/", defaults={"filename": "index.html"})
@bp.route("/<filename>")
def favicon(filename):
    return send_from_directory(current_app.static_folder, filename)


@bp.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(current_app.static_folder, "static/" + path)
