from typing import (
    cast,
    Dict,
    Iterable,
    Optional,
    Tuple,
    Union,
)

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mapper.reference import Reference


class VersionRecord:
    def __init__(self,
                 time_stamp: str,
                 path: Optional[MetadataPath],
                 element: Union[DatasetTree, MetadataRootRecord]):

        assert isinstance(time_stamp, str)
        assert isinstance(path, (type(None), MetadataPath))
        assert isinstance(element, (DatasetTree, MetadataRootRecord))

        self.time_stamp = time_stamp
        self.path = path or MetadataPath("")
        self.element = element

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_destination: Optional[str] = None
                 ) -> "VersionRecord":

        return VersionRecord(
            self.time_stamp,
            self.path,
            self.element.deepcopy(
                new_mapper_family,
                new_destination))


class VersionList(MappableObject):
    def __init__(self,
                 initial_set: Optional[Dict[str, VersionRecord]] = None,
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(initial_set, (type(None), dict))
        assert isinstance(realm, (type(None), str))
        assert isinstance(reference, (type(None), Reference))

        super().__init__(realm, reference)
        self.version_set: Dict[str, VersionRecord] = initial_set or dict()

    def purge_impl(self):
        for version, version_record in self.version_set.items():
            version_record.element.purge()
        self.version_set = dict()

    def get_modifiable_sub_objects_impl(self) -> Iterable[MappableObject]:
        yield from map(
            lambda version_record: version_record.element,
            self.version_set.values())

    def _get_version_record(self, primary_data_version) -> VersionRecord:
        return self.version_set[primary_data_version]

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
        version_record.element.read_in()
        return (
            version_record.time_stamp,
            version_record.path,
            version_record.element)

    def get_versioned_elements(self
                               ) -> Iterable[Tuple[str, Tuple[str, MetadataPath, MappableObject]]]:
        """
        Get an iterable of all versions and their records
        """
        for version, version_record in self.version_set.items():
            yield version, (
                version_record.time_stamp,
                version_record.path,
                version_record.element)

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
                                primary_data_version: str,
                                new_destination: Optional[str] = None):
        """
        Remove a metadata record from memory. First, persist the
        current status via save_object ---which will write it to
        the backend, if it was changed or--- then purge it
        from memory.
        """
        version_record = self.version_set[primary_data_version]
        version_record.element.write_out(new_destination)
        version_record.element.purge()

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs
                      ) -> "VersionList":

        path_prefix = kwargs.get("path_prefix", MetadataPath(""))

        copied_version_list = VersionList()
        for primary_data_version, version_record in self.version_set.items():
            copied_version_list.set_versioned_element(
                primary_data_version,
                version_record.time_stamp,
                path_prefix / version_record.path,
                version_record.element.deepcopy(new_mapper_family,
                                                new_destination))

        copied_version_list.write_out(new_destination)
        copied_version_list.purge()
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
                           primary_data_version: str,
                           new_destination: str):

        assert isinstance(primary_data_version, str)
        assert isinstance(new_destination, str)
        super().unget_versioned_element(primary_data_version,
                                        new_destination)

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs
                      ) -> "TreeVersionList":

        path_prefix = kwargs.get("path_prefix", MetadataPath(""))

        copied_version_list = TreeVersionList()
        for primary_data_version, version_record in self.version_set.items():

            copied_version_list.set_versioned_element(
                primary_data_version,
                version_record.time_stamp,
                path_prefix / version_record.path,
                cast(MetadataRootRecord,
                     version_record.element.deepcopy(
                        new_mapper_family,
                        new_destination)))

        copied_version_list.write_out(new_destination)
        copied_version_list.purge()
        return copied_version_list
