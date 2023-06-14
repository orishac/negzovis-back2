import os, ssl

from flask import Flask, request, current_app
from flask_cors import CORS

from celery import Celery
from config import Config

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.RESULT_BACKEND)


def create_app():
    app = Flask(
        __name__,
        static_url_path="",
        static_folder="client\\build",
    )

    # Configure the flask app instance
    ENV = os.getenv("FLASK_ENV", default="development")
    config_type = "config.DevelopmentConfig" if ENV == "development" else "config.ProductionConfig"
    app.config.from_object(config_type)

    setup_cors(app)

    celery.conf.update(app.config)

    initialize_db(app)

    if ENV != "development":
        setup_certification(app)
    configure_logging(app)

    register_blueprints(app)
    register_error_handlers(app)
    register_test_route(app)
    register_update_handlers(app)

    create_directories(app)

    return app


def register_test_route(app):
    @app.route("/ping")
    def test():
        return "ONLINE_UPDATE"


def setup_cors(app):
    # TODO: Check what this is doing
    CORS(app, resources={r"/*": {"origins": "*"}})

    # app.before_first_request(log_inconsistencies)

    # @app.after_request
    # def cors_header(response):
    #     if "Access-Control-Allow-Origin" not in response.headers:
    #         response.headers.add("Access-Control-Allow-Origin", "*")

    #     return response


def initialize_db(app):
    from .src import db

    db.init_app(app)


def create_directories(app):
    os.makedirs(app.config["DATASETS_ROOT"], exist_ok=True)
    os.makedirs(app.config["TEMP_PATH"], exist_ok=True)


def register_update_handlers(app):
    @app.route("/restart", methods=["POST", "GET"])
    def restart():
        current_app.logger.info("Received a restart command")
        secret_token = request.headers.get("X-Gitlab-Token")
        if secret_token == current_app.config["RESTART_SECRET_KEY"]:

            # https://stackoverflow.com/questions/21953835/run-subprocess-and-print-output-to-logging
            import subprocess

            static_path = os.path.join(current_app.config["APP_ROOT"], current_app.static_folder)
            restart_process = subprocess.Popen(
                [
                    current_app.config["RESTART_SCRIPT_PATH"],
                    current_app.config["ROOT_PATH"],
                    current_app.config["FRONTEND_PATH"],
                    static_path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            with restart_process.stdout:
                for line in iter(restart_process.stdout.readline, b""):  # b'\n'-separated lines
                    line_str = line.decode()
                    app.logger.info(line_str[0:-1])

        return "Restarting...."


#     global some_queue
#     some_queue = None

#     @app.route("/restart")
#     def restart():
#         some_queue.put("something")
#         return "Quit"

#     def start_flaskapp(queue):
#         some_queue = queue
#         app.run(port=443)

#     q = queue()
#     p = Process(
#         target=start_flaskapp,
#         args=[
#             q,
#         ],
#     )
#     p.start()
#     while True:  # wathing queue, sleep if there is no call, otherwise break
#         if q.empty():
#             time.sleep(1)
#         else:
#             break
#     p.terminate()  # terminate flaskapp and then restart the app on subprocess
#     args = [sys.executable] + [sys.argv[0]]
#     subprocess.call(args)


def configure_logging(app):
    import logging
    from flask.logging import default_handler
    from logging.handlers import RotatingFileHandler

    if not os.path.exists("logs"):
        os.mkdir("logs")

    # Deactivate the default flask logger so that log messages don't get duplicated
    app.logger.removeHandler(default_handler)

    # Create a file handler object
    file_handler = RotatingFileHandler(
        "logs/karmalegoweb.log", maxBytes=16384, backupCount=20, delay=True
    )

    # Set the logging level of the file handler object so that it logs INFO and up
    file_handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Create a file formatter object
    file_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [in %(filename)s %(lineno)d]: %(message)s"
    )

    # Apply the file formatter object to the file handler object
    file_handler.setFormatter(file_formatter)

    # Add file handler object to the logger
    app.logger.addHandler(file_handler)


def setup_certification(app):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    certfile = os.path.join(app.config["ROOT_PATH"], "server.crt")
    keyfile = os.path.join(app.config["ROOT_PATH"], "server.key")
    context.load_cert_chain(certfile, keyfile)


def register_error_handlers(app):
    from .src.db import get_db

    db = get_db()

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        app.log_exception(e)
        return (
            "Oops, you encountered a server error, try again later or call for technical help",
            500,
        )


# register blueprints
def register_blueprints(app):
    from .src.views import (
        static,
        auth,
        permissions,
        data_mining,
        datasets_files,
        datasets_stats,
        discretization,
        preprocessing,
        tali,
        tutorial,
        upload,
        users,
        visualization,
        manage_datasets,
        file_uploader,
    )

    app.register_blueprint(static.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(permissions.bp)
    app.register_blueprint(data_mining.bp)
    app.register_blueprint(datasets_files.bp)
    app.register_blueprint(datasets_stats.bp)
    app.register_blueprint(discretization.bp)
    app.register_blueprint(preprocessing.bp)
    app.register_blueprint(tali.bp)
    app.register_blueprint(tutorial.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(visualization.bp)
    app.register_blueprint(manage_datasets.bp)
    app.register_blueprint(file_uploader.bp)
