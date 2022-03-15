import enum
import logging
from pathlib import Path
from typing import (
    Set,
    Tuple,
)

from ...mapper.reference import none_location
from .treeupdater import EntryType


object_reference_name = "refs/datalad/object-references"

logger = logging.getLogger("datalad.metalad.gitmapper.objectreference")

cached_object_references: Set[Tuple[EntryType, str]] = set()


class GitReference(enum.Enum):
    TREE_VERSION_LIST = "refs/datalad/dataset-tree-version-list"
    UUID_SET = "refs/datalad/dataset-uuid-set"
    TREES = "refs/datalad/object-references/trees"
    BLOBS = "refs/datalad/object-references/blobs"


def add_object_reference(entry_type: EntryType,
                         object_hash: str):

    if object_hash == none_location:
        logger.warning("attempt to add a None-reference")
        return

    cached_object_references.add((entry_type, object_hash))


def flush_object_references(realm: Path):
    global cached_object_references

    from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import git_update_ref
    from dataladmetadatamodel.mapper.gitmapper.treeupdater import (
        PathInfo,
        _get_dir,
        add_paths,
    )
    from dataladmetadatamodel.mapper.gitmapper.utils import locked_backend

    path_infos = [
        PathInfo(
            [
                object_hash[0:3],
                object_hash[3:6],
                object_hash[6:9],
                object_hash[9:],
            ],
            object_hash,
            entry_type)
        for entry_type, object_hash in cached_object_references
    ]

    with locked_backend(realm):
        try:
            root_entries = _get_dir(realm, object_reference_name)
        except RuntimeError:
            root_entries = []
        tree_hash = add_paths(realm, path_infos, root_entries)
        git_update_ref(str(realm), object_reference_name, tree_hash)

    cached_object_references = set()


def legacy_flush_object_references(realm: Path):
    global cached_object_references

    from dataladmetadatamodel.mapper.gitmapper.utils import locked_backend
    from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
        git_ls_tree,
        git_update_ref,
        git_save_tree,
    )

    with locked_backend(realm):
        for git_reference, cached_tree_entries in cached_object_references.items():
            try:
                existing_tree_entries = [
                    tuple(line.split())
                    for line in git_ls_tree(str(realm), git_reference)
                ]
            except RuntimeError:
                existing_tree_entries = []

            existing_tree_entries_set = set(existing_tree_entries)
            existing_tree_entries_set |= set(cached_tree_entries)
            tree_hash = git_save_tree(str(realm), existing_tree_entries_set)
            git_update_ref(str(realm), git_reference, tree_hash)

    cached_object_references = dict()


def add_tree_reference(_, object_hash: str):
    add_object_reference(EntryType.Directory, object_hash)


def add_blob_reference(_, object_hash: str):
    add_object_reference(EntryType.File, object_hash)


def remove_object_reference(*args, **kwargs):
    raise NotImplementedError
