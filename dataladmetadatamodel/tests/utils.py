import unittest
from typing import Any

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord


def assert_equal(test_case: unittest.TestCase,
                 object_a: Any,
                 object_b: Any,
                 _: bool,
                 ):
    test_case.assertEqual(object_a, object_b)


def assert_connector_objects_equal(test_case: unittest.TestCase,
                                   a_connector: Connector,
                                   b_connector: Connector,
                                   a_purge_unsafe: bool,
                                   equality_asserter):

    a_object = a_connector.load_object()
    b_object = b_connector.load_object()

    equality_asserter(test_case, a_object, b_object, a_purge_unsafe)

    a_object.purge(a_purge_unsafe)
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
        list(map(lambda x: x[0], a_entries)),
        list(map(lambda x: x[0], b_entries)))

    # Compare metadata elements
    for a_connector, b_connector in zip(
            map(lambda x: x[1], a_entries),
            map(lambda x: x[1], b_entries)):

        # TODO: proper metadata comparison instead of assertEqual
        assert_connector_objects_equal(
            test_case,
            a_connector,
            b_connector,
            unsafe,
            assert_equal)


def assert_dataset_trees_equal(test_case: unittest.TestCase,
                               a: DatasetTree,
                               b: DatasetTree,
                               unsafe: bool
                               ):

    a_entries = list(a.get_dataset_paths())
    b_entries = list(b.get_dataset_paths())

    # Compare paths
    test_case.assertListEqual(
        list(map(lambda x: x[0], a_entries)),
        list(map(lambda x: x[0], b_entries)))

    # Compare metadata_root_records
    for a_connector, b_connector in zip(
            map(lambda x: x[1], a_entries),
            map(lambda x: x[1], b_entries)):

        assert_connector_objects_equal(
            test_case,
            a_connector,
            b_connector,
            unsafe,
            assert_mrrs_equal)


def assert_mrrs_equal(test_case: unittest.TestCase,
                      a: MetadataRootRecord,
                      b: MetadataRootRecord,
                      unsafe: bool
                      ):

    # Compare dataset level metadata
    assert_connector_objects_equal(
        test_case,
        a.dataset_level_metadata,
        b.dataset_level_metadata,
        unsafe,
        assert_equal)

    # Compare file trees
    assert_connector_objects_equal(
        test_case,
        a.file_tree,
        b.file_tree,
        unsafe,
        assert_file_trees_equal
    )

    # Compare the metadata remainder
    test_case.assertEqual(a.dataset_identifier, b.dataset_identifier)
    test_case.assertEqual(a.dataset_version, b.dataset_version)
