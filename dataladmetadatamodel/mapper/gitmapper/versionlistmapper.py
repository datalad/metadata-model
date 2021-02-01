from typing import Any

from .execute import checked_execute
from .gittools import git_command_line, git_load_json, git_save_json
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
    def unmap(self, obj: Any) -> str:
        location = super().unmap(obj)
        cmd_line = git_command_line(
            self.realm,
            "update-ref",
            ["refs/develop/dataset-tree", location])
        checked_execute(cmd_line)
        return "refs/develop/dataset-tree"
