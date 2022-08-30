import subprocess

from ..utils import split_git_lstree_line
from ..gitbackend.subprocess import (
    git_ls_tree,
    git_ls_tree_recursive,
)


def test_split_git_lstree_line(tmp_path):
    d = tmp_path / "dir 1"
    d.mkdir(parents=True)
    f = d / "file 1"
    f.write_text("some content")

    subprocess.run(["git", "init"], cwd=str(tmp_path))
    subprocess.run(["git", "add", "dir 1"], cwd=str(tmp_path))
    subprocess.run(["git", "commit", "-m", "some stuff"], cwd=str(tmp_path))

    l = git_ls_tree(str(tmp_path), "HEAD")[0]
    _, _, _, name = split_git_lstree_line(l)
    assert name == "dir 1"

    l = git_ls_tree_recursive(str(tmp_path), "HEAD")[0]
    _, _, _, name = split_git_lstree_line(l)
    assert name == "dir 1/file 1"
