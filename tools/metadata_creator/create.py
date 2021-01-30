import logging
from uuid import UUID
from typing import List, Tuple

from model.mapper.reference import Reference


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


def _create_file_tree(tree_spec: List[int], upper_levels: List[int]) -> List[str]:
    upper_level_postfix = (
        "." + ".".join(map(str, upper_levels))
        if upper_levels
        else ""
    )
    node_count = tree_spec[0]

    if len(tree_spec) == 1:
        return [
            f"file{upper_level_postfix}.{node_number}"
            for node_number in range(tree_spec[0])]

    result = []
    for node_index in range(node_count):
        for sub_tree in _create_file_tree(tree_spec[1:], upper_levels + [node_index]):
            name = f"d{upper_level_postfix}.{node_index}/{sub_tree}"
            result.append(name)
    return result



#print(sorted(_create_tree_paths([(4, 2), (3, 1), (2, 2)], 0)))

print(_create_file_tree([2, 3, 2], []))

