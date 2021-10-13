import time
import unittest
from typing import (
    cast,
    Any,
    List,
    Optional,
    Union,
)
from uuid import UUID

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mtreeproxy import MTreeProxy
from dataladmetadatamodel.uuidset import UUIDSet
from dataladmetadatamodel.versionlist import VersionList
from dataladmetadatamodel.mapper.reference import Reference


uuid_pattern = "9900{:04x}00000000000000000000{:04x}"
version_pattern = "ea{:04x}000000000000000000000000000000{:04x}"


default_file_tree_paths = [
    MetadataPath("a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x")]

default_dataset_tree_paths = [
    MetadataPath("d1"),
    MetadataPath("d1/d1.1"),
    MetadataPath("d2"),
    MetadataPath("d2/d2.1/d2.1.1"),
    MetadataPath("d3/d3.1")]


def get_uuid(n: int) -> UUID:
    return UUID(uuid_pattern.format(n, n))


def get_location(n: int) -> str:
    return version_pattern.format(n, n)


def get_version(n: int) -> str:
    return get_location(n)


def assert_equal(test_case: unittest.TestCase,
                 object_a: Any,
                 object_b: Any,
                 _: bool,
                 ):
    test_case.assertEqual(object_a, object_b)


def assert_metadata_equal(test_case: unittest.TestCase,
                          object_a: Any,
                          object_b: Any,
                          _: bool,
                          ):

    test_case.assertEqual(object_a, object_b)


def assert_mrr_equal(test_case: unittest.TestCase,
                     a_mrr: MetadataRootRecord,
                     b_mrr: MetadataRootRecord,
                     a_purge_unsafe: bool,
                     ):

    test_case.assertEqual(a_mrr.dataset_identifier, b_mrr.dataset_identifier)
    test_case.assertEqual(a_mrr.dataset_version, b_mrr.dataset_version)
    assert_mappable_objects_equal(
        test_case,
        a_mrr.dataset_level_metadata,
        b_mrr.dataset_level_metadata,
        a_purge_unsafe,
        assert_metadata_equal)

    assert_mappable_objects_equal(
        test_case,
        a_mrr.file_tree,
        b_mrr.file_tree,
        a_purge_unsafe,
        assert_file_trees_equal)


def assert_mappable_objects_equal(test_case: unittest.TestCase,
                                  a_object: Union[MappableObject, MTreeProxy],
                                  b_object: Union[MappableObject, MTreeProxy],
                                  a_purge_unsafe: bool,
                                  equality_asserter):

    a_object = a_object.read_in()
    b_object = b_object.read_in()

    equality_asserter(test_case, a_object, b_object, a_purge_unsafe)

    if a_purge_unsafe is False:
        a_object.purge()
    b_object.purge()


def assert_file_trees_equal(test_case: unittest.TestCase,
                            a: FileTree,
                            b: FileTree,
                            unsafe: bool
                            ):

    a_entries = list(a.get_paths_recursive())
    b_entries = list(b.get_paths_recursive())

    # Compare paths
    test_case.assertListEqual(
        sorted(list(map(lambda x: x[0], a_entries))),
        sorted(list(map(lambda x: x[0], b_entries))))

    # Compare metadata elements
    for a_object, b_object in zip(
            map(lambda x: x[1], a_entries),
            map(lambda x: x[1], b_entries)):

        # TODO: proper metadata comparison instead of assertEqual
        assert_mappable_objects_equal(
            test_case,
            a_object,
            b_object,
            unsafe,
            assert_equal)


def assert_dataset_trees_equal(test_case: unittest.TestCase,
                               a: DatasetTree,
                               b: DatasetTree,
                               a_purge_unsafe: bool
                               ):

    a_entries = list(a.get_dataset_paths())
    b_entries = list(b.get_dataset_paths())

    # Compare paths
    test_case.assertListEqual(
        list(map(lambda x: x[0], a_entries)),
        list(map(lambda x: x[0], b_entries)))

    # Compare metadata_root_records
    for a_mrr, b_mrr in zip(
            map(lambda x: x[1], a_entries),
            map(lambda x: x[1], b_entries)):

        assert_mrr_equal(
            test_case,
            a_mrr.read_in(),
            b_mrr.read_in(),
            a_purge_unsafe)


