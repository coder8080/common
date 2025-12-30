import logging
from os import getenv


def get_str_env(key: str, default: str | None = None) -> str:
    res = getenv(key)
    if res is None and default is not None:
        return default
    assert res, f"{key} env var is required"
    return res


def get_int_env(key: str, default: int | None = None) -> int:
    str_val = getenv(key)
    if str_val is None and default is not None:
        return default
    assert str_val, f"{key} env var is required"
    return int(str_val)


def get_bool_env(key: str, default: bool | None = None) -> bool:
    raw_val = getenv(key)
    if raw_val is None and default is not None:
        return default
    assert raw_val is not None and raw_val.lower() in ("true", "false"), (
        f"{key} env should be true of false"
    )
    return raw_val.lower() == "true"


def str_to_loglevel(val: str) -> int:
    match val:
        case "NOTSET":
            return logging.NOTSET
        case "DEBUG":
            return logging.DEBUG
        case "INFO":
            return logging.INFO
        case "WARN":
            return logging.WARN
        case "WARNING":
            return logging.WARNING
        case "ERROR":
            return logging.ERROR
        case "FATAL":
            return logging.FATAL
        case "CRITICAL":
            return logging.CRITICAL
        case _:
            raise RuntimeError(f"Unknown logging level: {val}")
