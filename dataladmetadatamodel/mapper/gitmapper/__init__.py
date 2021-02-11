import enum

from .datasettreemapper import DatasetTreeGitMapper
from .filetreemapper import FileTreeGitMapper
from .metadatamapper import MetadataGitMapper
from .metadatarootrecordmapper import MetadataRootRecordGitMapper
from .referencemapper import ReferenceGitMapper
from .textmapper import TextGitMapper
from .uuidsetmapper import UUIDSetGitMapper
from .versionlistmapper import TreeVersionListGitMapper
from .versionlistmapper import VersionListGitMapper


class GitReference(enum.Enum):
    TREE_VERSION_LIST = "refs/datalad/dataset-tree"
    UUID_SET = "refs/datalad/dataset-set"
    DATASET_TREE = "refs/datalad/object-references/dataset-tree"
    METADATA = "refs/datalad/object-references/metadata"
    FILE_TREE = "refs/datalad/object-references/file-tree"


GIT_MAPPER_FAMILY_MEMBERS = {
    "DatasetTree": DatasetTreeGitMapper,
    "FileTree": FileTreeGitMapper,
    "Metadata": MetadataGitMapper,
    "MetadataRootRecord": MetadataRootRecordGitMapper,
    "Reference": ReferenceGitMapper,
    "Text": TextGitMapper,
    "TreeVersionList": TreeVersionListGitMapper,
    "UUIDSet": UUIDSetGitMapper,
    "VersionList": VersionListGitMapper
}


TREE_VERSION_LIST_REFERENCE = "refs/datalad/dataset-tree"
UUID_SET_REFERENCE = "refs/datalad/dataset-set"


GIT_MAPPER_LOCATIONS = (TREE_VERSION_LIST_REFERENCE, UUID_SET_REFERENCE)
