import sys
import time
from typing import Dict, Optional, Tuple
from uuid import UUID

from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.uuidset import UUIDSet
from dataladmetadatamodel.versionlist import VersionList

from tools.metadata_creator.mrrcreator import create_metadata_root_record
from tools.metadata_creator.utils import get_dataset_id, get_dataset_version, read_datasets


def create_uuid_set(mapper_family: str,
                    realm: str,
                    path: str,
                    parameter_set_count: int
                    ) -> Optional[UUIDSet]:

    uuid_set = UUIDSet(mapper_family, realm)
    for path, dir_entry in read_datasets(path):

        dataset_id = get_dataset_id(dir_entry.path)
        if dataset_id is None:
            print(f"cannot determine id of dataset at {dir_entry.path}", file=sys.stderr)
            continue

        version = get_dataset_version(dir_entry.path)
        if version is None:
            print(f"cannot determine version of dataset at {dir_entry.path}", file=sys.stderr)
            continue

        version_list = VersionList(mapper_family, realm)
        version_list.set_versioned_element(
            version,
            str(time.time()),
            path,
            create_metadata_root_record(
                mapper_family,
                realm,
                dataset_id,
                version,
                dir_entry.path,
                path,
                parameter_set_count
            )
        )

        uuid_set.set_version_list(
            dataset_id,
            version_list
        )

    return uuid_set


def create_uuid_set_for_mrrs(mapper_family: str,
                             realm: str,
                             metadata_root_records: Dict[Tuple[UUID, str, str], MetadataRootRecord]
                             ) -> UUIDSet:

    uuid_set = UUIDSet(mapper_family, realm)

    version_list = VersionList(mapper_family, realm)
    for id_version_path, metadata_root_record in metadata_root_records.items():

        dataset_id, dataset_version, relative_path = id_version_path
        version_list.set_versioned_element(
            dataset_version,
            str(time.time()),
            relative_path,
            metadata_root_record
        )

        uuid_set.set_version_list(
            dataset_id,
            version_list
        )

    return uuid_set
