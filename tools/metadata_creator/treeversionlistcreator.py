import sys
import time
from typing import Dict, Optional, Tuple
from uuid import UUID

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.versionlist import TreeVersionList

from tools.metadata_creator.datasettreecreator import create_dataset_tree
from tools.metadata_creator.utils import get_dataset_version


def create_tree_version_list(mapper_family: str,
                             realm: str,
                             path: str,
                             parameter: Optional[dict] = None
                             ) -> Optional[TreeVersionList]:

    version = get_dataset_version(path)
    if version is None:
        print(f"cannot determine version of dataset at {path}", file=sys.stderr)
    tree_version_list = TreeVersionList(mapper_family, realm)
    tree_version_list.set_dataset_tree(
        version,
        str(time.time()),
        create_dataset_tree(
            mapper_family,
            realm,
            path,
            parameter
        )
    )
    return tree_version_list


def create_tree_version_list_for_mrrs(
        mapper_family: str,
        realm: str,
        metadata_root_records: Dict[Tuple[UUID, str, str], MetadataRootRecord]
        ) -> TreeVersionList:

    dataset_tree = DatasetTree(mapper_family, realm)

    for id_version_path, metadata_root_record in metadata_root_records.items():
        dataset_id, dataset_version, relative_path = id_version_path
        dataset_tree.add_dataset(relative_path, metadata_root_record)

    top_level_version = tuple(
        filter(
            lambda ivp_mrr: ivp_mrr[0][2] == "",
            metadata_root_records.items()))[0][0][1]

    tree_version_list = TreeVersionList(mapper_family, realm)
    tree_version_list.set_dataset_tree(
        top_level_version,
        str(time.time()),
        dataset_tree
    )

    return tree_version_list
