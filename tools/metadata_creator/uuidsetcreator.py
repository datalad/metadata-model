import os
import sys
import time
from typing import Optional
from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.metadata import ExtractorConfiguration, Metadata
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.uuidset import UUIDSet
from dataladmetadatamodel.versionlist import VersionList

from tools.metadata_creator.filetreecreator import create_file_tree
from tools.metadata_creator.utils import get_dataset_id, get_dataset_version, read_datasets


def create_metadata_root_record(mapper_family,
                                realm,
                                path,
                                dataset_id: UUID,
                                dataset_version: str,
                                entry: os.DirEntry
                                ) -> Optional[MetadataRootRecord]:

    file_tree = create_file_tree(
        mapper_family,
        realm,
        entry.path,
        {"ft_parameter_1": "ft_value_1"}
    )

    metadata = Metadata(mapper_family, realm)
    metadata.add_extractor_run(
            time.time(),
            "dataset-test-extractor",
            "datasetcreator.py",
            "support@datalad.org",
            ExtractorConfiguration("1.2.3", {"ds_parameter_a": "ds_value_a"}),
            {
                "info": "fake metadata for dataset-test-extractor",
                "path": path
            }
        )

    mrr = MetadataRootRecord(
        mapper_family,
        realm,
        dataset_id,
        dataset_version,
        Connector.from_object(metadata),
        Connector.from_object(file_tree)
    )

    mrr.save()
    mrr.dataset_level_metadata.purge()
    mrr.file_tree.purge()
    return mrr

    print(f"dataset_level_metadata connector {mrr.dataset_level_metadata}", file=sys.stderr)
    print(f"file_tree connector {mrr.file_tree}", file=sys.stderr)
    print(f"writing MRR of {dataset_id} at path {entry.path},", file=sys.stderr)
    ref = mrr.save()
    print(f"done, reference: {ref},", file=sys.stderr)
    print(f"post save: dataset_level_metadata connector {mrr.dataset_level_metadata}", file=sys.stderr)
    print(f"post save: file_tree connector {mrr.file_tree}", file=sys.stderr)
    print("unloading dataset metadata and filetree,", file=sys.stderr)
    mrr.dataset_level_metadata.purge()
    mrr.file_tree.purge()
    print("done.", file=sys.stderr)

    dataset_tree.add_dataset(path, mrr)


def create_uuid_set(mapper_family: str,
                    realm: str,
                    path: str,
                    parameter: Optional[dict] = None
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
                path,
                dataset_id,
                version,
                dir_entry
            )
        )

        uuid_set.set_version_list(
            dataset_id,
            version_list
        )

    return uuid_set
