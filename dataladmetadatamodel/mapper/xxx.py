from _collections import defaultdict
from typing import (
    Any,
    Dict
)


registered_mapper: defaultdict[str, Dict[str, Any]] = defaultdict(dict)


def get_mapper(class_name: str, backend_type: str):
    return registered_mapper[backend_type][class_name]


def set_mapper(class_name: str, backend_type: str, mapper: Any):
    registered_mapper[backend_type][class_name] = mapper
