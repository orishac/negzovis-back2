import smtplib, ssl, os
from flask import current_app

from karmalegoweb.src.discretization.post_discretization import (
    name_bins,
    process_kl_input,
    validate_file_creation,
)

from karmalegoweb import celery
from karmalegoweb.src import models
from karmalegoweb.src.db import get_db


# TODO: Log raised exceptions without manually using try except every where


def send_email(message, receiver_email):
    __send_email_task(message, receiver_email)
    # __send_email_task.apply_async(args=[message, receiver_email])


@celery.task(name="karmalegoweb.tasks.send_email")
def __send_email_task(message, receiver_email):
    smtp_server = current_app.config["MAIL_SERVER"]  # For SSL
    port = current_app.config["MAIL_PORT"]

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
            server.sendmail(current_app.config["MAIL_USERNAME"], receiver_email, message)

    except Exception as e:
        current_app.log_exception(e)


@celery.task(name="karmalegoweb.tasks.discretization")
def discretization(
    request_files_names,
    is_per_property,
    is_sequential,
    dataset_name,
    disc_id,
    binsNames,
    user_email,
    command,
    disc_path,
    dataset_path,
):
    try:
        os.system(command)
        process_kl_input(disc_path)

        if is_sequential:
            success = True
        else:
            name_bins(dataset_path, disc_path, request_files_names, is_per_property, binsNames)
            success = validate_file_creation(disc_path)
        
    except Exception as e:
        success = False
        current_app.log_exception(e)

    finally:
        run = models.discretization_status.query.filter_by(discretization_id=disc_id).first()
        db = get_db()
        run.finished = True
        run.success = success
        db.session.commit()

        success_msg = (
            f'Subject: A discretization for Your dataset "'
            + dataset_name
            + '" has been successfully created'
        )
        fail_msg = (
            f'Subject: A problem has occurred with the discretization you queued for Your dataset "'
            + dataset_name
            + '". Please try again.'
        )
        __send_email_task(
            message=success_msg if success else fail_msg,
            receiver_email=user_email,
        )
