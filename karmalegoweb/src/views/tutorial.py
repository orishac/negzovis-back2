import os

from flask import Blueprint, request, send_file, jsonify, current_app

bp = Blueprint("tutorial", __name__, "/")


@bp.route("/getExampleFile", methods=["GET"])
def get_example_file():
    """
    Returns a requested example file for what an acceptable user-submitted file should look like.
    param file: the csv file
    :return:
    404 (NOT FOUND) if:
    # The requested file cannot be found in the server.

    200 (OK) if the file exists, returns the requested example file
    """
    try:
        file_name = request.args.get("file")
        file_path = os.path.join(current_app.root_path, "Resources", file_name + ".csv")
        return send_file(file_path), 200
    except FileNotFoundError:
        return jsonify({"message": "the request file cannot be found."}), 400
