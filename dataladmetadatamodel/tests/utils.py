import unittest
from typing import Any, List
from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord


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
    assert_connector_objects_equal(
        test_case,
        a_mrr.dataset_level_metadata,
        b_mrr.dataset_level_metadata,
        a_purge_unsafe,
        assert_metadata_equal)

    assert_connector_objects_equal(
        test_case,
        a_mrr.file_tree,
        b_mrr.file_tree,
        a_purge_unsafe,
        assert_file_trees_equal)


def assert_connector_objects_equal(test_case: unittest.TestCase,
                                   a_connector: Connector,
                                   b_connector: Connector,
                                   a_purge_unsafe: bool,
                                   equality_asserter):

    a_object = a_connector.load_object()
    b_object = b_connector.load_object()

    equality_asserter(test_case, a_object, b_object, a_purge_unsafe)

    a_connector.purge(a_purge_unsafe)
    b_connector.purge()


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


def create_file_tree(backend: str,
                     realm: str,
                     paths: List[str],
                     ) -> FileTree:

    file_tree = FileTree(backend, realm)
    for path in paths:
        metadata = Metadata(backend, realm)
        file_tree.add_metadata(path, metadata)

    return file_tree


def create_file_tree_with_metadata(backend: str,
                                   realm: str,
                                   paths: List[str],
                                   metadata: List[Metadata]
                                   ) -> FileTree:

    assert len(paths) == len(metadata)

    file_tree = FileTree(backend, realm)
    for path, md in zip(paths, metadata):
        file_tree.add_metadata(path, md)

    return file_tree


def create_dataset_tree(backend: str,
                        realm: str,
                        dataset_paths: List[str],
                        file_tree_paths: List[str],
                        ) -> DatasetTree:

    dataset_tree = DatasetTree(backend, realm)
    for index, path in enumerate(dataset_paths):

        metadata = Metadata(backend, realm)
        file_tree = create_file_tree(backend, realm, file_tree_paths)

        mrr = MetadataRootRecord(
            backend,
            realm,
            UUID(uuid_pattern.format(index)),
            version_pattern.format(index),
            Connector.from_object(metadata),
            Connector.from_object(file_tree)
        )
        dataset_tree.add_dataset(path, mrr)

    return dataset_tree
