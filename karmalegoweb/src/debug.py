import sys
import functools

from flask import current_app


def debug_only(f):
    @functools.wraps(f)
    def wrapped_f(*args, **kwargs):
        if current_app.debug:
            return f(*args, **kwargs)
        return None

    return wrapped_f


@debug_only
def startProgress(title):
    global progress_x
    sys.stdout.write(title + ": [" + "-" * 40 + "]" + chr(8) * 41)
    sys.stdout.flush()
    progress_x = 0


@debug_only
def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    sys.stdout.write("#" * (x - progress_x))
    sys.stdout.flush()
    progress_x = x


@debug_only
def endProgress():
    sys.stdout.write("#" * (40 - progress_x) + "]\n")
    sys.stdout.flush()
