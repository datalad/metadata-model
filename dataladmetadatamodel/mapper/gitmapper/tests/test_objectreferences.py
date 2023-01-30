import subprocess
import tempfile
from hashlib import sha1
from pathlib import Path
from typing import (
    List,
    Iterable,
    Tuple,
)
from unittest.mock import patch

from ..gitbackend.subprocess import (
    git_ls_tree,
    git_save_tree_node,
    git_update_ref,
)
from ...reference import none_location
from ..objectreference import (
    GitReference,
    add_blob_reference,
    add_object_reference,
    add_tree_reference,
    flush_object_references,
)
from ..treeupdater import EntryType
from ..utils import (
    create_git_repo,
    split_git_lstree_line,
)


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
        (element[3], element[2])
        for element in (
            split_git_lstree_line(line)
            for line in git_ls_tree(str(realm), reference)))


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
            assert _create_hash(i) in references

        # Check that the old references are gone by trying to update them
        assert _does_ref_exist(realm, GitReference.LEGACY_BLOBS.value) is False
        assert _does_ref_exist(realm, GitReference.LEGACY_TREES.value) is False


def test_none_reference_warning():
    with patch("dataladmetadatamodel.mapper.gitmapper.objectreference.logger") as logger_mock:
        add_object_reference(EntryType.Directory, none_location)
        add_blob_reference(none_location)
        add_tree_reference(none_location)
    assert logger_mock.warning.call_count == 3
