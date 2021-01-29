from typing import Any

from .gittools import git_load_json, git_save_json
from ..basemapper import BaseMapper
from ..reference import Reference


class MetadataRootRecordGitMapper(BaseMapper):

    def map(self, ref: Reference) -> Any:
        from model.connector import Connector
        from model.metadatarootrecord import MetadataRootRecord

        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"

        json_object = git_load_json(self.realm, ref.location)
        return MetadataRootRecord(
            "git",
            self.realm,
            json_object["dataset_identifier"],
            Connector.from_reference(
                Reference.from_json(json_object["dataset_level_metadata"])
            ),
            Connector.from_reference(
                Reference.from_json(json_object["file_level_metadata"])
            )
        )

    def unmap(self, obj) -> str:
        from model.metadatarootrecord import MetadataRootRecord
        assert isinstance(obj, MetadataRootRecord)
        json_object = {
            "dataset_identifier": obj.dataset_identifier,
            "dataset_level_metadata": obj.dataset_level_metadata.save(
                "git",
                self.realm
            ).to_json(),
            "file_level_metadata": obj.file_tree.save(
                "git",
                self.realm
            ).to_json()
        }
        return git_save_json(self.realm, json_object)

