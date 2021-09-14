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
    from .gitmapper.filetreemapper import FileTreeGitMapper
    from .gitmapper.metadatamapper import MetadataGitMapper

    set_mapper("Metadata", "git", MetadataGitMapper("Metadata"))
    set_mapper("FileTree", "git", FileTreeGitMapper("FileTree"))


initialize_object_store()
