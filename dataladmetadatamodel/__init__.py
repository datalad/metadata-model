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
    """
    Remove leading "./", leading and trailing "/",
    and collapse repeated "/"
    """

    # Remove leading "./"
    while path.startswith("./"):
        path = path[2:]

    # Remove leading and trailing "/"
    path = path.lstrip("/").rstrip("/")

    # Collapse repeated "/"
    while path.find("//") >= 0:
        path = path.replace("//", "/")
    return path
