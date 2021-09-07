from typing import Any
from uuid import UUID

from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_save_json
)
from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.reference import Reference


class Strings:
    GIT = "git"
    DATASET_IDENTIFIER = "dataset_identifier"
    DATASET_VERSION = "dataset_version"
    DATASET_LEVEL_METADATA = "dataset_level_metadata"
    FILE_TREE = "file_tree"


class MetadataRootRecordGitMapper(BaseMapper):
    def map(self, ref: Reference) -> Any:
        from dataladmetadatamodel.connector import Connector
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

        assert isinstance(ref, Reference)
        assert ref.mapper_family == Strings.GIT

        json_object = git_load_json(self.realm, ref.location)
        return MetadataRootRecord(
            Strings.GIT,
            self.realm,
            UUID(json_object[Strings.DATASET_IDENTIFIER]),
            json_object[Strings.DATASET_VERSION],
            Connector.from_reference(
                Reference.from_json_obj(
                    json_object[Strings.DATASET_LEVEL_METADATA])),
            Connector.from_reference(
                Reference.from_json_obj(json_object[Strings.FILE_TREE])))

    def unmap(self, obj) -> str:
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
        assert isinstance(obj, MetadataRootRecord)
        json_object = {
            Strings.DATASET_IDENTIFIER: str(obj.dataset_identifier),
            Strings.DATASET_VERSION: str(obj.dataset_version),
            Strings.DATASET_LEVEL_METADATA:
                obj.dataset_level_metadata.save_object().to_json_obj(),
            Strings.FILE_TREE:
                obj.file_tree.save_object().to_json_obj()
        }
        return git_save_json(self.realm, json_object)
