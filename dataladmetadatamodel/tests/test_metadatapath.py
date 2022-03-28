import unittest
from unittest.mock import patch
from pathlib import (
    PurePosixPath,
    PureWindowsPath
)

from dataladmetadatamodel.metadatapath import MetadataPath


class TestMetadataPath(unittest.TestCase):
    def test_empty_join(self):
        self.assertEqual(
            MetadataPath("") / MetadataPath(""),
            MetadataPath(""))

    def test_empty_leading(self):
        self.assertEqual(
            MetadataPath("") / MetadataPath("") / MetadataPath("a"),
            MetadataPath("a"))

    def test_common(self):
        self.assertEqual(
            MetadataPath("") / MetadataPath("") / MetadataPath(
                "a") / MetadataPath("b"),
            MetadataPath("a/b"))

    def test_multiple_dashes(self):
        self.assertEqual(
            MetadataPath("/") / MetadataPath("a//") / MetadataPath("b"),
            MetadataPath("a/b"))

    def test_intermediate_root(self):
        self.assertEqual(
            MetadataPath("/") / MetadataPath("a//") / MetadataPath("/b"),
            MetadataPath("a/b"))

    def test_windows_paths(self):
        # Enforce windows prefix_path interpretation
        with patch("dataladmetadatamodel.metadatapath.PurePosixPath", new=PureWindowsPath):
            metadata_path = MetadataPath("a\\b\\c")
        self.assertEqual(metadata_path, MetadataPath("a/b/c"))

        with patch("dataladmetadatamodel.metadatapath.PurePosixPath", new=PureWindowsPath):
            metadata_path = MetadataPath("a/b/c")
        self.assertEqual(metadata_path, MetadataPath("a/b/c"))

    def test_posix_paths(self):
        with patch("dataladmetadatamodel.metadatapath.PurePosixPath", new=PurePosixPath):
            metadata_path = MetadataPath("a/b/c")
        self.assertEqual(metadata_path, MetadataPath("a/b/c"))


if __name__ == '__main__':
    unittest.main()
