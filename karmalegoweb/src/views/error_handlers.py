import functools

from flask import request


def validate_args(args_to_validate, inForm=True):
    def validate(view):
        """
        this function checks if the user is connected by checking the token
        :param f: the token
        :return:
        """

        @functools.wraps(view)
        def wrapped_view(*args, **kwargs):
            for arg in args_to_validate:
                args_object = request.form if inForm else request.args
                if arg not in args_object:
                    return f"Missing {arg} in request's body", 400

            return view(*args, **kwargs)

        return wrapped_view

    return validate
