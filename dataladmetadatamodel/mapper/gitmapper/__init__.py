from dataladmetadatamodel.mapper.gitmapper.datasettreemapper import DatasetTreeGitMapper
from dataladmetadatamodel.mapper.gitmapper.filetreemapper import FileTreeGitMapper
from dataladmetadatamodel.mapper.gitmapper.metadatamapper import MetadataGitMapper
from dataladmetadatamodel.mapper.gitmapper.metadatarootrecordmapper import MetadataRootRecordGitMapper
from dataladmetadatamodel.mapper.gitmapper.filetreemapper import GitReference
from dataladmetadatamodel.mapper.gitmapper.referencemapper import ReferenceGitMapper
from dataladmetadatamodel.mapper.gitmapper.textmapper import TextGitMapper
from dataladmetadatamodel.mapper.gitmapper.uuidsetmapper import UUIDSetGitMapper
from dataladmetadatamodel.mapper.gitmapper.versionlistmapper import TreeVersionListGitMapper
from dataladmetadatamodel.mapper.gitmapper.versionlistmapper import VersionListGitMapper


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
