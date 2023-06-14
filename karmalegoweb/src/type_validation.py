def check_non_negative_int(s):
    """
    Validates that the input string represents an integer larger than or equal to 0.
    :param s: the string we want to check
    :return: True if it is represents an integer larger than or equal to 0, False otherwise
    """
    try:
        return int(s) >= 0
    except ValueError:
        return False


def check_int(s):
    """
    Validates that the input string represents an integer.
    :param s: the string we want to check
    :return: True if it is represents an integer, False otherwise
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def check_float(s):
    """
    Validates that the input string represents an floating point number.
    :param s: the string we want to check
    :return: True if it is represents an floating point number, False otherwise
    """
    try:
        float(s)
        return True
    except ValueError:
        return False
