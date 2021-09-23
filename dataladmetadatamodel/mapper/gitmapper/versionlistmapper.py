from dataladmetadatamodel.mapper.gitmapper.objectreference import GitReference
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_save_json,
    git_update_ref
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class VersionListGitMapper(Mapper):
    """
    Map version lists to git objects.
    The objects are blobs containing json strings that
    define a list of primary data-metadata associations.
    """

    def _get_version_records(self, reference: Reference) -> dict:
        from dataladmetadatamodel.datasettree import DatasetTree
        from dataladmetadatamodel.metadatapath import MetadataPath
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
        from dataladmetadatamodel.versionlist import VersionRecord

        assert isinstance(reference, Reference)
        assert reference.mapper_family == "git"

        json_object = git_load_json(reference.realm, reference.location)

        version_records = {}
        for pdm_assoc in json_object:

            reference = Reference.from_json_obj(pdm_assoc["dataset_tree"])
            if reference.class_name in ("DatasetTree", "MTreeNode"):
                mrr_or_tree = DatasetTree(reference=reference)
            elif reference.class_name == "MetadataRootRecord":
                mrr_or_tree = MetadataRootRecord(None, None, None, None, reference)
            else:
                raise ValueError(
                    f"unexpected tree class in primary data-metadata "
                    f"assoc: ({reference.class_name})")

            version_records[pdm_assoc["primary_data_version"]] = VersionRecord(
                pdm_assoc["time_stamp"],
                MetadataPath(pdm_assoc["path"]),
                mrr_or_tree)

        return version_records

    def map_in_impl(self,
                    version_list: "VersionList",
                    reference: Reference) -> None:

        from dataladmetadatamodel.versionlist import VersionList

        assert isinstance(version_list, VersionList)
        version_list.version_set = self._get_version_records(reference)

    def map_out_impl(self,
                     version_list: "VersionList",
                     destination: str,
                     force_write: bool
                     ) -> Reference:

        from dataladmetadatamodel.versionlist import VersionList

        assert isinstance(version_list, VersionList)
        json_object = [
            {
                "primary_data_version": primary_data_version,
                "time_stamp": version_record.time_stamp,
                "path": version_record.path.as_posix(),
                "dataset_tree": version_record.element.write_out(destination).to_json_obj()
            }
            for primary_data_version, version_record in version_list.version_set.items()
        ]

        location = git_save_json(destination, json_object)
        return Reference("git", destination, "VersionList", location)


class TreeVersionListGitMapper(VersionListGitMapper):
    def map_in_impl(self,
                    tree_version_list: "TreeVersionList",
                    reference: Reference) -> None:

        from dataladmetadatamodel.versionlist import TreeVersionList

        assert isinstance(tree_version_list, TreeVersionList)
        tree_version_list.version_set = self._get_version_records(reference)

    def map_out_impl(self,
                     tree_version_list: "TreeVersionList",
                     destination: str,
                     force_write: bool
                     ) -> Reference:

        from dataladmetadatamodel.versionlist import TreeVersionList

        assert isinstance(tree_version_list, TreeVersionList)
        reference = super().map_out_impl(tree_version_list, destination, force_write)
        git_update_ref(
            destination,
            GitReference.TREE_VERSION_LIST.value,
            reference.location)
        return reference
