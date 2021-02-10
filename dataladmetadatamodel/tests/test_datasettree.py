import unittest
from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord


uuid_0 = UUID("00000000000000000000000000000000")


class TestDatasetTree(unittest.TestCase):
    def test_add_metadata(self):

        paths = ["a/b/c", "a/b/a", "b", "c/d/e"]

        dataset_tree = DatasetTree("git", "/tmp")
        mrr = MetadataRootRecord(
            "git", "/tmp", uuid_0, "00112233",
            Connector.from_object(None),
            Connector.from_object(None)
        )
        for path in paths:
            dataset_tree.add_dataset(path, mrr)

        returned_entries = tuple(dataset_tree.get_dataset_paths())

        returned_paths = [entry[0] for entry in returned_entries]
        self.assertEqual(sorted(paths), sorted(returned_paths))

        for entry in returned_entries:
            self.assertEqual(entry[1], mrr)

    def test_root_node(self):
        dataset_tree = DatasetTree("git", "/tmp")
        mrr = MetadataRootRecord(
            "git", "/tmp", uuid_0, "00112233",
            Connector.from_object(None),
            Connector.from_object(None)
        )
        dataset_tree.add_dataset("", mrr)
        self.assertEqual(dataset_tree.value, mrr)

        returned_entries = tuple(dataset_tree.get_dataset_paths())
        self.assertEqual(len(returned_entries), 1)

        self.assertEqual(returned_entries[0][0], "")
        self.assertEqual(returned_entries[0][1], mrr)


if __name__ == '__main__':
    unittest.main()