def assert_mrrs_equal(test_case: unittest.TestCase,
                      a: MetadataRootRecord,
                      b: MetadataRootRecord,
                      unsafe: bool
                      ):

    # Compare dataset level metadata
    assert_mappable_objects_equal(
        test_case,
        a.dataset_level_metadata,
        b.dataset_level_metadata,
        unsafe,
        assert_equal)

    # Compare file trees
    assert_mappable_objects_equal(
        test_case,
        a.file_tree,
        b.file_tree,
        unsafe,
        assert_file_trees_equal
    )

    # Compare the remaining metadata
    test_case.assertEqual(a.dataset_identifier, b.dataset_identifier)
    test_case.assertEqual(a.dataset_version, b.dataset_version)


def assert_version_lists_equal(test_case: unittest.TestCase,
                               a: VersionList,
                               b: VersionList,
                               unsafe: bool
                               ):

    a_entries = [a.get_versioned_element(pdv) for pdv in a.versions()]
    b_entries = [b.get_versioned_element(pdv) for pdv in b.versions()]

    for a_entry, b_entry in zip(a_entries, b_entries):
        test_case.assertEqual(a_entry[0], b_entry[0])
        test_case.assertEqual(a_entry[1], b_entry[1])
        test_case.assertIsInstance(a_entry[2], (DatasetTree, MetadataRootRecord))
        test_case.assertIsInstance(b_entry[2], (DatasetTree, MetadataRootRecord))
        if isinstance(a_entry[2], DatasetTree):
            assert_dataset_trees_equal(
                test_case,
                cast(DatasetTree, a_entry[2]),
                cast(DatasetTree, b_entry[2]),
                unsafe)
        else:
            assert_mrr_equal(
                test_case,
                cast(MetadataRootRecord, a_entry[2]),
                cast(MetadataRootRecord, b_entry[2]),
                unsafe)


def assert_uuid_sets_equal(test_case: unittest.TestCase,
                           a_uuid_set: UUIDSet,
                           b_uuid_set: UUIDSet):

    for dataset_id in a_uuid_set.uuids():
        a_version_list = a_uuid_set.get_version_list(dataset_id)
        b_version_list = b_uuid_set.get_version_list(dataset_id)
        assert_version_lists_equal(test_case,
                                   a_version_list,
                                   b_version_list,
                                   True)


def create_file_tree(paths: Optional[List[MetadataPath]] = None) -> FileTree:

    paths = paths or default_file_tree_paths

    file_tree = FileTree()
    for path in paths:
        metadata = Metadata()
        file_tree.add_metadata(path, metadata)
    return file_tree


def create_file_tree_with_metadata(paths: List[MetadataPath],
                                   metadata: List[Metadata]) -> FileTree:

    assert len(paths) == len(metadata)

    file_tree = FileTree()
    for path, md in zip(paths, metadata):
        file_tree.add_metadata(path, md)

    return file_tree


def create_dataset_tree(dataset_tree_paths: Optional[List[MetadataPath]] = None,
                        file_tree_paths: Optional[List[MetadataPath]] = None,
                        initial_mrr: Optional[MetadataRootRecord] = None
                        ) -> DatasetTree:

    dataset_tree_paths = dataset_tree_paths or default_dataset_tree_paths
    file_tree_paths = file_tree_paths or default_file_tree_paths

    dataset_tree = DatasetTree()
    for index, path in enumerate(dataset_tree_paths):

        metadata = Metadata()
        file_tree = create_file_tree(file_tree_paths)

        if initial_mrr is None:
            mrr = MetadataRootRecord(
                get_uuid(index),
                get_version(index),
                metadata,
                file_tree)
        else:
            mrr = initial_mrr

        dataset_tree.add_dataset(path, mrr)

    return dataset_tree


class MMDummy:
    def __init__(self,
                 info: str = "",
                 is_mapped: bool = False,
                 copied_from: Optional["MMDummy"] = None):
        self.info = info or f"MMDummy created at {time.time()}"
        self.mapped = is_mapped
        self.copied_from = copied_from

    def deepcopy(self, *args, **kwargs):
        return MMDummy(self.info, False, self)

    def read_in(self, backend_type="git") -> Any:
        self.mapped = True
        return self

    def write_out(self,
                  destination: Optional[str] = None,
                  backend_type: str = "git",
                  force_write: bool = False) -> Reference:
        return Reference(
            "MMDummy",
            get_location(0x51))

    def purge(self, force: bool = False):
        self.mapped = False
        return
