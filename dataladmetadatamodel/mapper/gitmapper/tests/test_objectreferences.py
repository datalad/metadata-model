import subprocess
import tempfile
from hashlib import sha1
from pathlib import Path
from typing import (
    List,
    Iterable,
    Tuple,
)

from nose.tools import (
    assert_false,
    assert_in,
)

from ..utils import create_git_repo

from ..gitbackend.subprocess import (
    git_ls_tree,
    git_save_tree_node,
    git_update_ref,
)
from ..objectreference import (
    GitReference,
    flush_object_references,
)
from ..treeupdater import EntryType


def _does_ref_exist(realm: Path, reference: str) -> bool:
    result = subprocess.run(
        ["git", "--git-dir", str(realm / ".git"), "show-ref", reference])
    return result.returncode == 0


def _create_hash(n: int) -> str:
    return sha1(f"index: {n}".encode()).hexdigest()


def _create_legacy_tree(start_index: int,
                        stop_index: int,
                        entry_type: EntryType
                        ) -> Iterable[Tuple[str, str, str, str]]:

    flag, object_type = {
        EntryType.File: ("100644", "blob"),
        EntryType.Directory: ("040000", "tree")
    }[entry_type]

    return (
        (
            flag,
            object_type,
            _create_hash(i),
            "object_reference:" + _create_hash(i)
         )
        for i in range(start_index, stop_index)
    )


def _write_legacy_tree(realm: Path,
                       reference: str,
                       entry_type: EntryType,
                       start_index: int,
                       stop_index: int,
                       ):

    tree_hash = git_save_tree_node(
        str(realm),
        _create_legacy_tree(start_index, stop_index, entry_type))
    git_update_ref(str(realm), reference, tree_hash)


def _read_tree(realm: Path, reference: str) -> Iterable[Tuple[str, str]]:
    return (
        (line.split()[3], line.split()[2])
        for line in git_ls_tree(str(realm), reference))


def _read_reference_tree(realm: Path,
                         reference: str,
                         parts: List[str]
                         ) -> List[str]:
    """A simple recursive reference tree reader"""

    if len(parts) == 4:
        assert reference[9:] == parts[3]
        return ["".join(parts)]

    result = []
    for name, sub_reference in _read_tree(realm, reference):
        sub_results = _read_reference_tree(realm, sub_reference, parts + [name])
        result.extend(sub_results)
    return result


def test_old_reference_conversion():
    with tempfile.TemporaryDirectory() as td:
        realm = Path(td)
        create_git_repo(realm, {"readme.md": "test repo"})

        _write_legacy_tree(realm, GitReference.LEGACY_BLOBS.value, EntryType.File, 100, 200)
        _write_legacy_tree(realm, GitReference.LEGACY_TREES.value, EntryType.Directory, 200, 300)

        flush_object_references(realm)

        references = _read_reference_tree(
            realm,
            GitReference.OBJECT_REFERENCES.value,
            [])

        # Check that the new references exist.
        for i in range(100, 300):
            assert_in(_create_hash(i), references)

        # Check that the old references are gone by trying to update them
        assert_false(_does_ref_exist(realm, GitReference.LEGACY_BLOBS.value))
        assert_false(_does_ref_exist(realm, GitReference.LEGACY_TREES.value))


