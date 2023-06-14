import os
from dotenv import load_dotenv

load_dotenv()


# Find the absolute file path to the top level project directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class. Contains default configuration settings + configuration settings applicable to all environments.
    """

    # Default settings
    DEBUG = False
    # TESTING = False
    # WTF_CSRF_ENABLED = True

    # Settings applicable to all environments
    SECRET_KEY = os.getenv("SECRET_KEY", default="A very terrible secret key.")

    # MAIL_USE_TLS = False
    # MAIL_USE_SSL = True
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", default="")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", default="")
    # MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME", default="")
    # MAIL_SUPPRESS_SEND = False

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL ")
    RESULT_BACKEND = os.getenv("RESULT_BACKEND")

    RESTART_SECRET_KEY = os.getenv("RESTART_SECRET_KEY", default="")
    FRONTEND_PATH = os.getenv("FRONTEND_PATH", default="")
    RESTART_SCRIPT_PATH = os.path.join(basedir, "restart.bat")

    ROOT_PATH = basedir
    DATASETS_ROOT = os.path.join(basedir, "Datasets")
    APP_ROOT = os.path.join(basedir, "karmalegoweb")
    TEMP_PATH = os.path.join(basedir, "tmp_storage")
    CLI_PATH = os.path.join(APP_ROOT, "HugoBot/cli.py")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False

    RAW_DATA_HEADER_FORMAT = [
        "EntityID",
        "TemporalPropertyID",
        "TimeStamp",
        "TemporalPropertyValue",
    ]

    VMAP_HEADER_FORMAT = ["Variable ID", "Variable Name", "Description"]
    VMAP_HEADER_FORMAT_2 = ["TemporalPropertyID", "TemporalPropertyName", "Description"]
    GRADIENT_HEADER_FORMAT = [
        "StateID",
        "TemporalPropertyID",
        "Method",
        "BinID",
        "BinLow",
        "BinHigh",
        "BinLowScore",
    ]
    KB_HEADER_FORMAT = [
        "StateID",
        "TemporalPropertyID",
        "TemporalPropertyName",
        "Method",
        "BinID",
        "BinLow",
        "BinHigh",
        "BinLowScore",
        "BinLabel",
    ]
    MODE = "temporal-abstraction"
    DATASET_OR_PROPERTY = "per-dataset"
    PAA_FLAG = "-paa"
    DISCRETIZATION_PREFIX = "discretization"
    GRADIENT_PREFIX = "gradient"
    GRADIENT_FLAG = "-sp"
    KB_PREFIX = "knowledge-based"
    ABSTRACTION_METHOD_CONVERSION = {
        "Equal Frequency": "equal-frequency",
        "Equal Width": "equal-width",
        "SAX": "sax",
        "Persist": "persist",
        "KMeans": "kmeans",
        "Knowledge-Based": "knowledge-based",
        "Gradient": "gradient",
        "TD4C-Cosine": "td4c-cosine",
        "TD4C-Diffmax": "td4c-diffmax",
        "TD4C-Diffsum": "td4c-diffsum",
        "TD4C-Entropy": "td4c-entropy",
        "TD4C-Entropy-IG": "td4c-entropy-ig",
        "TD4C-SKL": "td4c-skl",
    }


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'local.db')}"


# class TestingConfig(Config):
#     TESTING = True
#     WTF_CSRF_ENABLED = False
#     MAIL_SUPPRESS_SEND = True
#     SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "test.db")


class ProductionConfig(Config):
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI", default=f"sqlite:///{os.path.join(basedir, 'prod.db')}"
    )

    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
