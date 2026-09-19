import datetime
import json
import math
import os
import random
import time
import urllib.error
import urllib.request


class StdLibError(Exception):
    pass


def builtin_len(arguments):
    if len(arguments) != 1:
        raise StdLibError("len() expects 1 argument")
    try:
        return len(arguments[0])
    except TypeError:
        raise StdLibError("Object has no length")


def builtin_str(arguments):
    if len(arguments) != 1:
        raise StdLibError("str() expects 1 argument")
    return str(arguments[0])


def builtin_int(arguments):
    if len(arguments) != 1:
        raise StdLibError("int() expects 1 argument")
    try:
        return int(arguments[0])
    except (ValueError, TypeError):
        raise StdLibError("Cannot convert value to int")


def builtin_float(arguments):
    if len(arguments) != 1:
        raise StdLibError("float() expects 1 argument")
    try:
        return float(arguments[0])
    except (ValueError, TypeError):
        raise StdLibError("Cannot convert value to float")


def builtin_abs(arguments):
    if len(arguments) != 1:
        raise StdLibError("abs() expects 1 argument")
    try:
        return abs(arguments[0])
    except TypeError:
        raise StdLibError("Invalid value for abs()")


def builtin_min(arguments):
    if len(arguments) == 0:
        raise StdLibError("min() expects at least 1 argument")
    try:
        return min(arguments)
    except TypeError:
        raise StdLibError("Invalid values for min()")


def builtin_max(arguments):
    if len(arguments) == 0:
        raise StdLibError("max() expects at least 1 argument")
    try:
        return max(arguments)
    except TypeError:
        raise StdLibError("Invalid values for max()")


def builtin_range(arguments):
    if len(arguments) < 1 or len(arguments) > 3:
        raise StdLibError("range() expects 1 to 3 arguments")
    try:
        return list(range(*arguments))
    except (TypeError, ValueError):
        raise StdLibError("Invalid arguments for range()")


def builtin_sqrt(arguments):
    if len(arguments) != 1:
        raise StdLibError("sqrt() expects 1 argument")
    try:
        return math.sqrt(arguments[0])
    except (TypeError, ValueError):
        raise StdLibError("Invalid value for sqrt()")


def builtin_power(arguments):
    if len(arguments) != 2:
        raise StdLibError("power() expects 2 arguments")
    try:
        return arguments[0] ** arguments[1]
    except (TypeError, ValueError):
        raise StdLibError("Invalid values for power()")


def builtin_floor(arguments):
    if len(arguments) != 1:
        raise StdLibError("floor() expects 1 argument")
    try:
        return math.floor(arguments[0])
    except (TypeError, ValueError):
        raise StdLibError("Invalid value for floor()")


def builtin_ceil(arguments):
    if len(arguments) != 1:
        raise StdLibError("ceil() expects 1 argument")
    try:
        return math.ceil(arguments[0])
    except (TypeError, ValueError):
        raise StdLibError("Invalid value for ceil()")


def builtin_sin(arguments):
    if len(arguments) != 1:
        raise StdLibError("sin() expects 1 argument")
    try:
        return math.sin(arguments[0])
    except (TypeError, ValueError):
        raise StdLibError("Invalid value for sin()")


def builtin_cos(arguments):
    if len(arguments) != 1:
        raise StdLibError("cos() expects 1 argument")
    try:
        return math.cos(arguments[0])
    except (TypeError, ValueError):
        raise StdLibError("Invalid value for cos()")


def builtin_tan(arguments):
    if len(arguments) != 1:
        raise StdLibError("tan() expects 1 argument")
    try:
        return math.tan(arguments[0])
    except (TypeError, ValueError):
        raise StdLibError("Invalid value for tan()")


def builtin_round(arguments):
    if len(arguments) not in (1, 2):
        raise StdLibError("round() expects 1 or 2 arguments")
    try:
        return round(*arguments)
    except (TypeError, ValueError):
        raise StdLibError("Invalid arguments for round()")


def builtin_random(arguments):
    if len(arguments) != 0:
        raise StdLibError("random() expects 0 arguments")
    return random.random()


def builtin_randint(arguments):
    if len(arguments) != 2:
        raise StdLibError("randint() expects 2 arguments")
    try:
        return random.randint(arguments[0], arguments[1])
    except (TypeError, ValueError):
        raise StdLibError("Invalid arguments for randint()")


def builtin_choice(arguments):
    if len(arguments) != 1:
        raise StdLibError("choice() expects 1 argument")
    try:
        return random.choice(arguments[0])
    except (IndexError, TypeError):
        raise StdLibError("Cannot choose from this value")


