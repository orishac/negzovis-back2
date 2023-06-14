import os
import shutil

from flask import Blueprint, current_app, request
from karmalegoweb.src.manage_data.entities import (
    upload_entities_to_dataset,
    validate_entities,
)

from karmalegoweb.src.views.error_handlers import validate_args
from karmalegoweb.src.db import get_db
from karmalegoweb.src import models
from karmalegoweb.src.views.auth import login_required


# TODO: Switch later
bp = Blueprint("manage_dataset", __name__, url_prefix="")


@bp.route("/updateDetails", methods=["POST"])
@login_required
@validate_args(["dataset_name"])
def update_details():
    dataset_name = request.form["dataset_name"]
    description = request.form["description"] if "description" in request.form else None
    source = request.form["source"] if "source" in request.form else None
    class_0_name = request.form["class_0_name"] if "class_0_name" in request.form else None
    class_1_name = request.form["class_1_name"] if "class_1_name" in request.form else None

    dataset = models.info_about_datasets.query.filter_by(Name = dataset_name).first()
    if dataset is None:
        return "Requested dataset does not exist", 400
    else:
        if description:
            dataset.Description = description
        if source:
            dataset.source = source
        if class_0_name:
            dataset.class_0_name = class_0_name
        if class_1_name:
            dataset.class_1_name = class_1_name
            
    db = get_db()
    db.session.commit()
    return "Dataset updated successfully"

@bp.route("/uploadEntities", methods=["POST"])
@login_required
@validate_args(["dataset_name", "entities_uuid"])
def upload_entities():
    dataset_name = request.form["dataset_name"]
    entities_uuid = request.form["entities_uuid"]

    success, err = validate_entities(dataset_name, entities_uuid)
    if not success:
        return err, 400

    upload_entities_to_dataset(dataset_name, entities_uuid)

    return "Uploaded Successfully"


@bp.route("/deleteDataset", methods=["POST"])
@login_required
@validate_args(["dataset"])
def delete_dataset():
    dataset_name = request.form["dataset"]
    dataset = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
    if dataset is None:
        return "The dataset does not exists", 400

    # From database
    db = get_db()

    models.Visualization.query.filter_by(dataset=dataset_name).delete()

    discretizations = models.discretization.query.filter_by(dataset_Name=dataset_name)
    for discretization in discretizations:
        models.discretization_status.query.filter_by(discretization_id=discretization.id).delete()
        tims = models.karma_lego.query.filter_by(discretization_name=discretization.id)
        if tims is None:
            tims = models.negative_karma_lego.query.filter_by(discretization_name=discretization.id)
        for tim in tims:
            models.karmalego_status.query.filter_by(karmalego_id=tim.id).delete()

            db.session.delete(tim)
        db.session.delete(discretization)
    db.session.delete(dataset)

    db.session.commit()

    dir_path = os.path.join(current_app.config["DATASETS_ROOT"], dataset_name)

    shutil.rmtree(dir_path)

    return "Dataset deleted", 200
