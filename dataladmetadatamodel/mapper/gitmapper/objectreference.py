import enum
import logging
from pathlib import Path
from typing import (
    Dict,
    List,
    Tuple,
)

from dataladmetadatamodel.mapper.reference import none_location


class GitReference(enum.Enum):
    TREE_VERSION_LIST = "refs/datalad/dataset-tree-version-list"
    UUID_SET = "refs/datalad/dataset-uuid-set"
    TREES = "refs/datalad/object-references/trees"
    BLOBS = "refs/datalad/object-references/blobs"


logger = logging.getLogger("datalad.metalad.gitmapper.objectreference")

cached_object_references: Dict[str, List[Tuple[str, str, str, str]]] = dict()


def add_object_reference(git_reference: GitReference,
                         flag: str,
                         object_type: str,
                         object_hash: str):

    if object_hash == none_location:
        logger.warning("attempt to add a None-reference")
        return

    if git_reference.value not in cached_object_references:
        cached_object_references[git_reference.value] = []

    cache_entry = (
        flag,
        object_type,
        object_hash,
        "object_reference:" + object_hash
    )

    if cache_entry not in cached_object_references[git_reference.value]:
        cached_object_references[git_reference.value].append(cache_entry)


def flush_object_references(realm: Path):
    global cached_object_references

    from dataladmetadatamodel.mapper.gitmapper.utils import (
        lock_backend,
        unlock_backend,
    )
    from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
        git_ls_tree,
        git_update_ref,
        git_save_tree,
    )

    lock_backend(realm)
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
    unlock_backend(realm)

    cached_object_references = dict()


def add_tree_reference(git_reference: GitReference, object_hash: str):
    add_object_reference(git_reference, "040000", "tree", object_hash)


def add_blob_reference(git_reference: GitReference, object_hash: str):
    add_object_reference(git_reference, "100644", "blob", object_hash)


def remove_object_reference(*args, **kwargs):
    raise NotImplementedError
