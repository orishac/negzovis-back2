from flask import Blueprint, request, g

from karmalegoweb.src.preprocessing.preproccessing import preprocessing, preprocessins_results

from karmalegoweb.src.views.error_handlers import validate_args
from karmalegoweb.src import models
from karmalegoweb.src.views.auth import login_required
from karmalegoweb.src import tasks
from karmalegoweb.src.preprocessing.negative_proccessing import negative_preprocessing

bp = Blueprint("preprocessing", __name__, "/")


@bp.route("/preprocess", methods=["POST"])
@login_required
@validate_args(["kl_id"])
def preprocess():
    kl_id = request.form["kl_id"]

    is_negative = models.negative_karma_lego.query.filter_by(id=kl_id).first()
    if is_negative is not None:
        process = negative_preprocessing(kl_id)
        result, _vis_id = process.start_negative()
    else:
        process = preprocessing(kl_id)
        result, _vis_id = process.start()
    message = "Visualization finished, unknown result"
    status = 200
    if result == preprocessins_results.GOOD:
        message = "Visualization has been successfully created"
        status = 200
    elif result == preprocessins_results.EXCEPTION:
        message = "Visualization for Your dataset had failed, a problem occurred in the server"
        status = 500
    elif result == preprocessins_results.MISSING_KARMALEGO:
        message = (
            "Could not find the requested karmalego, this is probably a problem with the server"
        )
        status = 500
    elif result == preprocessins_results.MISSING_STATES:
        message = "Could not find states data for the visualization, this is probably a problem with the server"
        status = 500
    elif result == preprocessins_results.VISUALIZATION_EXISTS:
        message = "A visualization for the requested karmalego already exists"
        status = 400

    if status == 500 or status == 200:
        tasks.send_email(
            message=f"Subject: {message}",
            receiver_email=g.user.Email,
        )

    return message, status
