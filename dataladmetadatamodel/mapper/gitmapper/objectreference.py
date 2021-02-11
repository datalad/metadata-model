
from . import GitReference
from .gitbackend.subprocess import git_ls_tree, git_save_tree


def add_object_reference(realm: str,
                         git_reference: GitReference,
                         flag: str,
                         object_type: str,
                         object_hash: str):
    try:
        existing_tree_entries = [
            tuple(line.split())
            for line in git_ls_tree(realm, git_reference.value)
        ]
    except RuntimeError:
        existing_tree_entries = []

    existing_tree_entries.append((
        flag,
        object_type,
        object_hash,
        "object_reference:" + object_hash
    ))
    git_save_tree(realm, existing_tree_entries)


def add_tree_reference(realm: str,
                       git_reference: GitReference,
                       object_hash: str):

    add_object_reference(
        realm,
        git_reference,
        "040000",
        "tree",
        object_hash
    )


def add_blob_reference(realm: str,
                       git_reference: GitReference,
                       object_hash: str):

    add_object_reference(
        realm,
        git_reference,
        "100644",
        "blob",
        object_hash
    )


def remove_object_reference(*args, **kwargs):
    raise NotImplementedError
