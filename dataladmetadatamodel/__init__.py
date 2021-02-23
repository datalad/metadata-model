from typing import Dict, List, Union


JSONObject = Union[int, float, str, List["JSONObject"], Dict[str, "JSONObject"]]


def join_paths(first: str, second: str) -> str:
    first = first or ""
    second = second or ""

    if first != "" and second != "":
        joined = first.rstrip("/") + "/" + second.lstrip("/")
    else:
        joined = first + second
    return joined.lstrip("/").rstrip("/")


def sanitize_path(path: str) -> str:
    """ remove leading and trailing "/", and collapse repeated "/" """
    path = path.lstrip("/").rstrip("/")
    while path.find("//") >= 0:
        path = path.replace("//", "/")
    return path
