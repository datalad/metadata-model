from uuid import UUID

from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_save_json,
)
from dataladmetadatamodel.mapper.gitmapper.objectreference import (
    add_blob_reference,
    add_tree_reference,
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
                    realm: str,
                    reference: Reference) -> None:

        from dataladmetadatamodel.filetree import FileTree
        from dataladmetadatamodel.metadata import Metadata
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

        assert isinstance(metadata_root_record, MetadataRootRecord)
        assert isinstance(realm, str)
        assert isinstance(reference, Reference)

        json_object = git_load_json(realm, reference.location)

        metadata_reference = Reference.from_json_obj(
            json_object[Strings.DATASET_LEVEL_METADATA])
        if metadata_reference.is_none_reference():
            metadata = None
        else:
            metadata = Metadata(realm=realm, reference=metadata_reference)

        file_tree_reference = Reference.from_json_obj(
            json_object[Strings.FILE_TREE])
        if file_tree_reference.is_none_reference():
            file_tree = None
        else:
            file_tree = FileTree(realm=realm, reference=file_tree_reference)

        MetadataRootRecord.__init__(
            metadata_root_record,
            UUID(json_object[Strings.DATASET_IDENTIFIER]),
            json_object[Strings.DATASET_VERSION],
            metadata,
            file_tree,
            realm=realm,
            reference=reference)

    def map_out_impl(self,
                     mrr: "MetadataRootRecord",
                     realm: str,
                     force_write: bool) -> Reference:

        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

        assert isinstance(mrr, MetadataRootRecord)

        if mrr._file_tree is None:
            file_tree_reference = Reference.get_none_reference("FileTree")
        else:
            file_tree_reference = mrr._file_tree.write_out(
                realm,
                "git",
                force_write)
            if not file_tree_reference.is_none_reference():
                add_tree_reference(file_tree_reference.location)

        if mrr.dataset_level_metadata is None:
            dataset_level_metadata_reference = Reference.get_none_reference("Metadata")
        else:
            dataset_level_metadata_reference = mrr.dataset_level_metadata.write_out(
                realm,
                "git",
                force_write)
            add_blob_reference(dataset_level_metadata_reference.location)

        json_object = {
            Strings.DATASET_IDENTIFIER: str(mrr.dataset_identifier),
            Strings.DATASET_VERSION: str(mrr.dataset_version),
            Strings.DATASET_LEVEL_METADATA: dataset_level_metadata_reference.to_json_obj(),
            Strings.FILE_TREE: file_tree_reference.to_json_obj()}

        return Reference(
            "MetadataRootRecord",
            git_save_json(realm, json_object))
