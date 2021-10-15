from collections import defaultdict
from typing import (
    DefaultDict,
    Dict
)

from .gitmapper import GIT_MAPPER_LOCATIONS


git_mapper_family_name = "git"

locations = {
    git_mapper_family_name: GIT_MAPPER_LOCATIONS
}

registered_mapper: DefaultDict[str, Dict[str, "Mapper"]] = defaultdict(dict)


def _get_locations(mapper_family: str):
    return locations.get(mapper_family, (None, None))


def get_uuid_set_location(mapper_family: str):
    return _get_locations(mapper_family)[1]


def get_tree_version_list_location(mapper_family: str):
    return _get_locations(mapper_family)[0]


def get_mapper(class_name: str, backend_type: str) -> "Mapper":
    return registered_mapper[backend_type][class_name]


def set_mapper(class_name: str, backend_type: str, mapper: "Mapper"):
    registered_mapper[backend_type][class_name] = mapper


def initialize_object_store():
    from .gitmapper.metadatamapper import MetadataGitMapper
    from .gitmapper.metadatarootrecordmapper import MetadataRootRecordGitMapper
    from .gitmapper.mtreenodemapper import MTreeNodeGitMapper
    from .gitmapper.textmapper import TextGitMapper
    from .gitmapper.uuidsetmapper import UUIDSetGitMapper
    from .gitmapper.versionlistmapper import (
        TreeVersionListGitMapper,
        VersionListGitMapper
    )

    set_mapper("DatasetTree", "git", MTreeNodeGitMapper("MTreeNode"))
    set_mapper("FileTree", "git", MTreeNodeGitMapper("MTreeNode"))
    set_mapper("Metadata", "git", MetadataGitMapper("Metadata"))
    set_mapper("MetadataRootRecord", "git", MetadataRootRecordGitMapper("MetadataRootRecord"))
    set_mapper("MTreeNode", "git", MTreeNodeGitMapper("MTreeNode"))
    set_mapper("Text", "git", TextGitMapper("Text"))
    set_mapper("TreeVersionList", "git", TreeVersionListGitMapper("TreeVersionList"))
    set_mapper("UUIDSet", "git", UUIDSetGitMapper("UUIDSet"))
    set_mapper("VersionList", "git", VersionListGitMapper("VersionList"))


initialize_object_store()
