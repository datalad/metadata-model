"""
Multi object tree updater

The multi object tree updater allows to update a git-tee with a tree that is
defined by object-hashes and their paths. It uses only the minimal necessary
read/write operations to perform this task.

This is mainly used by the object reference system to efficiently store object
references, by using prefixes of the object-hashes as "directory names", i.e. as
tree reference names.
"""
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import (
    Dict,
    Iterable,
    List,
    Tuple,
    Union,
)

from .gitbackend.subprocess import git_read_tree_node
from .gitbackend.subprocess import git_save_tree_node
from .utils import split_git_lstree_line


logger = logging.getLogger("datalad.metalad.gitmapper.treeupdater")


class EntryType(Enum):
    Directory = 0
    File = 1


@dataclass
class DirEntry:
    type: EntryType
    object_hash: str
    name: str

    def __post_init__(self):
        _check_hash_and_type(self)

    def get_git_tree_entry_elements(self) -> Tuple[str, str, str, str]:
        if self.type == EntryType.Directory:
            flag = "040000"
            entry_type = "tree"
        else:
            flag = "100644"
            entry_type = "blob"
        return flag, entry_type, self.object_hash, self.name


@dataclass
class PathInfo:
    """
    Instances of this class represent object hashes and the prefix_path under which
    those hashes should be, or are, available.
    """
    elements: List[str]
    object_hash: str
    type: EntryType

    def __post_init__(self):
        _check_hash_and_type(self)

    def first(self) -> str:
        return self.elements[0]

    def is_file(self) -> bool:
        return self.is_leaf() and self.type == EntryType.File

    def is_leaf(self) -> bool:
        return len(self.elements) == 1

    def stripped_by(self, amount: int) -> "PathInfo":
        return PathInfo(
            self.elements[amount:],
            self.object_hash,
            self.type)


def _check_hash_and_type(obj: Union[DirEntry, PathInfo]):
    if len(obj.object_hash) != 40:
        raise ValueError(
            f"{type(obj).__name__}: hash format error ({obj.object_hash})")
    if obj.type not in (EntryType.Directory, EntryType.File):
        raise ValueError(
            f"{type(obj).__name__}: unknown type: {obj.type}")


def _check_leaf_or_directory(leaf_infos: List[PathInfo],
                             directory_infos: Dict[str, PathInfo]):
    """Ensure that a leaf is either a file name or a directory name

    While there might only be one file named u, there might be many directories
    named u, but only one type can exist in the new and existing directory info
    entries.
    """
    # Ensure that a name at this level (a path_info.first()) is either a file
    # name or a directory name.
    leaf_and_dir_names = [
        name
        for name in [file_info.first() for file_info in leaf_infos]
        if name in directory_infos.keys()]

    if leaf_and_dir_names:
        raise ValueError("names used for leafs and directories: " + ", ".join(
            leaf_and_dir_names))


def _check_leaf_uniqueness(leaf_infos: List[PathInfo]):
    """ Ensure that a file name is only used once"""
    duplicated_leaf_names = set([
        file_info.first()
        for file_info in leaf_infos
        if [
            file_info.first()
            for file_info in leaf_infos
        ].count(file_info.first()) > 1])

    if duplicated_leaf_names:
        raise ValueError("duplicated file names: " + ", ".join(
            duplicated_leaf_names))


def _check_entries_validity(leaf_infos: List[PathInfo],
                            directory_infos: Dict[str, PathInfo]):

    _check_leaf_or_directory(leaf_infos, directory_infos)
    _check_leaf_uniqueness(leaf_infos)


def _get_dir(repo: Path, object_hash: str) -> List:
    result = []
    for entry in git_read_tree_node(str(repo), object_hash):
        _, object_type, object_hash, name = split_git_lstree_line(entry)
        result.append(
            DirEntry(
                type=EntryType.File
                if object_type == "blob"
                else EntryType.Directory,
                object_hash=object_hash,
                name=name))
    return result


def _write_dir(repo: Path, entries: Iterable[DirEntry]) -> str:
    return git_save_tree_node(
        str(repo),
        [entry.get_git_tree_entry_elements() for entry in entries])


def add_paths(repo: Path,
              path_infos: List[PathInfo],
              root_entries: List[DirEntry]) -> str:
    """
    Add all prefix_path infos to the tree object defined by "root-entries". Load
    subtrees if necessary, write subtrees, when they are completely assembled.

    This method is called recursively, with path_infos shortened by one and
    corresponding root_entries.
    """

    # Build a quickly accessible entry structure
    root_entry_table = {
        root_entry.name: root_entry
        for root_entry in root_entries}

    # Collect all leaf entries, i.e. prefix_path info has only one element.
    leaf_infos = [path_info for path_info in path_infos if path_info.is_leaf()]

    # Collect all directory entries, i.e. for each directory name, get all
    # sub-paths that start with the directory name.
    directory_infos = {
        path_info.first(): [
            matching_path_info.stripped_by(1)
            for matching_path_info in path_infos
            if matching_path_info not in leaf_infos
            and matching_path_info.first() == path_info.first()
        ]
        for path_info in path_infos
        if path_info not in leaf_infos
    }

    _check_entries_validity(leaf_infos, directory_infos)

    resulting_entries = {**root_entry_table}

    # Process leaf entries
    for leaf_info in leaf_infos:

        name = leaf_info.first()

        existing_entry = root_entry_table.get(name, None)
        if existing_entry:
            if existing_entry.type != leaf_info.type:
                raise ValueError(
                    f"cannot convert {existing_entry.type.name} "
                    f"to {leaf_info.type.name}: {name}")
            logger.debug(f"modifying existing entry: {name}")

        resulting_entries[name] = DirEntry(
            type=leaf_info.type,
            object_hash=leaf_info.object_hash,
            name=name)

    # Process non-leaf entries
    for directory_name, sub_path_infos in directory_infos.items():
        if directory_name in root_entry_table:
            if root_entry_table[directory_name].type != EntryType.Directory:
                raise ValueError(
                    f"cannot convert file to directory: {directory_name}")
            directory_hash = root_entry_table[directory_name].object_hash
            sub_dir_entries = _get_dir(repo, directory_hash)
        else:
            sub_dir_entries = []

        written_directory_hash = add_paths(
            repo,
            sub_path_infos,
            sub_dir_entries)

        resulting_entries[directory_name] = DirEntry(
            type=EntryType.Directory,
            object_hash=written_directory_hash,
            name=directory_name)

    return _write_dir(repo, resulting_entries.values())
