import os
from typing import Generator, Tuple

from dataladmetadatamodel import JSONObject
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import ExtractorConfiguration


DATALAD_DATASET_HIDDEN_DIR_NAME = ".datalad"


def is_dataset_dir(entry: os.DirEntry) -> bool:
    return any(
        filter(
            lambda x: x.is_dir(follow_symlinks=False) and x.name == DATALAD_DATASET_HIDDEN_DIR_NAME,
            os.scandir(entry.path)))


def should_follow(entry: os.DirEntry, ignore_dot_dirs) -> bool:
    return entry.is_dir(follow_symlinks=False) \
           and (not entry.name.startswith(".") or ignore_dot_dirs is False) \
           and not is_dataset_dir(entry)


def read_files(path: str, ignore_dot_dirs: bool = True) -> Generator[Tuple[str, os.DirEntry], None, None]:
    """ Return all sub-entries of path that are files """

    entries = list(os.scandir(path))
    while entries:
        entry = entries.pop()
        if should_follow(entry, ignore_dot_dirs):
            entries.extend(list(os.scandir(entry.path)))
        else:
            if not entry.is_dir() and not entry.name.startswith("."):
                yield entry.path[len(path) + 1:], entry


def get_extractor_run(path: str,
                      entry: os.DirEntry,
                      parameter_set_count: int) -> JSONObject:

    stat = entry.stat(follow_symlinks=False)
    return {
        "info": f"file-level test metadata for parameter set #{parameter_set_count}",
        "path": path,
        "size": stat.st_size,
        "atime": stat.st_atime,
        "ctime": stat.st_ctime,
        "mtime": stat.st_mtime
    }


def create_file_tree(mapper_family: str,
                     realm: str,
                     root_dir: str,
                     parameter_set_count: int
                     ) -> FileTree:

    file_tree = FileTree(mapper_family, realm)
    update_file_tree(
        mapper_family,
        realm,
        file_tree,
        root_dir,
        parameter_set_count
    )
    return file_tree


def update_file_tree(mapper_family: str,
                     realm: str,
                     file_tree: FileTree,
                     root_dir: str,
                     parameter_set_count: int):

    for path, entry in read_files(root_dir):
        for count in range(parameter_set_count):
            parameters = {
                "fs_parameter_0": f"value_0.{count}",
                "fs_parameter_1": f"value_1.{count}"
            }
            file_tree.add_extractor_run(
                mapper_family,
                realm,
                path,
                None,
                "file-core-extractor",
                "metadata_creator script",
                "support@datalad.org",
                ExtractorConfiguration(
                    "1.0.0",
                    parameters
                ),
                get_extractor_run(path, entry, count))
