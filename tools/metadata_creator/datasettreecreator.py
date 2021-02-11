import os
import sys
import time
from typing import Optional

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadata import ExtractorConfiguration, Metadata
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

from tools.metadata_creator.filetreecreator import create_file_tree
from tools.metadata_creator.utils import get_dataset_id, \
    get_dataset_version, has_datalad_dir, is_dataset_dir, read_datasets, \
    should_follow


def get_extractor_run(path: str, entry: os.DirEntry):
    stat = entry.stat(follow_symlinks=False)
    return {
        "path": path,
        "size": stat.st_size,
        "atime": stat.st_atime,
        "ctime": stat.st_ctime,
        "mtime": stat.st_mtime,
    }


def add_metadata_root_record(mapper_family,
                             realm,
                             dataset_tree: DatasetTree,
                             path,
                             entry: os.DirEntry):

    dataset_id = get_dataset_id(entry.path)
    if dataset_id is None:
        print(f"could not read id, ignoring dataset at path {entry.path},", file=sys.stderr)
        return

    dataset_version = get_dataset_version(entry.path)
    if dataset_id is None:
        print(f"could not read version, ignoring dataset at path {entry.path},", file=sys.stderr)
        return

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


def update_dataset_tree(mapper_family: str,
                        realm: str,
                        dataset_tree: DatasetTree,
                        root_dir: str,
                        parameter: Optional[dict] = None):

    for path, entry in read_datasets(root_dir):
        add_metadata_root_record(mapper_family, realm, dataset_tree, path, entry)


def create_dataset_tree(mapper_family: str,
                        realm: str,
                        root_dir: str,
                        parameter: Optional[dict] = None) -> DatasetTree:

    dataset_tree = DatasetTree(mapper_family, realm)
    update_dataset_tree(mapper_family, realm, dataset_tree, root_dir, parameter)
    return dataset_tree
