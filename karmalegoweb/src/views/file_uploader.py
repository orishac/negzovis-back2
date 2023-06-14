import os

from flask import Blueprint, request, make_response, current_app, g

from karmalegoweb.src import models
from karmalegoweb.src.db import get_db
from karmalegoweb.src.views.auth import login_required
from karmalegoweb.src.views.error_handlers import validate_args


# TODO: Switch later
# bp = Blueprint("auth", __name__, url_prefix="/auth")
bp = Blueprint("file_uploader", __name__, url_prefix="")


# https://stackoverflow.com/questions/44727052/handling-large-file-uploads-with-flask
# Note: DropZone will not chunk the file if the file is small enough
@bp.route("/new_upload", methods=["POST"])
@login_required
@validate_args(
    ["dzuuid", "dzchunkindex", "dzchunkbyteoffset", "dztotalchunkcount", "dztotalfilesize"]
)
def upload():
    file = request.files["file"]

    uuid = request.form["dzuuid"]
    current_chunk = int(request.form["dzchunkindex"])
    chunk_offset = int(request.form["dzchunkbyteoffset"])
    total_chunks = int(request.form["dztotalchunkcount"])
    total_file_Size = int(request.form["dztotalfilesize"])

    save_path = os.path.join(current_app.config["TEMP_PATH"], uuid)

    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if current_chunk == 0:
        if os.path.exists(save_path):
            # 400 and 500s will tell dropzone that an error occurred and show an error
            return make_response(("File already exists", 400))
        new_file = models.data_file(uuid=uuid, owner=g.user.Email)
        db = get_db()
        db.session.add(new_file)
        db.session.commit()

    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "ab") as f:
            f.seek(chunk_offset)
            f.write(file.stream.read())
    except OSError:
        # log.exception will include the traceback so we can see what's wrong
        current_app.logger.exception("Could not write to file")
        return make_response(("Not sure why," " but we couldn't write the file to disk", 500))

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != total_file_Size:
            current_app.logger.error(
                f"File {file.filename} was completed, "
                f"but has a size mismatch."
                f"Was {os.path.getsize(save_path)} but we"
                f" expected {request.form['dztotalfilesize']} "
            )
            return make_response(("Size mismatch", 500))
        else:
            # raise Exception("S")
            data_file = models.data_file.query.filter_by(uuid=uuid).first()
            data_file.uploaded_successfully = True
            db = get_db()
            db.session.commit()
            current_app.logger.info(f"File {file.filename} has been uploaded successfully")
    else:
        current_app.logger.debug(
            f"Chunk {current_chunk + 1} of {total_chunks} " f"for file {file.filename} complete"
        )

    return make_response((uuid, 200))
