"""
Simple lock interface.
"""
import os
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Dict,
    Tuple,
)

from fasteners import InterProcessLock

from dataladmetadatamodel.log import logger


PID = os.getpid()

GIT_MAPPER_LOCK_FILE_NAME = "datalad-metalad-write.lock"
read_write_locked = dict()


@dataclass
class LockState:
    counter: int
    lock: InterProcessLock


def _get_lock_state(lock_dict: dict, lock_dir: Path) -> LockState:
    if lock_dir not in lock_dict:
        lock_dict[lock_dir] = LockState(
            0,
            InterProcessLock(str(lock_dir / GIT_MAPPER_LOCK_FILE_NAME)))
    return lock_dict[lock_dir]


@contextmanager
def locked_backend(realm: Path):
    """ lock and unlock the backend given by realm """
    lock_backend(realm)
    try:
        yield None
    finally:
        unlock_backend(realm)


def lock_backend(realm: Path):
    lock_dir = get_lock_dir(realm)
    lock_state = _get_lock_state(read_write_locked, lock_dir)
    if lock_state.counter == 0:
        lock_time = time.time()
        lock_state.lock.acquire()
        lock_time = time.time() - lock_time
        logger.debug(
            "process {} locked git backend using file {} in {} seconds".format(
                PID,
                lock_dir,
                int(lock_time)))
    lock_state.counter += 1


def unlock_backend(realm: Path):
    lock_dir = get_lock_dir(realm, create_directory=False)
    assert lock_dir.exists()
    lock_state = _get_lock_state(read_write_locked, lock_dir)
    assert lock_state.counter > 0
    lock_state.counter -= 1
    if lock_state.counter == 0:
        logger.debug(
            "process {} unlocks git backend using file {}".format(PID, lock_dir))
        lock_state.lock.release()


def get_lock_dir(realm: Path, create_directory: bool = True) -> Path:
    lock_dir = realm / ".git"
    if not lock_dir.exists() and create_directory:
        # if exist_ok is False, we might get an error if
        # a concurrent mapper tries to lock the same
        # dataset.
        os.makedirs(lock_dir, exist_ok=True)
    return lock_dir


def create_file_tree(location: Path, content: Dict):
    for name, value_or_dict in content.items():
        new_location = location / name
        if isinstance(value_or_dict, str):
            new_location.write_text(value_or_dict)
        else:
            new_location.mkdir()
            create_file_tree(new_location, value_or_dict)


def create_git_repo(location: Path, content: Dict):
    subprocess.run(["git", "init", str(location)], check=True)
    create_file_tree(location, content)
    subprocess.run(
        ["git", "-C", str(location), "add", "."],
        check=True
    )

    subprocess.run(
        ["git", "-C", str(location), "commit", "-m", "create repo"],
        check=True
    )

    commit = subprocess.run(
        ["git", "-C", str(location), "cat-file", "-p", "HEAD"],
        check=True,
        stdout=subprocess.PIPE
    )
    return commit.stdout.decode().splitlines()[0].split()[1]


def split_git_lstree_line(line: str) -> Tuple[str, str, str, str]:
    fixed_fields, name = line.split("\t")
    flag, node_type, hash_value = fixed_fields.split(" ")
    return flag, node_type, hash_value, name
