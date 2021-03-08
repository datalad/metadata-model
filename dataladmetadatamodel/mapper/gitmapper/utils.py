"""
Simple linux kernel-based lock implementation. We use
file-locks here. This is not very flexible, but locks
are automatically released when a process exits. So no
stale locks are kept around, even if you kill a runaway-
process.
"""
import fcntl
import logging
import os
import time
from typing import IO, Optional, Tuple

from dataclasses import dataclass


PID = os.getpid()
GIT_MAPPER_LOCK_FILE_NAME = ".datalad-git-backend.lock"

logger = logging.getLogger("datalad.metadata.model")

read_write_locked = dict()


@dataclass
class LockState:
    counter: int
    file_object: Optional[IO]


def _get_locked_file(realm: str, mode: int) -> Tuple[IO, float]:
    lock_file = open(realm + "/" + GIT_MAPPER_LOCK_FILE_NAME, "w")
    lock_time = time.time()
    fcntl.lockf(lock_file, mode)
    lock_time = time.time() - lock_time
    lock_file.write(str(PID) + "\n")
    lock_file.flush()
    return lock_file, lock_time


def _unlock_file(lock_file: IO):
    lock_file.truncate(0)
    fcntl.lockf(lock_file, fcntl.LOCK_UN)
    lock_file.close()


def _get_lock_state(lock_dict: dict, realm: str) -> LockState:
    if realm not in lock_dict:
        lock_dict[realm] = LockState(0, None)
    return lock_dict[realm]


def lock_backend(realm: str):
    lock_state = _get_lock_state(read_write_locked, realm)
    if lock_state.counter == 0:
        lock_state.file_object, lock_time = _get_locked_file(realm, fcntl.LOCK_EX)
        logger.debug("process {} read-write-locked git backend {} in {} seconds".format(PID, realm, lock_time))
    lock_state.counter += 1


def unlock_backend(realm: str):
    lock_state = _get_lock_state(read_write_locked, realm)
    assert lock_state.counter > 0
    lock_state.counter -= 1
    if lock_state.counter == 0:
        logger.debug("process {} read-write-unlocks git backend {}".format(PID, realm))
        _unlock_file(lock_state.file_object)
        lock_state.file_object = None
