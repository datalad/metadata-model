import subprocess
import tempfile
import unittest
from pathlib import Path

from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.versionlist import (
    VersionList,
    VersionRecord
)
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references

from .utils import (
    assert_dataset_trees_equal,
    create_dataset_tree
)


file_test_paths = [
    MetadataPath("a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x")]

dataset_test_paths = [
    [
        MetadataPath(""),
        MetadataPath("d1"),
        MetadataPath("d1/d1.1"),
        MetadataPath("d2"),
        MetadataPath("d2/d2.1/d2.1.1"),
        MetadataPath("d3/d3.1")
    ],
    [
        MetadataPath(""),
        MetadataPath("e1"),
        MetadataPath("e1/e1.1"),
        MetadataPath("e2"),
        MetadataPath("e2/e2.1/e2.1.1"),
        MetadataPath("e3/e3.1")
    ]
]


class TestVersionList(unittest.TestCase):

    def test_basic(self):
        VersionList()

    def test_copy_end_to_end(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            dataset_trees = [
                create_dataset_tree(
                    dataset_test_paths[index],
                    file_test_paths)
                for index in range(2)]

            dataset_trees[0].write_out(original_dir)
            dataset_trees[0].purge()

            dataset_trees[1].write_out(original_dir)

            version_list = VersionList(initial_set={
                "v1": {
                    MetadataPath("a"): VersionRecord(
                        "0.1",
                        MetadataPath("a"),
                        dataset_trees[0]
                    )
                },
                "v2": {
                    MetadataPath("b"): VersionRecord(
                        "0.2",
                        MetadataPath("b"),
                        dataset_trees[1]
                    )
                }
            })

            version_list.write_out(original_dir)

            path_prefix = "x/y/z"
            copied_version_list = version_list.deepcopy(
                new_destination=copy_dir,
                path_prefix=MetadataPath(path_prefix))

            # Check that the mapping state of the original
            # has not changed.
            self.assertFalse(dataset_trees[0].mtree.mapped)
            self.assertTrue(dataset_trees[1].mtree.mapped)

            # Read the copied version list
            copied_version_list.read_in()

            # Check that the copied elements are unmapped
            for _, (_, _, copied_dataset_tree) in copied_version_list.versioned_elements:
                self.assertFalse(copied_dataset_tree.mtree.mapped)

            # Compare the version lists, taking modified dataset tree paths into account
            for primary_version, (_, path, dataset_tree) in version_list.versioned_elements:
                expected_path = path_prefix / path
                _, copy_path, copied_dataset_tree = copied_version_list.get_versioned_element(primary_version, expected_path)
                self.assertEqual(expected_path, copy_path)
                dataset_tree.read_in()
                copied_dataset_tree.read_in()
                assert_dataset_trees_equal(self, dataset_tree, copied_dataset_tree, True)
                # NB! dataset tree copying is tested in dataset-tree related unit tests


if __name__ == '__main__':
    unittest.main()
