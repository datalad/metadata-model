import unittest

from ..metadatapath import MetadataPath


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


if __name__ == '__main__':
    unittest.main()
