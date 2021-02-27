from .datasettreemapper import DatasetTreeGitMapper
from .filetreemapper import FileTreeGitMapper
from .metadatamapper import MetadataGitMapper
from .metadatarootrecordmapper import MetadataRootRecordGitMapper
from .filetreemapper import GitReference
from .referencemapper import ReferenceGitMapper
from .textmapper import TextGitMapper
from .uuidsetmapper import UUIDSetGitMapper
from .versionlistmapper import TreeVersionListGitMapper
from .versionlistmapper import VersionListGitMapper


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


GIT_MAPPER_LOCATIONS = (
    GitReference.TREE_VERSION_LIST.value,
    GitReference.UUID_SET.value
)
