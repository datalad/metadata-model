from typing import Any

from .gitbackend.subprocess import git_load_json, git_save_json, git_update_ref
from ..basemapper import BaseMapper
from ..reference import Reference


class VersionListGitMapper(BaseMapper):
    """
    Map version lists to git objects.
    The objects are blobs containing json strings that
    define a list of primary data-metadata associations.
    """

    def map(self, ref: Reference) -> Any:
        from dataladmetadatamodel.connector import Connector
        from dataladmetadatamodel.versionlist import VersionRecord, VersionList
        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"

        json_object = git_load_json(self.realm, ref.location)
        version_records = {
            pdm_assoc["primary_data_version"]: VersionRecord(
                pdm_assoc["time_stamp"],
                pdm_assoc["path"],
                Connector.from_reference(
                    Reference.from_json_obj(pdm_assoc["metadata_root"])
                )
            )
            for pdm_assoc in json_object
        }
        return VersionList("git", self.realm, version_records)

    def unmap(self, obj: Any) -> str:
        from dataladmetadatamodel.versionlist import VersionList
        assert isinstance(obj, VersionList)
        json_object = [
            {
                "primary_data_version": primary_data_version,
                "time_stamp": version_record.time_stamp,
                "path": version_record.path,
                "metadata_root": version_record.mrr_connector.save_object(
                    "git",
                    self.realm
                ).to_json_obj()
            }
            for primary_data_version, version_record in obj.version_set.items()
        ]
        return git_save_json(self.realm, json_object)


class TreeVersionListGitMapper(VersionListGitMapper):
    def map(self, ref: Reference) -> Any:
        from dataladmetadatamodel.connector import Connector
        from dataladmetadatamodel.versionlist import VersionRecord, TreeVersionList
        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"

        json_object = git_load_json(self.realm, ref.location)
        version_records = {
            pdm_assoc["primary_data_version"]: VersionRecord(
                pdm_assoc["time_stamp"],
                pdm_assoc["path"],
                Connector.from_reference(
                    Reference.from_json_obj(pdm_assoc["metadata_root"])
                )
            )
            for pdm_assoc in json_object
        }
        return TreeVersionList("git", self.realm, version_records)

    def unmap(self, obj: Any) -> str:
        location = super().unmap(obj)
        git_update_ref(self.realm, "refs/develop/dataset-tree", location)
        return "refs/develop/dataset-tree"
