from pathlib import Path

import appdirs

from .gitbackend.subprocess import (
    git_fetch_reference,
    git_init,
    git_object_exists,
)


cache_repository_name = (
    Path(appdirs.user_cache_dir("datalad-metalad"))
    / "local-git-cache"
)

is_initialized = False


def ensure_cache_is_initialized():
    global is_initialized

    if is_initialized is False:
        git_init(str(cache_repository_name))
        is_initialized = True


def cache_object(remote_repo: str, object_id: str):
    ensure_cache_is_initialized()

    cache_repo = str(cache_repository_name)
    if not git_object_exists(cache_repo, object_id):
        git_fetch_reference(
            cache_repo,
            remote_repo,
            object_id,
            object_id)