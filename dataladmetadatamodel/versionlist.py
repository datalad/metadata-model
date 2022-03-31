from typing import (
    cast,
    Dict,
    Generator,
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


unknown_version = "unknown"


class VersionRecord:
    def __init__(self,
                 time_stamp: str,
                 prefix_path: Optional[MetadataPath],
                 element: Union[DatasetTree, MetadataRootRecord]):

        assert isinstance(time_stamp, str)
        assert isinstance(prefix_path, (type(None), MetadataPath)), f"prefix_path is type: {type(prefix_path).__name__}"
        assert isinstance(element, (DatasetTree, MetadataRootRecord))

        self.time_stamp = time_stamp
        self.prefix_path = prefix_path or MetadataPath("")
        self.element = element

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_destination: Optional[str] = None
                 ) -> "VersionRecord":

        return VersionRecord(
            self.time_stamp,
            self.prefix_path,
            self.element.deepcopy(
                new_mapper_family,
                new_destination))


class VersionList(MappableObject):
    def __init__(self,
                 initial_set: Optional[Dict[str, Dict[MetadataPath, VersionRecord]]] = None,
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(initial_set, (type(None), dict))
        assert isinstance(realm, (type(None), str))
        assert isinstance(reference, (type(None), Reference))

        super().__init__(realm, reference)
        self.version_set: Dict[str, Dict[MetadataPath, VersionRecord]] = \
            initial_set or dict()

    def __len__(self):
        return sum([len(path_dict) for path_dict in self.version_set.values()])

    def purge_impl(self):
        for version, prefixed_set in self.version_set.items():
            for version_record in prefixed_set.values():
                version_record.element.purge()
        self.version_set = dict()

    def _get_version_record(self,
                            primary_data_version: str,
                            prefix_path: MetadataPath) -> VersionRecord:
        self.ensure_mapped()
        return self.version_set[primary_data_version][prefix_path]

    def _get_version_records(self,
                             primary_data_version: str
                             ) -> Iterable[VersionRecord]:
        self.ensure_mapped()
        return self.version_set[primary_data_version].values()

    def _iterate_version_records(self) -> Generator:
        self.ensure_mapped()
        yield from (
            (version, version_record)
            for version, prefixed_set in self.version_set.items()
            for version_record in prefixed_set.values()
        )

    def modifiable_sub_objects_impl(self) -> Iterable[MappableObject]:
        yield from map(
            lambda vvr: vvr[1].element,
            self._iterate_version_records())

    def versions(self) -> Iterable:
        self.ensure_mapped()
        yield from map(
            lambda vvr: vvr[0],
            self._iterate_version_records())

    def versions_and_prefix_paths(self) -> Iterable:
        self.ensure_mapped()
        yield from map(
            lambda vvr: (vvr[0], vvr[1].prefix_path),
            self._iterate_version_records())

    def get_versioned_element(self,
                              primary_data_version: str,
                              prefix_path: MetadataPath,
                              ) -> Tuple[str, MetadataPath, MappableObject]:
        """
        Get the dataset tree or metadata root record,
        its timestamp and prefix_path for the given version.
        If it is not mapped yet, it will be mapped.
        """
        self.ensure_mapped()
        version_record = self._get_version_record(
            primary_data_version,
            prefix_path)
        version_record.element.read_in()
        return (
            version_record.time_stamp,
            version_record.prefix_path,
            version_record.element)

    def get_versioned_elements(self,
                               primary_data_version: str,
                               ) -> Iterable[Tuple[str, MetadataPath, MappableObject]]:
        """
        Get all dataset trees or metadata root records, including their
        timestamp and prefix paths for the given version.
        If they are not mapped yet, they will be mapped.
        """
        self.ensure_mapped()
        for version_record in self._get_version_records(primary_data_version):
            version_record.element.read_in()
            yield (
                version_record.time_stamp,
                version_record.prefix_path,
                version_record.element)

    @property
    def versioned_elements(self
                           ) -> Iterable[Tuple[str, Tuple[str, MetadataPath, MappableObject]]]:
        """
        Get an iterable of all versions and their records
        """
        self.ensure_mapped()
        yield from (
            (
                version,
                (
                    version_record.time_stamp,
                    version_record.prefix_path,
                    version_record.element
                )
            )
            for version, version_record in self._iterate_version_records())

    def set_versioned_element(self,
                              primary_data_version: str,
                              time_stamp: str,
                              prefix_path: MetadataPath,
                              element: Union[DatasetTree, MetadataRootRecord]):
        """
        Set a new or updated dataset tree.
        Existing references are deleted.
        The entry is marked as dirty.
        """
        self.ensure_mapped()
        self.touch()
        if primary_data_version not in self.version_set:
            self.version_set[primary_data_version] = dict()
        self.version_set[primary_data_version][prefix_path] = VersionRecord(
            time_stamp,
            prefix_path,
            element)

    def unget_versioned_element(self,
                                primary_data_version: str,
                                prefix_path: MetadataPath,
                                new_destination: Optional[str] = None):
        """
        Remove a metadata record from memory. First, persist the
        current status via save_object ---which will write it to
        the backend, if it was changed or--- then purge it
        from memory.
        """
        version_record = self.version_set[primary_data_version][prefix_path]
        version_record.element.write_out(new_destination)
        version_record.element.purge()

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs
                      ) -> "VersionList":

        path_prefix = kwargs.get("path_prefix", MetadataPath(""))

        copied_version_list = VersionList()
        for primary_data_version, prefix_set in self.version_set.items():
            for version_record in prefix_set.values():
                copied_version_list.set_versioned_element(
                    primary_data_version,
                    version_record.time_stamp,
                    path_prefix / version_record.prefix_path,
                    version_record.element.deepcopy(
                        new_mapper_family,
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
                         primary_data_version: str,
                         prefix_path: MetadataPath,
                         ) -> Tuple[str, MetadataPath, DatasetTree]:

        self.ensure_mapped()
        time_stamp, prefix_path, dataset_tree = super().get_versioned_element(
            primary_data_version,
            prefix_path)
        dataset_tree = cast(DatasetTree, dataset_tree)
        return time_stamp, prefix_path, dataset_tree

    def get_dataset_trees(self,
                          primary_data_version: str,
                          ) -> Iterable[Tuple[str, MetadataPath, DatasetTree]]:

        self.ensure_mapped()
        return super().get_versioned_elements(primary_data_version)

    def set_dataset_tree(self,
                         primary_data_version: str,
                         time_stamp: str,
                         prefix_path: MetadataPath,
                         dataset_tree: DatasetTree,
                         ):

        self.ensure_mapped()
        self.touch()
        return super().set_versioned_element(
            primary_data_version=primary_data_version,
            time_stamp=time_stamp,
            prefix_path=prefix_path,
            element=dataset_tree)

    def unget_dataset_tree(self,
                           primary_data_version: str,
                           prefix_path: MetadataPath,
                           new_destination: str):

        assert isinstance(primary_data_version, str)
        assert isinstance(new_destination, str)
        super().unget_versioned_element(
            primary_data_version,
            prefix_path,
            new_destination)

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs
                      ) -> "TreeVersionList":

        path_prefix = kwargs.get("path_prefix", MetadataPath(""))

        copied_version_list = TreeVersionList()
        for primary_data_version, prefix_set in self.version_set.items():
            for version_record in prefix_set.values():
                copied_version_list.set_versioned_element(
                    primary_data_version,
                    version_record.time_stamp,
                    path_prefix / version_record.prefix_path,
                    cast(MetadataRootRecord,
                         version_record.element.deepcopy(
                            new_mapper_family,
                            new_destination)))

        copied_version_list.write_out(new_destination)
        copied_version_list.purge()
        return copied_version_list
