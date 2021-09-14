from _collections import defaultdict
from typing import (
    Any,
    DefaultDict,
    Dict
)


registered_mapper: DefaultDict[str, Dict[str, Any]] = defaultdict(dict)


def get_mapper(class_name: str, backend_type: str):
    return registered_mapper[backend_type][class_name]


def set_mapper(class_name: str, backend_type: str, mapper: Any):
    registered_mapper[backend_type][class_name] = mapper


def initialize_object_store():
    pass


initialize_object_store()