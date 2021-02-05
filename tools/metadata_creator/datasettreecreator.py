import os
import sys
import time
from typing import Generator, Optional, Tuple
from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadata import ExtractorConfiguration, Metadata
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

from tools.metadata_creator.filetreecreator import create_file_tree


DATALAD_DATASET_HIDDEN_DIR_NAME = ".datalad"


def has_datalad_dir(path: str) -> bool:
    return any(
        filter(
            lambda e: e.is_dir(follow_symlinks=False) and e.name == DATALAD_DATASET_HIDDEN_DIR_NAME,
            os.scandir(path)))


def is_dataset_dir(entry: os.DirEntry) -> bool:
    return entry.is_dir(follow_symlinks=False) and has_datalad_dir(entry.path)


def should_follow(entry: os.DirEntry, ignore_dot_dirs) -> bool:
    return (
        entry.is_dir(follow_symlinks=False)
        and not entry.name.startswith(".") or ignore_dot_dirs is False)


def read_datasets(path: str, ignore_dot_dirs: bool = True) -> Generator[Tuple[str, os.DirEntry], None, None]:
    """ Return all datasets und path """

    if has_datalad_dir(path):
        path_entry = tuple(filter(lambda e: path.endswith(e.name), os.scandir(path + "/..")))[0]
        yield ".", path_entry

    entries = list(os.scandir(path))
    while entries:
        entry = entries.pop()
        if is_dataset_dir(entry):
            yield entry.path[len(path) + 1:], entry
        if should_follow(entry, ignore_dot_dirs):
            entries.extend(list(os.scandir(entry.path)))


def get_extractor_run(path: str, entry: os.DirEntry):
    stat = entry.stat(follow_symlinks=False)
    return {
        "path": path,
        "size": stat.st_size,
        "atime": stat.st_atime,
        "ctime": stat.st_ctime,
        "mtime": stat.st_mtime,
    }


def get_dataset_id(path) -> Optional[UUID]:
    config_file_path = path + "/.datalad/config"
    try:
        with open(config_file_path) as f:
            for line in f.readlines():
                elements = line.split()
                if elements[:2] == ["id", "="]:
                    return UUID(elements[2])
        print("WARNING: no dataset id in config file: " + config_file_path, file=sys.stderr)
        return None
    except:
        print("WARNING: could not open config file: " + config_file_path, file=sys.stderr)
        return None


def add_metadata_root_record(mapper_family,
                             realm,
                             dataset_tree: DatasetTree,
                             path,
                             entry: os.DirEntry):

    dataset_id = get_dataset_id(entry.path)
    if dataset_id is None:
        print(f"ignoring dataset at path {entry.path},", file=sys.stderr)
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
            {"info": "fake metadata for dataset-test-extractor", "path": path}
        )

    mrr = MetadataRootRecord(
        mapper_family,
        realm,
        dataset_id,
        "1234567891123456789212345678931234567894",
         Connector.from_object(metadata),
         Connector.from_object(file_tree)
    )

    print(f"writing MRR of {dataset_id} at path {entry.path},", file=sys.stderr)
    ref = mrr.save()
    print(f"done, reference: {ref},", file=sys.stderr)
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
