from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_save_json,
    git_update_ref,
)
from dataladmetadatamodel.mapper.gitmapper.objectreference import GitReference
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class VersionListGitMapper(Mapper):
    """
    Map version lists to git objects.
    The objects are blobs containing json strings that
    define a list of primary data-metadata associations.
    """

    def _get_version_records(self,
                             realm: str,
                             reference: Reference) -> dict:
        from dataladmetadatamodel.datasettree import DatasetTree
        from dataladmetadatamodel.metadatapath import MetadataPath
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
        from dataladmetadatamodel.versionlist import VersionRecord

        assert isinstance(reference, Reference)

        json_object = git_load_json(realm, reference.location)

        version_records = {}
        for pdm_assoc in json_object:

            reference = Reference.from_json_obj(pdm_assoc["dataset_tree"])
            if reference.class_name in ("DatasetTree", "MTreeNode"):
                mrr_or_tree = DatasetTree(realm=realm, reference=reference)
            elif reference.class_name == "MetadataRootRecord":
                mrr_or_tree = MetadataRootRecord(None, None, None, None, realm, reference)
            else:
                raise ValueError(
                    f"unexpected tree class in primary data-metadata "
                    f"assoc: ({reference.class_name})")

            primary_data_version = pdm_assoc["primary_data_version"]
            prefix_path = MetadataPath(pdm_assoc["path"])
            if primary_data_version not in version_records:
                version_records[primary_data_version] = dict()
            version_records[primary_data_version][prefix_path] = \
                VersionRecord(
                    pdm_assoc["time_stamp"],
                    prefix_path,
                    mrr_or_tree)

        return version_records

    def map_in_impl(self,
                    version_list: "VersionList",
                    realm: str,
                    reference: Reference) -> None:

        from dataladmetadatamodel.versionlist import VersionList

        assert isinstance(version_list, VersionList)
        version_list.version_set = self._get_version_records(realm, reference)

    def map_out_impl(self,
                     version_list: "VersionList",
                     realm: str,
                     force_write: bool
                     ) -> Reference:

        from dataladmetadatamodel.versionlist import VersionList

        assert isinstance(version_list, VersionList)
        json_object = [
            {
                "primary_data_version": primary_data_version,
                "time_stamp": version_record.time_stamp,
                "path": version_record.prefix_path.as_posix(),
                "dataset_tree": version_record.element.write_out(realm).to_json_obj()
            }
            for primary_data_version, prefix_set in version_list.version_set.items()
            for version_record in prefix_set.values()
        ]

        location = git_save_json(realm, json_object)
        return Reference("VersionList", location)


class TreeVersionListGitMapper(VersionListGitMapper):
    def map_in_impl(self,
                    tree_version_list: "TreeVersionList",
                    realm: str,
                    reference: Reference) -> None:

        from dataladmetadatamodel.versionlist import TreeVersionList

        assert isinstance(tree_version_list, TreeVersionList)
        tree_version_list.version_set = self._get_version_records(realm, reference)

    def map_out_impl(self,
                     tree_version_list: "TreeVersionList",
                     realm: str,
                     force_write: bool
                     ) -> Reference:

        from dataladmetadatamodel.versionlist import TreeVersionList

        assert isinstance(tree_version_list, TreeVersionList)
        reference = super().map_out_impl(tree_version_list, realm, force_write)
        git_update_ref(
            realm,
            GitReference.TREE_VERSION_LIST.value,
            reference.location)
        return reference
