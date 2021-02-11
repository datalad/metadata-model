import enum

from .gitbackend.subprocess import git_ls_tree, git_update_ref, git_save_tree


class GitReference(enum.Enum):
    TREE_VERSION_LIST = "refs/datalad/dataset-tree-version-list"
    UUID_SET = "refs/datalad/dataset-uuid-set"
    DATASET_TREE = "refs/datalad/object-references/dataset-tree"
    METADATA = "refs/datalad/object-references/metadata"
    FILE_TREE = "refs/datalad/object-references/file-tree"


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
    tree_hash = git_save_tree(realm, existing_tree_entries)
    git_update_ref(realm, git_reference.value, tree_hash)


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
