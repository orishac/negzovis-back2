import click
from functools import wraps

from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

global db
db = None


def db_initialized(f):
    """
    Raises an error if the DB is not initialized
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if db is None:
            raise RuntimeError("DB is access before initialized")
        return f(*args, **kwargs)

    return decorated


def init_app(app):
    global db
    db = SQLAlchemy(app)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@db_initialized
def get_db() -> SQLAlchemy:
    return db


@db_initialized
def close_db(e=None):
    return db.session.close()


@db_initialized
def init_db():
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
