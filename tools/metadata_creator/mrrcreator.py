import logging
import time
from typing import Dict, Optional, Tuple
from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.metadata import ExtractorConfiguration, Metadata
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

from tools.metadata_creator.datasettreecreator import read_datasets
from tools.metadata_creator.filetreecreator import create_file_tree
from tools.metadata_creator.utils import get_dataset_id, get_dataset_version


mdc_logger = logging.getLogger("metadata_creator")


def create_metadata_root_record(mapper_family,
                                realm,
                                dataset_id: UUID,
                                dataset_version: str,
                                dataset_path: str,
                                relative_path: str,
                                ) -> Optional[MetadataRootRecord]:

    file_tree = create_file_tree(
        mapper_family,
        realm,
        dataset_path,
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
                "path": relative_path
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


def get_dataset_id_version(path: str) -> Tuple[Optional[UUID], Optional[str]]:

    dataset_id = get_dataset_id(path)
    if dataset_id is None:
        mdc_logger.error(f"cannot determine id of dataset at {path}")

    dataset_version = get_dataset_version(path)
    if dataset_version is None:
        mdc_logger.error(f"cannot determine version of dataset at {path}")

    return dataset_id, dataset_version


def create_mrrs_from_dataset(mapper: str,
                             realm: str,
                             root_path: str
                             ) -> Dict[Tuple[UUID, str, str], MetadataRootRecord]:

    result = dict()
    for relative_path, entry in read_datasets(root_path):

        dataset_path = entry.path

        dataset_id, dataset_version = get_dataset_id_version(dataset_path)
        if dataset_id is None or dataset_version is None:
            mdc_logger.info(f"ignoring dataset at {dataset_version} because version or id could not be read")
            continue

        mrr = create_metadata_root_record(
            mapper,
            realm,
            dataset_id,
            dataset_version,
            dataset_path,
            relative_path)

        result[(dataset_id, dataset_version, relative_path)] = mrr

    return result
