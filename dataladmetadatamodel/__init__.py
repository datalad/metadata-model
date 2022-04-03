from typing import (
    Dict,
    List,
    Union
)


JSONObject = Union[
    None, bool, int, float, str,
    List["JSONObject"],
    Dict[str, "JSONObject"]
]


version = 2
version_minor = 0
version_string = f"{version}.{version_minor}"


def check_serialized_version(json_object: JSONObject):
    stored_class = json_object["@"]["type"]
    stored_version = json_object["@"]["version"]
    if stored_version != version_string:
        raise ValueError(
            f"Unsupported metadata version ({stored_version}) in "
            f"stored {stored_class} object, expected version: "
            f"{version_string}")


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