def builtin_shuffle(arguments):
    if len(arguments) != 1:
        raise StdLibError("shuffle() expects 1 argument")

    value = arguments[0]

    if not isinstance(value, list):
        raise StdLibError("shuffle() requires a list")

    random.shuffle(value)

    return value


def builtin_json_parse(arguments):
    if len(arguments) != 1:
        raise StdLibError("json_parse() expects 1 argument")

    if not isinstance(arguments[0], str):
        raise StdLibError("json_parse() requires a string")

    try:
        return json.loads(arguments[0])
    except json.JSONDecodeError:
        raise StdLibError("Invalid JSON")


def builtin_json_stringify(arguments):
    if len(arguments) != 1:
        raise StdLibError("json_stringify() expects 1 argument")

    try:
        return json.dumps(
            arguments[0],
            ensure_ascii=False
        )
    except (TypeError, ValueError):
        raise StdLibError("Cannot convert value to JSON")


def builtin_file_write(arguments):
    if len(arguments) != 2:
        raise StdLibError("file_write() expects 2 arguments")

    path = arguments[0]
    content = arguments[1]

    if not isinstance(path, str):
        raise StdLibError("File path must be a string")

    if not isinstance(content, str):
        content = str(content)

    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
    except OSError:
        raise StdLibError("Unable to write file")

    return True


def builtin_file_read(arguments):
    if len(arguments) != 1:
        raise StdLibError("file_read() expects 1 argument")

    path = arguments[0]

    if not isinstance(path, str):
        raise StdLibError("File path must be a string")

    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except OSError:
        raise StdLibError("Unable to read file")


def builtin_file_append(arguments):
    if len(arguments) != 2:
        raise StdLibError("file_append() expects 2 arguments")

    path = arguments[0]
    content = arguments[1]

    if not isinstance(path, str):
        raise StdLibError("File path must be a string")

    if not isinstance(content, str):
        content = str(content)

    try:
        with open(path, "a", encoding="utf-8") as file:
            file.write(content)
    except OSError:
        raise StdLibError("Unable to append to file")

    return True


def builtin_file_exists(arguments):
    if len(arguments) != 1:
        raise StdLibError("file_exists() expects 1 argument")

    path = arguments[0]

    if not isinstance(path, str):
        raise StdLibError("File path must be a string")

    return os.path.isfile(path)


def builtin_file_delete(arguments):
    if len(arguments) != 1:
        raise StdLibError("file_delete() expects 1 argument")

    path = arguments[0]

    if not isinstance(path, str):
        raise StdLibError("File path must be a string")

    try:
        if os.path.isfile(path):
            os.remove(path)
            return True

        return False
    except OSError:
        raise StdLibError("Unable to delete file")


def builtin_now(arguments):
    if len(arguments) != 0:
        raise StdLibError("now() expects 0 arguments")

    return datetime.datetime.now().isoformat(
        timespec="seconds"
    )


def builtin_today(arguments):
    if len(arguments) != 0:
        raise StdLibError("today() expects 0 arguments")

    return datetime.date.today().isoformat()


def builtin_timestamp(arguments):
    if len(arguments) != 0:
        raise StdLibError("timestamp() expects 0 arguments")

    return int(time.time())


def builtin_time_format(arguments):
    if len(arguments) != 1:
        raise StdLibError("time_format() expects 1 argument")

    if not isinstance(arguments[0], str):
        raise StdLibError("time_format() requires a string")

    return datetime.datetime.now().strftime(arguments[0])


def builtin_sleep(arguments):
    if len(arguments) != 1:
        raise StdLibError("sleep() expects 1 argument")

    try:
        seconds = float(arguments[0])
    except (TypeError, ValueError):
        raise StdLibError("sleep() requires a number")

    if seconds < 0:
        raise StdLibError(
            "sleep() requires a non-negative value"
        )

    time.sleep(seconds)

    return True


def builtin_http_get(arguments):
    if len(arguments) != 1:
        raise StdLibError("http_get() expects 1 argument")

    url = arguments[0]

    if not isinstance(url, str):
        raise StdLibError("URL must be a string")

    try:
        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "User-Agent": "Velto/0.47"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:
            return response.read().decode(
                "utf-8",
                errors="replace"
            )

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError
    ):
        raise StdLibError(
            "HTTP GET request failed"
        )


