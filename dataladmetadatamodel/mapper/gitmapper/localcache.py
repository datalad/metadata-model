"""
Different remote repositories have to be cached in different
local repositories to avoid conflicts in reference name space
"""
import hashlib
from pathlib import Path

import appdirs

from .gitbackend.subprocess import (
    git_fetch_object,
    git_fetch_reference,
    git_init,
    git_object_exists_locally,
)


cache_repository_base = (
    Path(appdirs.user_cache_dir("datalad-metalad"))
    / "local-git-cache"
)


def get_name_hash(name: str) -> str:
    return hashlib.sha256(name.encode()).hexdigest()


def get_repo_cache_path(remote_repo: str) -> Path:
    return cache_repository_base / get_name_hash(remote_repo)


def ensure_cache_exists(remote_repo: str):
    cache_path = get_repo_cache_path(remote_repo)
    if not cache_path.exists():
        git_init(str(cache_path))


def cache_object(remote_repo: str, object_id: str):

    ensure_cache_exists(remote_repo)
    cache_repo = str(get_repo_cache_path(remote_repo))

    if object_id.startswith("refs"):
        git_fetch_reference(
            cache_repo,
            remote_repo,
            object_id,
            object_id)
    elif not git_object_exists_locally(cache_repo, object_id):
        git_fetch_object(
            cache_repo,
            remote_repo,
            object_id)


def get_cache_realm(remote_repo: str) -> Path:
    return get_repo_cache_path(remote_repo)
