from typing import Dict, Iterable, Optional, Tuple, Union

from dataladmetadatamodel.connector import ConnectedObject, Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mapper.reference import Reference


class VersionRecord:
    def __init__(self,
                 time_stamp: str,
                 path: Optional[MetadataPath],
                 element_connector: Connector):

        self.time_stamp = time_stamp
        self.path = path or MetadataPath("")
        self.element_connector = element_connector

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "VersionRecord":

        return VersionRecord(
            self.time_stamp,
            self.path,
            self.element_connector.deepcopy(new_mapper_family, new_realm)
        )


class VersionList(ConnectedObject):
    def __init__(self,
                 mapper_family: str,
                 realm: str,
                 initial_set: Optional[Dict[str, VersionRecord]] = None):

        super().__init__()
        self.mapper_family = mapper_family
        self.realm = realm
        self.version_set = initial_set or dict()

    def _get_version_record(self, primary_data_version) -> VersionRecord:
        return self.version_set[primary_data_version]

    def _get_dst_connector(self, primary_data_version) -> Connector:
        return self._get_version_record(primary_data_version).element_connector

    def is_modified(self) -> bool:
        return (
            super().is_modified()
            or any(
                map(
                    lambda vr: vr.element_connector.is_object_modified(),
                    self.version_set.values())))

    def save(self) -> Reference:
        """
        This method persists the bottom-half of all modified
        connectors by delegating it to the ConnectorDict. Then
        it saves the properties of the VersionList and the top-half
        of the connectors with the appropriate class mapper.
        """
        self.un_touch()

        for primary_data_version, version_record in self.version_set.items():
            version_record.element_connector.save_object()

        return Reference(
            self.mapper_family,
            self.realm,
            "VersionList",
            get_mapper(
                self.mapper_family,
                "VersionList")(self.realm).unmap(self))

    def versions(self) -> Iterable:
        return self.version_set.keys()

    def get_versioned_element(self,
                              primary_data_version: str
                              ) -> Tuple[str, MetadataPath, Union[DatasetTree, MetadataRootRecord]]:

        """
        Get the dataset tree or metadata root record,
        its timestamp and path for the given version.
        If it is not mapped yet, it will be mapped.
        """
        version_record = self._get_version_record(primary_data_version)
        return (
            version_record.time_stamp,
            version_record.path,
            version_record.element_connector.load_object())

    def set_versioned_element(self,
                              primary_data_version: str,
                              time_stamp: str,
                              path: MetadataPath,
                              element: Union[DatasetTree, MetadataRootRecord]):
        """
        Set a new or updated dataset tree.
        Existing references are deleted.
        The entry is marked as dirty.
        """
        self.touch()

        self.version_set[primary_data_version] = VersionRecord(
            time_stamp,
            path,
            Connector.from_object(element))

    def unget_versioned_element(self,
                                primary_data_version: str):
        """
        Remove a metadata record from memory. First, persist the
        current status via save_object ---which will write it to
        the backend, if it was changed or--- then purge it
        from memory.
        """
        dst_connector = self._get_dst_connector(primary_data_version)
        dst_connector.save_object()
        dst_connector.purge()

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None,
                 path_prefix: Optional[MetadataPath] = None
                 ) -> "VersionList":

        new_mapper_family = new_mapper_family or self.mapper_family
        new_realm = new_realm or self.realm
        path_prefix = path_prefix or MetadataPath("")

        copied_version_list = VersionList(new_mapper_family, new_realm)

        for primary_data_version, version_record in self.version_set.items():

            metadata_root_record = version_record.element_connector.load_object()

            copied_version_list.set_versioned_element(
                primary_data_version,
                version_record.time_stamp,
                path_prefix / version_record.path,
                metadata_root_record.deepcopy(new_mapper_family, new_realm))

            version_record.element_connector.purge()

        return copied_version_list


class TreeVersionList(VersionList):
    """
    Thin wrapper around version list to support tree-version list
    specific mapping, for example in the git mapper, which will
    update a reference, if mapping an TreeVersionList instance.
    """
    def save(self) -> Reference:

        self.un_touch()

        # Save all dataset tree connectors that are mapped
        for primary_data_version, version_record in self.version_set.items():
            version_record.element_connector.save_object()

        return Reference(
            self.mapper_family,
            self.realm,
            "TreeVersionList",
            get_mapper(
                self.mapper_family,
                "TreeVersionList")(self.realm).unmap(self))

    def get_dataset_tree(self,
                         primary_data_version: str
                         ) -> Tuple[str, DatasetTree]:

        time_stamp, _, dataset_tree = super().get_versioned_element(
            primary_data_version)
        return time_stamp, dataset_tree

    def set_dataset_tree(self,
                         primary_data_version: str,
                         time_stamp: str,
                         dataset_tree: DatasetTree
                         ):

        self.touch()

        return super().set_versioned_element(
            primary_data_version,
            time_stamp,
            MetadataPath(""),
            dataset_tree)

    def unget_dataset_tree(self,
                           primary_data_version: str):

        super().unget_versioned_element(primary_data_version)

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None,
                 path_prefix: Optional[MetadataPath] = None
                 ) -> "TreeVersionList":

        new_mapper_family = new_mapper_family or self.mapper_family
        new_realm = new_realm or self.realm
        path_prefix = path_prefix or MetadataPath("")

        copied_version_list = TreeVersionList(new_mapper_family, new_realm)

        for primary_data_version, version_record in self.version_set.items():

            metadata_root_record = version_record.element_connector.load_object()

            copied_version_list.set_versioned_element(
                primary_data_version,
                version_record.time_stamp,
                path_prefix / version_record.path,
                metadata_root_record.deepcopy(new_mapper_family, new_realm))

            version_record.element_connector.purge()

        return copied_version_list
