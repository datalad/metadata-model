import itertools
import logging
import sys
from time import time
from typing import Dict, List, Tuple, Union
from uuid import UUID

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import ExtractorConfiguration, Metadata
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.uuidset import UUIDSet
from dataladmetadatamodel.versionlist import TreeVersionList, VersionList, VersionRecord


JSONObject = Union[List["JSONObject"], Dict[str, "JSONObject"], int, float, str]

MDC_LOGGER = logging.getLogger("metadata_creator")


FILE_LEVEL_FORMATS = ["file-format-1", "file-format-2"]
DATASET_LEVEL_FORMATS = ["dataset-format-1", "dataset-format-2"]


def _create_tree_paths(tree_spec: List[Tuple[int, int]], upper_levels: List[int]) -> List[str]:
    upper_level_postfix = (
        "." + ".".join(map(str, upper_levels))
        if upper_levels
        else ""
    )
    if len(tree_spec) == 1:
        return [
            f"dataset{upper_level_postfix}.{node_number}"
            for node_number in range(tree_spec[0][0])
        ]

    # If we create a path that identifies a dataset, add it the the result list
    result = [
        f"dataset{upper_level_postfix}.{node_number}"
        for node_number in range(tree_spec[0][0])
        if node_number < tree_spec[0][1]
    ]

    return result + [
        f"dataset{upper_level_postfix}.{node_number}/" + sub_spec
        if node_number < tree_spec[0][1]
        else f"dir{upper_level_postfix}.{node_number}/" + sub_spec
        for node_number in range(tree_spec[0][0])
        for sub_spec in _create_tree_paths(tree_spec[1:], upper_levels + [node_number])
    ]


def _create_file_paths(tree_spec: List[int], upper_levels: List[int]) -> List[str]:
    upper_level_postfix = (
        "." + ".".join(map(str, upper_levels))
        if upper_levels
        else ""
    )
    node_count = tree_spec[0]
    if len(tree_spec) == 1:
        return [
            f"file{upper_level_postfix}.{node_number}"
            for node_number in range(node_count)]

    return [
        f"dir{upper_level_postfix}.{node_index}/{sub_tree}"
        for node_index in range(node_count)
        for sub_tree in _create_file_paths(tree_spec[1:], upper_levels + [node_index])
    ]


def _create_metadata(mapper_family: str,
                     realm: str,
                     path: str,
                     formats: List[str],
                     parameter_count: int,
                     invocation_count: int) -> Metadata:

    metadata = Metadata(mapper_family, realm)
    for format in formats:
        parameter_lists = [
            {
                f"{format}-parameter-{invocation}.{i}": f"v-{format}.{invocation}.{i}"
                for i in range(parameter_count)
            }
            for invocation in range(invocation_count)
        ]
        for parameter_list in parameter_lists:

            extractor_configuration = ExtractorConfiguration(
                "1.0",
                parameter_list
            )

            metadata.add_extractor_run(
                int(time()),
                format,
                "Auto-created by create.py",
                "christian.moench@web.de",
                extractor_configuration,
                f'{{"type": "inline", "content": '
                f'"{format}({path})"}}'
            )

    return metadata


def _create_file_tree(mapper_family, realm) -> FileTree:

    file_tree = FileTree(mapper_family, realm)
    file_paths = _create_file_paths([3, 4, 10], [])
    for path in file_paths:
        metadata = _create_metadata(
            mapper_family,
            realm,
            path,
            FILE_LEVEL_FORMATS,
            3,
            2
        )
        file_tree.add_metadata(path, metadata)
    return file_tree


def _create_metadata_root_record(mapper_family: str,
                                 realm: str,
                                 path: str,
                                 uuid: UUID,
                                 primary_data_version: str) -> MetadataRootRecord:

    file_tree = _create_file_tree(mapper_family, realm)

    dataset_level_metadata = _create_metadata(
        mapper_family,
        realm,
        path,
        ["dataset_format_1", "dataset_format_2"],
        4,
        2
    )

    metadata_root_record = MetadataRootRecord(
        mapper_family,
        realm,
        uuid,
        primary_data_version,
        Connector.from_object(dataset_level_metadata),
        Connector.from_object(file_tree)
    )
    return metadata_root_record


def _create_dataset_tree(realm) -> DatasetTree:
    dataset_paths = _create_tree_paths([(3, 1), (2, 1), (3, 3)], [])
    dataset_tree = DatasetTree(realm)
    for index, path in enumerate([""] + dataset_paths):
        dataset_tree.add_dataset(
            path,
            _create_metadata_root_record(
                realm,
                path,
                UUID(f"0000000000000000000000000000{index:04x}"),
                "000102030405060708090a0b0c0d0e0f1011{index:04x}".format(index=index)
            )
        )

    return dataset_tree


def main(argv):
    _, mapper_family, realm = argv

    time_counter = 0
    version_counter = 0

    def get_time_str(counter: int) -> str:
        return str(123456789 + counter)

    def get_primary_data_version(counter: int) -> str:
        return "000102030405060708090a0b0c0d0e0f1011{counter:04x}".format(counter=counter)

    dataset_tree = _create_dataset_tree(mapper_family, realm)
    dataset_tree_version_list = TreeVersionList(initial_set={
        dataset_tree.value.dataset_version: VersionRecord(
            get_time_str(time_counter),
            None,
            Connector.from_object(dataset_tree)
        )
    })

    # Extract the UUID Set from the dataset tree:
    uuid_version_lists = {}
    datasets = dataset_tree.get_dataset_paths()
    for path, metadata_root_record in datasets:
        uuid_version_lists[metadata_root_record.dataset_identifier] = Connector.from_object(
            VersionList(initial_set={
                get_primary_data_version(version_counter): VersionRecord(
                    get_time_str(time_counter),
                    path,
                    Connector.from_object(metadata_root_record)
                )
            })
        )
        version_counter += 1
        time_counter += 1

    uuid_set = UUIDSet(
        mapper_family,
        realm,
        uuid_version_lists
    )

    print(uuid_set.save())
    print(dataset_tree_version_list.save())


if __name__ == "__main__":
    main(sys.argv)
