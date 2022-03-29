import os
import sys
from typing import Optional, Generator, Tuple
from uuid import UUID

from tools.metadata_creator.execute import checked_execute


DATALAD_DATASET_HIDDEN_DIR_NAME = ".datalad"


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
    except FileNotFoundError:
        print("WARNING: could not open config file: " + config_file_path, file=sys.stderr)
        return None


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


def get_dataset_version(path) -> Optional[str]:
    git_dir = path + "/.git"
    try:
        return checked_execute(
            ["git", f"--git-dir", git_dir, "log", "-1", "--pretty=format:%H"]
        )[0].strip()
    except RuntimeError:
        return None


def read_datasets(path: str, ignore_dot_dirs: bool = True) -> Generator[Tuple[str, os.DirEntry], None, None]:
    """ Return all datasets and paths """

    path = path.rstrip("/")

    if has_datalad_dir(path):
        path_entry = tuple(filter(lambda e: path.endswith(e.name), os.scandir(path + "/..")))[0]
        yield "", path_entry

    entries = list(os.scandir(path))
    while entries:
        entry = entries.pop()
        if is_dataset_dir(entry):
            yield entry.path[len(path) + 1:], entry
        if should_follow(entry, ignore_dot_dirs):
            entries.extend(list(os.scandir(entry.prefix_path)))