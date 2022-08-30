import enum
import logging
from pathlib import Path
from typing import (
    Set,
    Tuple,
)

from ...mapper.reference import none_location
from .treeupdater import EntryType
from .utils import split_git_lstree_line


logger = logging.getLogger("datalad.metalad.gitmapper.objectreference")

cached_object_references: Set[Tuple[EntryType, str]] = set()


class GitReference(enum.Enum):
    TREE_VERSION_LIST = "refs/datalad/dataset-tree-version-list"
    UUID_SET = "refs/datalad/dataset-uuid-set"
    OBJECT_REFERENCES = "refs/datalad/object-references-2.0"
    LEGACY_TREES = "refs/datalad/object-references/trees"
    LEGACY_BLOBS = "refs/datalad/object-references/blobs"


checked_legacy_stores = set()


def add_object_reference(entry_type: EntryType,
                         object_hash: str):

    if object_hash == none_location:
        logger.warning("attempt to add a None-reference")
        return

    cached_object_references.add((entry_type, object_hash))


def add_legacy_store_entries_from(realm: Path,
                                  reference: GitReference,
                                  entry_type: EntryType):

    from .gitbackend.subprocess import git_ls_tree

    try:
        legacy_entries = (
            split_git_lstree_line(line)
            for line in git_ls_tree(str(realm), reference.value))

        logger.info(f"converting legacy reference store at {realm} (ref: "
                    f"{reference.value}) to new format")

        for entry in legacy_entries:
            cached_object_references.add((entry_type, entry[2]))
        return True
    except RuntimeError:
        return False


def add_legacy_store_entries(realm: Path) -> Tuple[bool, bool]:
    """
    Add legacy store entries to the cache, if they exist
    """
    if realm not in checked_legacy_stores:
        checked_legacy_stores.add(realm)

        legacy_trees_added = add_legacy_store_entries_from(
            realm,
            GitReference.LEGACY_TREES,
            EntryType.Directory)

        legacy_blobs_added = add_legacy_store_entries_from(
            realm,
            GitReference.LEGACY_BLOBS,
            EntryType.File)

        return legacy_trees_added, legacy_blobs_added

    return False, False


def remove_legacy_store_reference(realm: Path, reference: GitReference):
    from .gitbackend.subprocess import git_delete_ref

    logger.info(
        f"deleting legacy object reference store: {realm} "
        f"(ref: {reference.value})")
    git_delete_ref(str(realm), reference.value)


def flush_object_references(realm: Path):
    global cached_object_references

    from .gitbackend.subprocess import git_update_ref
    from ..gitmapper.treeupdater import (
        PathInfo,
        _get_dir,
        add_paths,
    )
    from ..gitmapper.utils import locked_backend

    legacy_trees_added, legacy_blobs_added = add_legacy_store_entries(realm)

    if cached_object_references:
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
                root_entries = _get_dir(realm, GitReference.OBJECT_REFERENCES.value)
            except RuntimeError:
                root_entries = []

            tree_hash = add_paths(realm, path_infos, root_entries)
            git_update_ref(str(realm), GitReference.OBJECT_REFERENCES.value, tree_hash)

        cached_object_references = set()

    if legacy_trees_added is True:
        remove_legacy_store_reference(realm, GitReference.LEGACY_TREES)
    if legacy_blobs_added is True:
        remove_legacy_store_reference(realm, GitReference.LEGACY_BLOBS)


def add_tree_reference(object_hash: str):
    add_object_reference(EntryType.Directory, object_hash)


def add_blob_reference(object_hash: str):
    add_object_reference(EntryType.File, object_hash)


def remove_object_reference(*args, **kwargs):
    raise NotImplementedError