def builtin_http_post(arguments):
    if len(arguments) != 2:
        raise StdLibError("http_post() expects 2 arguments")

    url = arguments[0]
    data = arguments[1]

    if not isinstance(url, str):
        raise StdLibError("URL must be a string")

    if not isinstance(data, str):
        data = str(data)

    try:
        request = urllib.request.Request(
            url,
            data=data.encode("utf-8"),
            method="POST",
            headers={
                "User-Agent": "Velto/0.47",
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:
            return response.read().decode(
                "utf-8",
                errors="replace"
            )

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError
    ):
        raise StdLibError(
            "HTTP POST request failed"
        )


def builtin_set(arguments):
    if len(arguments) != 1:
        raise StdLibError("set() expects 1 argument")

    try:
        return list(dict.fromkeys(arguments[0]))
    except TypeError:
        raise StdLibError("set() requires an iterable")


def builtin_unique(arguments):
    if len(arguments) != 1:
        raise StdLibError("unique() expects 1 argument")

    try:
        return list(dict.fromkeys(arguments[0]))
    except TypeError:
        raise StdLibError("unique() requires an iterable")


def builtin_contains(arguments):
    if len(arguments) != 2:
        raise StdLibError("contains() expects 2 arguments")

    try:
        return arguments[1] in arguments[0]
    except TypeError:
        raise StdLibError("Invalid value for contains()")


def builtin_keys(arguments):
    if len(arguments) != 1:
        raise StdLibError("keys() expects 1 argument")

    if not isinstance(arguments[0], dict):
        raise StdLibError("keys() requires a dictionary")

    return list(arguments[0].keys())


def builtin_values(arguments):
    if len(arguments) != 1:
        raise StdLibError("values() expects 1 argument")

    if not isinstance(arguments[0], dict):
        raise StdLibError("values() requires a dictionary")

    return list(arguments[0].values())


def builtin_items(arguments):
    if len(arguments) != 1:
        raise StdLibError("items() expects 1 argument")

    if not isinstance(arguments[0], dict):
        raise StdLibError("items() requires a dictionary")

    return [
        [key, value]
        for key, value in arguments[0].items()
    ]


def builtin_sort(arguments):
    if len(arguments) != 1:
        raise StdLibError("sort() expects 1 argument")

    if not isinstance(arguments[0], list):
        raise StdLibError("sort() requires a list")

    result = list(arguments[0])

    try:
        result.sort()
    except TypeError:
        raise StdLibError("List values cannot be sorted")

    return result


def builtin_reverse(arguments):
    if len(arguments) != 1:
        raise StdLibError("reverse() expects 1 argument")

    if not isinstance(arguments[0], list):
        raise StdLibError("reverse() requires a list")

    result = list(arguments[0])
    result.reverse()

    return result


def builtin_join(arguments):
    if len(arguments) != 2:
        raise StdLibError("join() expects 2 arguments")

    separator = arguments[0]
    values = arguments[1]

    if not isinstance(separator, str):
        raise StdLibError("join() separator must be a string")

    if not isinstance(values, list):
        raise StdLibError("join() requires a list")

    try:
        return separator.join(str(value) for value in values)
    except TypeError:
        raise StdLibError("Invalid values for join()")


def builtin_split(arguments):
    if len(arguments) not in (1, 2):
        raise StdLibError("split() expects 1 or 2 arguments")

    text = arguments[0]

    if not isinstance(text, str):
        raise StdLibError("split() requires a string")

    if len(arguments) == 1:
        return text.split()

    separator = arguments[1]

    if not isinstance(separator, str):
        raise StdLibError("split() separator must be a string")

    return text.split(separator)


BUILTINS = {
    "len": builtin_len,
    "str": builtin_str,
    "int": builtin_int,
    "float": builtin_float,
    "abs": builtin_abs,
    "min": builtin_min,
    "max": builtin_max,
    "range": builtin_range,
    "sqrt": builtin_sqrt,
    "power": builtin_power,
    "floor": builtin_floor,
    "ceil": builtin_ceil,
    "sin": builtin_sin,
    "cos": builtin_cos,
    "tan": builtin_tan,
    "round": builtin_round,
    "random": builtin_random,
    "randint": builtin_randint,
    "choice": builtin_choice,
    "shuffle": builtin_shuffle,
    "json_parse": builtin_json_parse,
    "json_stringify": builtin_json_stringify,
    "file_write": builtin_file_write,
    "file_read": builtin_file_read,
    "file_append": builtin_file_append,
    "file_exists": builtin_file_exists,
    "file_delete": builtin_file_delete,
    "now": builtin_now,
    "today": builtin_today,
    "timestamp": builtin_timestamp,
    "time_format": builtin_time_format,
    "sleep": builtin_sleep,
    "http_get": builtin_http_get,
    "http_post": builtin_http_post,
    "set": builtin_set,
    "unique": builtin_unique,
    "contains": builtin_contains,
    "keys": builtin_keys,
    "values": builtin_values,
    "items": builtin_items,
    "sort": builtin_sort,
    "reverse": builtin_reverse,
    "join": builtin_join,
    "split": builtin_split
}
