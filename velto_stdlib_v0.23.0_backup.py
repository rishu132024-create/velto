class StdLibError(Exception):
    pass


def builtin_len(args):
    if len(args) != 1:
        raise StdLibError("len() expects 1 argument")

    value = args[0]

    if isinstance(value, (str, list)):
        return len(value)

    raise StdLibError("len() supports strings and lists")


def builtin_str(args):
    if len(args) != 1:
        raise StdLibError("str() expects 1 argument")

    return str(args[0])


def builtin_int(args):
    if len(args) != 1:
        raise StdLibError("int() expects 1 argument")

    try:
        return int(args[0])
    except (ValueError, TypeError):
        raise StdLibError("int() received an invalid value")


def builtin_float(args):
    if len(args) != 1:
        raise StdLibError("float() expects 1 argument")

    try:
        return float(args[0])
    except (ValueError, TypeError):
        raise StdLibError("float() received an invalid value")


def builtin_abs(args):
    if len(args) != 1:
        raise StdLibError("abs() expects 1 argument")

    try:
        return abs(args[0])
    except TypeError:
        raise StdLibError("abs() received an invalid value")


def builtin_min(args):
    if len(args) < 1:
        raise StdLibError("min() expects at least 1 argument")

    try:
        return min(args)
    except TypeError:
        raise StdLibError("min() received invalid values")


def builtin_max(args):
    if len(args) < 1:
        raise StdLibError("max() expects at least 1 argument")

    try:
        return max(args)
    except TypeError:
        raise StdLibError("max() received invalid values")


def builtin_range(args):
    if len(args) not in (1, 2, 3):
        raise StdLibError(
            "range() expects 1, 2, or 3 arguments"
        )

    try:
        return list(range(*args))
    except (TypeError, ValueError):
        raise StdLibError("range() received invalid values")


BUILTINS = {
    "len": builtin_len,
    "str": builtin_str,
    "int": builtin_int,
    "float": builtin_float,
    "abs": builtin_abs,
    "min": builtin_min,
    "max": builtin_max,
    "range": builtin_range
}
