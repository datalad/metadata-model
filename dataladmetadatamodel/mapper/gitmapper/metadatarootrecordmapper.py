from typing import Any
from uuid import UUID

from .gittools import git_load_json, git_save_json
from ..basemapper import BaseMapper
from ..reference import Reference


class MetadataRootRecordGitMapper(BaseMapper):

    def map(self, ref: Reference) -> Any:
        from dataladmetadatamodel.connector import Connector
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"

        json_object = git_load_json(self.realm, ref.location)
        return MetadataRootRecord(
            "git",
            self.realm,
            UUID(json_object["dataset_identifier"]),
            json_object["dataset_version"],
            Connector.from_reference(
                Reference.from_json_obj(json_object["dataset_level_metadata"])
            ),
            Connector.from_reference(
                Reference.from_json_obj(json_object["file_level_metadata"])
            )
        )

    def unmap(self, obj) -> str:
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
        assert isinstance(obj, MetadataRootRecord)
        json_object = {
            "dataset_identifier": str(obj.dataset_identifier),
            "dataset_version": str(obj.dataset_version),
            "dataset_level_metadata": obj.dataset_level_metadata.save_object(
                "git",
                self.realm
            ).to_json_obj(),
            "file_level_metadata": obj.file_tree.save_object(
                "git",
                self.realm
            ).to_json_obj()
        }
        return git_save_json(self.realm, json_object)
