from flask import Blueprint, request, jsonify, g

from karmalegoweb.src.db import get_db
from karmalegoweb.src import models
from karmalegoweb.src import tasks


# TODO: Switch later
bp = Blueprint("permissions", __name__, url_prefix="")


@bp.route("/loadMail", methods=["GET"])
def load_mail():
    """
    This function loads all of the relevant mail relative to the current user (= the user who sent the request).
    :return:
    500 (INTERNAL SERVER ERROR) if:
    # The server experienced an unintended internal error.

    200 (OK) if all went well, the response contains:
    # myDatasets: A table containing all of the user's datasets.
    # myDatasetsLen: The length of myDatasets.
    # tablesToExplore: A table containing every dataset a user can ask permission to use.
    # tablesToExploreLen: the length of tablesToExplore.
    # myPermissions: A table of datasets for which the current user has permissions.
    # myPermissionsLen: the length of myPermissions
    # askPermissions: A table of datasets for which the current user has requested (but not yet granted) permissions.
    # askPermissionsLen: the length of askPermissions
    # approve A table of datasets that the user owns for which certain users have asked permission for.
    # approveLen: the length of approve
    """
    to_return = {}

    # loads my datasets
    to_return["myDatasets"] = {}
    my_datasets = g.user.my_datasets
    for x, curr_dataset in enumerate(my_datasets):
        to_return["myDatasets"][str(x)] = {
            "Category": curr_dataset.category,
            "DatasetName": curr_dataset.Name,
            "Owner": curr_dataset.Email,
            "PublicPrivate": curr_dataset.public_private,
            "Size": str(curr_dataset.size),
        }
    to_return["myDatasetsLen"] = len(my_datasets)

    # loads all the tables we can explore
    datasets = models.info_about_datasets.query.all()
    to_return["tablesToExplore"] = {}
    for x, curr_dataset in enumerate(datasets):
        if curr_dataset.public_private != "Public":
            full_name = curr_dataset.owner.FName + " " + curr_dataset.owner.LName
            to_return["tablesToExplore"][str(x)] = {
                "Category": curr_dataset.category,
                "DatasetName": curr_dataset.Name,
                "Owner": full_name,
                "PublicPrivate": curr_dataset.public_private,
                "Size": str(curr_dataset.size),
            }
    to_return["tablesToExploreLen"] = len(to_return["tablesToExplore"])

    # loads all the tables we have permission for
    # TODO: All the datasets he owns needs to be added here?
    # TODO: All the public datasets needs to be added here?
    users_permissions = models.Permissions.query.filter_by(Email=g.user.Email).all()
    to_return["myPermissions"] = {}
    for x, curr_record in enumerate(users_permissions):
        curr_dataset = curr_record.dataset
        to_return["myPermissions"][str(x)] = {
            "Category": curr_dataset.category,
            "DatasetName": curr_dataset.Name,
            "Owner": curr_dataset.Email,
            "PublicPrivate": curr_dataset.public_private,
            "Size": str(curr_dataset.size),
        }
    to_return["myPermissionsLen"] = len(to_return["myPermissions"])

    # loads all the permissions we want to get
    # TODO: Shouldn't we return only the requests that was not yet approved?
    user_permissions = models.ask_permissions.query.filter_by(Email=g.user.Email).all()
    to_return["askPermissions"] = {}
    for curr_record in enumerate(user_permissions):
        curr_dataset = curr_record.dataset
        to_return["askPermissions"][str(x)] = {
            "Category": curr_dataset.category,
            "DatasetName": curr_dataset.Name,
            "Owner": curr_dataset.Email,
            "PublicPrivate": curr_dataset.public_private,
            "Size": str(curr_dataset.size),
        }
    to_return["askPermissionsLen"] = len(user_permissions)

    # loads all the requested datasets
    ask_me = models.ask_permissions.query.all()
    to_return["approve"] = {}
    for x, curr_permission in enumerate(ask_me):
        curr_dataset = curr_permission.dataset
        if curr_dataset.Email == g.user.Email:
            to_return["approve"][str(x)] = {
                "Category": curr_dataset.category,
                "DatasetName": curr_dataset.Name,
                "Grantee": curr_permission.Email,
                "Owner": curr_dataset.Email,
                "PublicPrivate": curr_dataset.public_private,
                "Size": str(curr_dataset.size),
            }
    to_return["approveLen"] = len(to_return["approve"])

    to_return["Email"] = g.user.Email

    return jsonify(to_return)


