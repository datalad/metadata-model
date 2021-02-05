import sys
import time
from typing import Optional

from dataladmetadatamodel.versionlist import TreeVersionList

from tools.metadata_creator.datasettreecreator import create_dataset_tree
from tools.metadata_creator.utils import get_dataset_version


def create_tree_version_list(mapper_family: str,
                             realm: str,
                             path: str,
                             ) -> Optional[TreeVersionList]:

    version = get_dataset_version(path)
    if version is None:
        print(f"cannot determine version of dataset at {path}", file=sys.stderr)
    tree_version_list = TreeVersionList(mapper_family, realm)
    tree_version_list.set_dataset_tree(
        version,
        str(time.time()),
        path,
        create_dataset_tree(
            mapper_family,
            realm,
            path
        )
    )
    return tree_version_list
