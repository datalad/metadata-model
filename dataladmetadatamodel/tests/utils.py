import unittest
from typing import Any, List
from uuid import UUID

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mappableobject import MappableObject


uuid_pattern = "0000000000000000000000000000{:04x}"
version_pattern = "000000000000000000000000000000000000{:04x}"


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
                                  a_object: MappableObject,
                                  b_object: MappableObject,
                                  a_purge_unsafe: bool,
                                  equality_asserter):

    a_object = a_object.read_in()
    b_object = b_object.read_in()

    equality_asserter(test_case, a_object, b_object, a_purge_unsafe)

    a_object.purge(a_purge_unsafe)
    b_object.purge(a_purge_unsafe)   # TODO:


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
            a_mrr,
            b_mrr,
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

    # Compare the metadata remainder
    test_case.assertEqual(a.dataset_identifier, b.dataset_identifier)
    test_case.assertEqual(a.dataset_version, b.dataset_version)


def create_file_tree(paths: List[MetadataPath]) -> FileTree:

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


def create_dataset_tree(dataset_paths: List[MetadataPath],
                        file_tree_paths: List[MetadataPath]) -> DatasetTree:

    dataset_tree = DatasetTree()
    for index, path in enumerate(dataset_paths):

        metadata = Metadata()
        file_tree = create_file_tree(file_tree_paths)

        mrr = MetadataRootRecord(
            UUID(uuid_pattern.format(index)),
            version_pattern.format(index),
            metadata,
            file_tree)
        dataset_tree.add_dataset(path, mrr)

    return dataset_tree
