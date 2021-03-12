import logging

from typing import Dict, List, Union


JSONObject = Union[int, float, str, List["JSONObject"], Dict[str, "JSONObject"]]


logger = logging.getLogger("datalad.metadata.model")


def join_paths(first: str, second: str) -> str:
    first = first or ""
    second = second or ""

    if first != "" and second != "":
        joined = first.rstrip("/") + "/" + second.lstrip("/")
    else:
        joined = first + second
    return joined.lstrip("/").rstrip("/")


def sanitize_path(path: str) -> str:
    """
    Replace "." with ""
    Remove leading "./", leading and trailing "/",
    and collapse repeated "/"
    """
    if path == ".":
        logger.warning("Converting path '.' to ''")
        return ""

    # Remove leading "./"
    while path.startswith("./"):
        logger.warning(f"Removing leading './' from path {path}")
        path = path[2:]

    # Remove leading and trailing "/"
    path = path.lstrip("/").rstrip("/")

    # Collapse repeated "/"
    while path.find("//") >= 0:
        path = path.replace("//", "/")
    return path
