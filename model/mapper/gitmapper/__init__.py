
from .datasettreemapper import DatasetTreeGitMapper
from .filetreemapper import FileTreeGitMapper
from .metadatamapper import MetadataGitMapper
from .metadatarootrecordmapper import MetadataRootRecordGitMapper
from .referencemapper import ReferenceGitMapper
from .textmapper import TextGitMapper
from .uuidsetmapper import UUIDSetGitMapper
from .versionlistmapper import VersionListGitMapper


GIT_MAPPER_FAMILY = {
    "DatasetTree": DatasetTreeGitMapper,
    "FileTree": FileTreeGitMapper,
    "Metadata": MetadataGitMapper,
    "MetadataRootRecord": MetadataRootRecordGitMapper,
    "Reference": ReferenceGitMapper,
    "Text": TextGitMapper,
    "UUIDSet": UUIDSetGitMapper,
    "VersionList": VersionListGitMapper
}
