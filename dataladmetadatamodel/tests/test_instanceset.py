import unittest

from dataladmetadatamodel.metadata import ExtractorConfiguration, MetadataInstance, MetadataInstanceSet


class TestSerialization(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata_instance_set = MetadataInstanceSet()
        self.metadata_instance_set.add_metadata_instance(
            MetadataInstance(
                1.2,
                "name",
                "email",
                ExtractorConfiguration(
                    "2.0",
                    {"p1": "v1"}
                ),
                "metadata-content"
            )
        )

    def assert_equal_to_pattern(self, instance_set: MetadataInstanceSet) -> None:
        self.assertListEqual(
            self.metadata_instance_set.parameter_set,
            instance_set.parameter_set
        )

        self.assertDictEqual(
            self.metadata_instance_set.instance_set,
            instance_set.instance_set
        )

    def test_object_round_trip(self):
        json_obj = self.metadata_instance_set.to_json_obj()
        ins2 = MetadataInstanceSet.from_json_obj(json_obj)
        self.assert_equal_to_pattern(ins2)

    def test_string_round_trip(self):
        json_str = self.metadata_instance_set.to_json_str()
        ins2 = MetadataInstanceSet.from_json_str(json_str)
        self.assert_equal_to_pattern(ins2)


if __name__ == '__main__':
    unittest.main()
