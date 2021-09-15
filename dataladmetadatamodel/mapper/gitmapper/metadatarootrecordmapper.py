from uuid import UUID

from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_save_json
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class Strings:
    GIT = "git"
    DATASET_IDENTIFIER = "dataset_identifier"
    DATASET_VERSION = "dataset_version"
    DATASET_LEVEL_METADATA = "dataset_level_metadata"
    FILE_TREE = "file_tree"


class MetadataRootRecordGitMapper(Mapper):
    def map_in_impl(self,
                    metadata_root_record: "MetadataRootRecord",
                    reference: Reference) -> None:

        from dataladmetadatamodel.filetree import FileTree
        from dataladmetadatamodel.metadata import Metadata
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

        assert isinstance(metadata_root_record, MetadataRootRecord)
        assert isinstance(reference, Reference)
        assert reference.mapper_family == Strings.GIT

        json_object = git_load_json(reference.realm, reference.location)

        metadata_reference = Reference.from_json_obj(
            json_object[Strings.DATASET_LEVEL_METADATA])
        file_tree_reference = Reference.from_json_obj(
            json_object[Strings.FILE_TREE])

        MetadataRootRecord.__init__(
            metadata_root_record,
            UUID(json_object[Strings.DATASET_IDENTIFIER]),
            json_object[Strings.DATASET_VERSION],
            Metadata(metadata_reference),
            FileTree(file_tree_reference))

    def map_out_impl(self,
                     mrr: "MetadataRootRecord",
                     destination: str,
                     force_write: bool) -> Reference:

        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

        assert isinstance(mrr, MetadataRootRecord)

        json_object = {
            Strings.DATASET_IDENTIFIER: str(mrr.dataset_identifier),
            Strings.DATASET_VERSION: str(mrr.dataset_version),
            Strings.DATASET_LEVEL_METADATA: mrr.dataset_level_metadata.write_out(
                destination,
                "git",
                force_write).to_json_obj(),
            Strings.FILE_TREE: mrr.file_tree.write_out(
                destination,
                "git",
                force_write).to_json_obj()}

        return Reference(
            "git",
            destination,
            "MetadataRootRecord",
            git_save_json(destination, json_object))
