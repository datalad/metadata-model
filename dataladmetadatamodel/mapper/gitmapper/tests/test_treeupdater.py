import tempfile
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

from ..utils import create_git_repo
from ..gitbackend.subprocess import (
    git_ls_tree,
    git_ls_tree_recursive,
)
from ..treeupdater import (
    EntryType,
    PathInfo,
    _get_dir,
    _write_dir,
    add_paths
)


default_repo = {
    "a": {
        "af1": "1234"
    },
    "b": {
        "bf1": "aasdsd"
    },
    "LICENSE": "license content"
}


def test_basic():
    path_infos = [
        PathInfo(["a", "b", "c"], "000000000000000000000000000000000000000c", EntryType.File),
        PathInfo(["a", "b", "d"], "000000000000000000000000000000000000000d", EntryType.File),
        PathInfo(["tools", "ttttc"], "000000000000000000000000000000000000000c", EntryType.File),
        PathInfo(["a", "d"], "000000000000000000000000000000000000000d", EntryType.File),
        PathInfo(["b", "a"], "000000000000000000000000000000000000000a", EntryType.File),
        PathInfo(["c", "b"], "000000000000000000000000000000000000000b", EntryType.File),
        PathInfo(["d"], "000000000000000000000000000000000000000d", EntryType.File),
        PathInfo(["LICENSE"], "00000000000000000000000000000000000000a0", EntryType.File)
    ]

    with tempfile.TemporaryDirectory() as td:
        repo_path = Path(td)
        tree_hash = create_git_repo(repo_path, default_repo)
        root_entries = _get_dir(repo_path, tree_hash)
        result = add_paths(repo_path, path_infos, root_entries)

        lines = git_ls_tree_recursive(str(repo_path), result)
        for path_info in path_infos:
            assert f"100644 blob {path_info.object_hash}\t{'/'.join(path_info.elements)}" in lines


def test_dir_adding():
    path_infos = [
        PathInfo(
            ["a_dir"],
            "000000000000000000000000000000000000000c",
            EntryType.Directory
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        repo_path = Path(td)
        tree_hash = create_git_repo(repo_path, default_repo)
        root_entries = _get_dir(repo_path, tree_hash)
        result = add_paths(repo_path, path_infos, root_entries)

        lines = git_ls_tree(str(repo_path), result)
        for path_info in path_infos:
            assert f"040000 tree {path_info.object_hash}\t{'/'.join(path_info.elements)}" in lines


def test_dir_overwrite_error():
    path_infos = [
        PathInfo(
            ["a"],
            "000000000000000000000000000000000000000c",
            EntryType.File
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        repo_path = Path(td)
        tree_hash = create_git_repo(repo_path, default_repo)
        root_entries = _get_dir(repo_path, tree_hash)

        try:
            add_paths(repo_path, path_infos, root_entries)
            raise RuntimeError("did not get expected ValueError")
        except ValueError as ve:
            assert ve.args[0] == "cannot convert Directory to File: a"


def test_file_overwrite_error():
    path_infos = [
        PathInfo(
            ["LICENSE"],
            "000000000000000000000000000000000000000c",
            EntryType.Directory
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        repo_path = Path(td)
        tree_hash = create_git_repo(repo_path, default_repo)
        root_entries = _get_dir(repo_path, tree_hash)

        try:
            add_paths(repo_path, path_infos, root_entries)
            raise RuntimeError("did not get expected ValueError")
        except ValueError as ve:
            assert ve.args[0], "cannot convert File to Directory: LICENSE"


def test_minimal_invocation():

    complex_repo = {
        "a": {
            "a_a": {
                "a_a_f1": "content of a_a_f1"
            },
            "a_b": {
                "a_b_f1": "content of a_b_f1"
            }
        },
        "b": {
            "b_a": {
                "b_a_f1": "content of b_a_f1"
            },
            "b_b": {
                "b_b_f1": "content of b_b_f1"
            }
        },
        "c": {
            "c_f1": "content of c_f1"
        }
    }

    path_infos = [
        PathInfo(
            ["a", "a_a", "a_a_a", "a_a_a_f1"],
            "000000000000000000000000000000000000000c",
            EntryType.File
        ),
        PathInfo(
            ["a", "a_a", "a_a_a", "a_a_a_f2"],
            "000000000000000000000000000000000000000c",
            EntryType.File
        ),
        PathInfo(
            ["a", "a_a", "a_a_f1"],
            "000000000000000000000000000000000000000c",
            EntryType.File
        ),
        PathInfo(
            ["a", "a_b", "a_b_f2"],
            "000000000000000000000000000000000000000c",
            EntryType.File
        ),
    ]

    with \
            tempfile.TemporaryDirectory() as td, \
            patch("dataladmetadatamodel.mapper.gitmapper.treeupdater._get_dir") as gd_mock, \
            patch("dataladmetadatamodel.mapper.gitmapper.treeupdater._write_dir") as wd_mock:

        def gd_counter(*args):
            get_calls[args[1]] += 1
            return _get_dir(*args)

        def wd_counter(*args):
            write_calls[args] += 1
            return _write_dir(*args)

        get_calls = defaultdict(int)
        write_calls = defaultdict(int)
        gd_mock.side_effect = gd_counter
        wd_mock.side_effect = wd_counter

        repo_path = Path(td)
        tree_hash = create_git_repo(repo_path, complex_repo)
        root_entries = _get_dir(repo_path, tree_hash)

        result = add_paths(repo_path, path_infos, root_entries)

        # Assert that a node is only read once
        assert all(map(lambda x: x == 1, get_calls.values()))
        assert len(get_calls) == 3
        # Assert that a node is only written once
        assert all(map(lambda x: x == 1, write_calls.values()))
        assert len(write_calls) == 5

        lines = git_ls_tree_recursive(str(repo_path), result)
        for path_info in path_infos:
            assert f"100644 blob {path_info.object_hash}\t{'/'.join(path_info.elements)}" in lines
