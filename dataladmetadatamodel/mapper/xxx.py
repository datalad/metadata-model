from _collections import defaultdict
from typing import (
    DefaultDict,
    Dict
)

registered_mapper: DefaultDict[str, Dict[str, "Mapper"]] = defaultdict(dict)


def get_mapper(class_name: str, backend_type: str) -> "Mapper":
    return registered_mapper[backend_type][class_name]


def set_mapper(class_name: str, backend_type: str, mapper: "Mapper"):
    registered_mapper[backend_type][class_name] = mapper


def initialize_object_store():
    from .gitmapper.datasettreemapper import DatasetTreeGitMapper
    from .gitmapper.filetreemapper import FileTreeGitMapper
    from .gitmapper.metadatamapper import MetadataGitMapper
    from .gitmapper.metadatarootrecordmapper import MetadataRootRecordGitMapper
    from .gitmapper.uuidsetmapper import UUIDSetGitMapper
    from .gitmapper.versionlistmapper import (
        TreeVersionListGitMapper,
        VersionListGitMapper
    )

    set_mapper("DatasetTree", "git", DatasetTreeGitMapper("DatasetTree"))
    set_mapper("FileTree", "git", FileTreeGitMapper("FileTree"))
    set_mapper("Metadata", "git", MetadataGitMapper("Metadata"))
    set_mapper("MetadataRootRecord", "git", MetadataRootRecordGitMapper("MetadataRootRecord"))
    set_mapper("TreeVersionList", "git", TreeVersionListGitMapper("TreeVersionList"))
    set_mapper("UUIDSet", "git", UUIDSetGitMapper("UUIDSet"))
    set_mapper("VersionList", "git", VersionListGitMapper("VersionList"))


initialize_object_store()
