from typing import Any

from dataladmetadatamodel.mapper.gitmapper.objectreference import GitReference
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_save_json,
    git_update_ref
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference
from dataladmetadatamodel.mappableobject import MappableObject


class VersionListGitMapper(Mapper):
    """
    Map version lists to git objects.
    The objects are blobs containing json strings that
    define a list of primary data-metadata associations.
    """

    def _get_version_records(self, ref: Reference) -> dict:
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

    def map_out_impl(self,
                     version_list: "VersionList",
                     destination: str,
                     force_write: bool
                     ) -> Reference:

        from dataladmetadatamodel.versionlist import VersionList

        assert isinstance(version_list, VersionList)

        for primary_data_version, version_record in version_list.version_set.items():
            version_record.write_out()

        json_object = [
            {
                "primary_data_version": primary_data_version,
                "time_stamp": version_record.time_stamp,
                "path": version_record.path.as_posix(),
                "dataset_tree": version_record.reference.to_json_obj()
            }
            for primary_data_version, version_record in version_list.version_set.items()]

        location = git_save_json(destination, json_object)
        return Reference("git", destination, "VersionList", location)


class TreeVersionListGitMapper(VersionListGitMapper):
    def map_in_impl(self,
                    tree_version_list: "TreeVersionList",
                    reference: Reference) -> None:

        from dataladmetadatamodel.versionlist import TreeVersionList

        for version, version_record in self._get_version_records(reference):
            self.set_dataset_tree("000", "1.2", None)

    def map_out_impl(self,
                     tree_version_list: "TreeVersionList",
                     destination: str,
                     force_write: bool
                     ) -> Reference:

        from dataladmetadatamodel.versionlist import TreeVersionList

        assert isinstance(tree_version_list, TreeVersionList)
        reference = super().unmap_impl(obj)
        git_update_ref(
            self.realm,
            GitReference.TREE_VERSION_LIST.value,
            reference.location)
        return reference
