import logging
from time import time
from typing import Dict, List, Tuple, Union

from model.metadata import ExtractorConfiguration, Metadata, MetadataInstance


JSONObject = Union[List["JSONObject"], Dict[str, "JSONObject"], int, float, str]


MDC_LOGGER = logging.getLogger("metadata_creator")

tree_pattern = [3, -3, 4, -3]
dataset_versions = 3
dataset_metadata_formats = ["core-metadata", "annex-metadata", "random-metadata"]


def _create_tree_paths(tree_spec: List[Tuple[int, int]], level: int) -> List[str]:
    if len(tree_spec) == 1:
        return [
            f"dataset.{node_number}"
            for node_number in range(tree_spec[0][0])
        ]
    return [
        f"dataset.{node_number}/" + sub_spec
        if node_number < tree_spec[0][1]
        else f"sub_dir.{node_number}/" + sub_spec
        for sub_spec in _create_tree_paths(tree_spec[1:], level + 1)
        for node_number in range(tree_spec[0][0])
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


def _create_metadata(
        mapper_family: str,
        realm: str,
        formats: List[str],
        parameter_lists: List[JSONObject]) -> Metadata:

    metadata = Metadata(mapper_family, realm)
    for format in formats:
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
                f'"metadata content for format {format}, '
                f'parameter: {extractor_configuration}"}}'
            )

    return metadata


metadata = _create_metadata(
    "git",
    "/tmp",
    ["core-extrator", "format_x"],
    [
        {
            "param_1": "1.1",
            "param_2": "2.1",
            "param_3": "3.1",
            "param_4": "4.1",
        },
        {
            "param_1": "1.2",
            "param_2": "2.2",
            "param_3": "3.2",
            "param_4": "4.2",
        },
        {
            "param_1": "1.3",
            "param_2": "2.3",
            "param_3": "3.3",
            "param_4": "4.3",
        }
    ]
)

print(metadata)
