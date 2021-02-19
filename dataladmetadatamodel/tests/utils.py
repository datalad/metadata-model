import subprocess
import tempfile
import unittest

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references


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

        a_metadata = a_connector.load_object()
        b_metadata = b_connector.load_object()

        # TODO: proper metadata comparison
        test_case.assertEqual(a_metadata.instance_sets, b_metadata.instance_sets)

        # Use unsafe purge for a, because it might just exist
        # in memory and we don't want to write it to a backend
        a_connector.purge(unsafe)
        b_connector.purge()


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

    # Compare metadata elements
    for a_connector, b_connector in zip(
            map(lambda x: x[1], a_entries),
            map(lambda x: x[1], b_entries)):

        a_metadata_root_record = a_connector.load_object()
        b_metadata_root_record = b_connector.load_object()

        test_case.assertEqual(
            a_metadata_root_record,
            b_metadata_root_record)

        # TODO: proper metadata root record comparison, i.e.
        #  load file trees, compare them and purge them, and
        #  load dataset-level metadata, compare them and purge them.

        # Use unsafe purge for a, because it might just exist
        # in memory and we don't want to write it to a backend
        a_connector.purge(unsafe)
        b_connector.purge()

