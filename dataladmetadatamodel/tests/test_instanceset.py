import unittest
from typing import Tuple

from dataladmetadatamodel.metadata import (
    ExtractorConfiguration,
    MetadataInstance,
    MetadataInstanceSet
)


class TestInstanceSetBase(unittest.TestCase):
    def setUp(self) -> None:

        self.metadata_instances = {
            prefix: self.create_metadata_instance(time_stamp, prefix)
            for time_stamp, prefix in ((1.0, "default"), (2.0, "new"))
        }

        self.metadata_instance_set = MetadataInstanceSet()
        self.metadata_instance_set.add_metadata_instance(
            self.metadata_instances["default"][1]
        )

    def create_metadata_instance(self,
                                 time_stamp: float,
                                 prefix: str
                                 ) -> Tuple[ExtractorConfiguration, MetadataInstance]:

        extractor_configuration = ExtractorConfiguration(
            "1.0",
            {"info": f"{prefix}_value"}
        )

        return (
            extractor_configuration,
            MetadataInstance(
                time_stamp,
                f"{prefix}_name",
                f"{prefix}_email",
                extractor_configuration,
                {"metadata 1": f"{prefix}_content"}
            )
        )

    def get_instance(self, prefix):
        return self.metadata_instances[prefix][1]

    def get_configuration(self, prefix):
        return self.metadata_instances[prefix][0]

    def assert_equal_to_pattern(self, instance_set: MetadataInstanceSet) -> None:
        self.assertListEqual(
            self.metadata_instance_set.parameter_set,
            instance_set.parameter_set
        )

        self.assertDictEqual(
            self.metadata_instance_set._instances,
            instance_set._instances
        )


class TestSerialization(TestInstanceSetBase):

    def test_object_round_trip(self):
        json_obj = self.metadata_instance_set.to_json_obj()
        ins2 = MetadataInstanceSet.from_json_obj(json_obj)
        self.assert_equal_to_pattern(ins2)

    def test_string_round_trip(self):
        json_str = self.metadata_instance_set.to_json_str()
        ins2 = MetadataInstanceSet.from_json_str(json_str)
        self.assert_equal_to_pattern(ins2)


class TestUniqueness(TestInstanceSetBase):

    def test_configuration_unity(self):
        # Ensure known state
        configuration_list = self.metadata_instance_set.configurations
        self.assertEqual(1, len(configuration_list))
        self.assertEqual(configuration_list[0], self.get_configuration("default"))

        # Re-add the only instance
        self.metadata_instance_set.add_metadata_instance(
            self.metadata_instance_set.get_instance_for_configuration(
                configuration_list[0]))

        # Ensure nothing has changes
        new_configuration_list = self.metadata_instance_set.configurations
        self.assertEqual(configuration_list, new_configuration_list)
        self.assertEqual(
            self.metadata_instance_set.get_instance_for_configuration(
                configuration_list[0]
            ),
            self.get_instance("default")
        )

    def test_configuration_multiplicity(self):
        configuration_list = self.metadata_instance_set.configurations
        self.assertEqual(1, len(configuration_list))
        self.assertEqual(configuration_list[0], self.get_configuration("default"))

        self.metadata_instance_set.add_metadata_instance(self.get_instance("new"))
        configuration_list = self.metadata_instance_set.configurations
        self.assertEqual(2, len(configuration_list))
        self.assertIn(self.get_configuration("default"), configuration_list)
        self.assertIn(self.get_configuration("new"), configuration_list)


if __name__ == '__main__':
    unittest.main()