@bp.route("/askPermission", methods=["POST"])
def ask_permission():
    """
    This function handles a permission request for a dataset by the current user.
    :param current_user: The currently logged in user.
    :param dataset: witch dataset we want permission
    :return:
    200 (OK) if all went well.
    """
    # TODO: Check if request already exists

    dataset_name = request.form["dataset"]

    dataset = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
    owner_email = dataset.owner.Email

    new_request = models.ask_permissions(Email=g.user.Email, name_of_dataset=dataset_name)
    db = get_db()
    db.session.add(new_request)
    db.session.commit()

    tasks.send_email(
        message=f"Subject: A user with the email {g.user.Email} has asked for permission to use {dataset_name}",
        receiver_email=owner_email,
    )

    return jsonify({"message": "Permission asked!"})


@bp.route("/acceptPermission", methods=["POST"])
def accept_permission():
    """
    This function handles a permission acceptance for a dataset owned by the current user.
    :param dataset: the name of the dataset to accept, string
    :param userEmail: the email of the user that we want to accept his permission
    :return:
    403 (Forbidden) if:
    # Tried to approve a request to a dataset you do not own.

    404 (Not Found) if:
    # A request with the give details does not exits.

    200 (OK) if all went well.
    """
    dataset_name = request.args.get("dataset")
    user_email = request.args.get("userEmail")

    db = get_db()

    record = models.ask_permissions.query.filter_by(
        Email=user_email, name_of_dataset=dataset_name
    ).first()
    if record is None:
        return jsonify({"message": "Request does not exists"}), 404

    owner_email = record.dataset.owner.Email
    if g.user.Email != owner_email:
        return jsonify({"message": "To approve a request to a dataset, you need to own it"}), 403

    to_add = models.Permissions(Email=user_email, name_of_dataset=dataset_name)
    db.session.add(to_add)
    db.session.delete(record)
    db.session.commit()

    tasks.send_email(
        message=f"Subject: You got permission for dataset {dataset_name}",
        receiver_email=user_email,
    )

    return jsonify({"message": "Permission accepted!"})


@bp.route("/rejectPermission", methods=["POST"])
def reject_permission(current_user):
    """
    This function handles a permission rejection for a dataset owned by the current user.
    :param current_user: The currently logged in user.
    param dataset: the name of the dataset to reject, string
    param userEmail: the email of the user that we want to reject his permission
    :return:
    403 (Forbidden) if:
    # Tried to reject a request to a dataset you do not own.

    404 (Not Found) if:
    # A request with the give details does not exits.


    200 (OK) if all went well.
    """
    dataset_name = request.args.get("dataset")
    user_email = request.args.get("userEmail")

    db = get_db()

    record = models.ask_permissions.query.filter_by(
        Email=user_email, name_of_dataset=dataset_name
    ).first()
    if record is None:
        return jsonify({"message": "Request does not exists"}), 404

    owner_email = record.dataset.owner.Email
    if current_user.Email != owner_email:
        return jsonify({"message": "To reject a request to a dataset, you need to own it"}), 403

    db.session.delete(record)
    db.session.commit()

    tasks.send_email(
        message=f"Subject: Your permission request for Dataset {dataset_name} was rejected",
        receiver_email=user_email,
    )

    return jsonify({"message": "Permission accepted!"})
