from typing import (
    Dict,
    Iterable,
    Optional,
    Tuple,
    Union
)

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.modifiableobject import ModifiableObject
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mapper.reference import Reference


class VersionRecord:
    def __init__(self,
                 time_stamp: str,
                 path: Optional[MetadataPath],
                 element: Union[DatasetTree, MetadataRootRecord]):

        self.time_stamp = time_stamp
        self.path = path or MetadataPath("")
        self.element = element

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "VersionRecord":

        raise NotImplementedError

        return VersionRecord(
            self.time_stamp,
            self.path,
            self.element.deepcopy(new_mapper_family, new_realm))


class VersionList(MappableObject):
    def __init__(self,
                 initial_set: Optional[Dict[str, VersionRecord]],
                 reference: Optional[Reference] = None):

        super().__init__(reference)
        self.version_set: Dict[str, VersionRecord] = initial_set or dict()

    def _get_version_record(self, primary_data_version) -> VersionRecord:
        return self.version_set[primary_data_version]

    def get_modifiable_sub_objects(self) -> Iterable[ModifiableObject]:
        yield from self.version_set.values()

    def versions(self) -> Iterable:
        return self.version_set.keys()

    def get_versioned_element(self,
                              primary_data_version: str
                              ) -> Tuple[str, MetadataPath, MappableObject]:

        """
        Get the dataset tree or metadata root record,
        its timestamp and path for the given version.
        If it is not mapped yet, it will be mapped.
        """
        version_record = self._get_version_record(primary_data_version)
        return (
            version_record.time_stamp,
            version_record.path,
            version_record.element.read_in())

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
            element)

    def unget_versioned_element(self,
                                primary_data_version: str):
        """
        Remove a metadata record from memory. First, persist the
        current status via save_object ---which will write it to
        the backend, if it was changed or--- then purge it
        from memory.
        """
        version_record = self.version_set[primary_data_version]
        version_record.element.write_out()
        version_record.element.purge()

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None,
                 path_prefix: Optional[MetadataPath] = None
                 ) -> "VersionList":

        raise NotImplementedError
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

    def get_dataset_tree(self,
                         primary_data_version: str
                         ) -> Tuple[str, DatasetTree]:

        time_stamp, _, dataset_tree = super().get_versioned_element(
            primary_data_version)
        assert isinstance(dataset_tree, DatasetTree)
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

        raise NotImplementedError
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
