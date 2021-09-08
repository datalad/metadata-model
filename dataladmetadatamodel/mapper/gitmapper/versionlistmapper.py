from typing import Any

from dataladmetadatamodel.mapper.gitmapper.objectreference import GitReference
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_save_json,
    git_update_ref
)
from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.reference import Reference


class VersionListGitMapper(BaseMapper):
    """
    Map version lists to git objects.
    The objects are blobs containing json strings that
    define a list of primary data-metadata associations.
    """

    def _get_version_records(self, ref: Reference) -> dict:
        from dataladmetadatamodel.connector import Connector
        from dataladmetadatamodel.metadatapath import MetadataPath
        from dataladmetadatamodel.versionlist import VersionRecord

        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"

        json_object = git_load_json(self.realm, ref.location)
        version_records = {
            pdm_assoc["primary_data_version"]: VersionRecord(
                pdm_assoc["time_stamp"],
                MetadataPath(pdm_assoc["path"]),
                Connector.from_reference(
                    Reference.from_json_obj(pdm_assoc["dataset_tree"])
                )
            )
            for pdm_assoc in json_object
        }
        return version_records

    def map_impl(self, ref: Reference) -> Any:
        from dataladmetadatamodel.versionlist import VersionList

        version_records = self._get_version_records(ref)
        return VersionList("git", self.realm, version_records)

    def unmap_impl(self, obj: Any) -> str:
        from dataladmetadatamodel.versionlist import VersionList

        assert isinstance(obj, VersionList)
        json_object = [
            {
                "primary_data_version": primary_data_version,
                "time_stamp": version_record.time_stamp,
                "path": version_record.path.as_posix(),
                "dataset_tree": version_record.element_connector.reference.to_json_obj()
            }
            for primary_data_version, version_record in obj.version_set.items()
        ]
        return git_save_json(self.realm, json_object)


class TreeVersionListGitMapper(VersionListGitMapper):
    def map_impl(self, ref: Reference) -> Any:
        from dataladmetadatamodel.versionlist import TreeVersionList

        version_records = self._get_version_records(ref)
        return TreeVersionList("git", self.realm, version_records)

    def unmap_impl(self, obj: Any) -> str:
        location = super().unmap_impl(obj)
        git_update_ref(
            self.realm, GitReference.TREE_VERSION_LIST.value, location)
        return GitReference.TREE_VERSION_LIST.value
