"""
Simple linux kernel-based lock implementation. We use
file-locks here. This is not very flexible, but locks
are automatically released when a process exits. So no
stale locks are kept around, even if you kill a runaway-
process.
"""
import logging
import os
import time

from dataclasses import dataclass
from fasteners import InterProcessLock


logger = logging.getLogger("datalad.metadata.model")
PID = os.getpid()

GIT_MAPPER_LOCK_FILE_NAME = ".datalad-git-backend.lock"
read_write_locked = dict()
sleep_time = .1


@dataclass
class LockState:
    counter: int
    lock: InterProcessLock


def _get_lock_file(realm: str) -> float:

    lock_time = time.time()
    while True:
        try:
            lock_file = open(os.path.join(realm, GIT_MAPPER_LOCK_FILE_NAME, "wx"))
            break
        except FileExistsError:
            time.sleep(.1)
    lock_time = time.time() - lock_time

    lock_file.write(str(PID) + "\n")
    lock_file.flush()
    lock_file.close()
    return lock_time


def _remove_lock_file(realm: str):
    os.unlink(os.path.join(realm, GIT_MAPPER_LOCK_FILE_NAME))


def _get_lock_state(lock_dict: dict, realm: str) -> LockState:
    if realm not in lock_dict:
        lock_dict[realm] = LockState(
            0,
            InterProcessLock(os.path.join(realm, GIT_MAPPER_LOCK_FILE_NAME)))
    return lock_dict[realm]


def lock_backend(realm: str):
    lock_state = _get_lock_state(read_write_locked, realm)
    if lock_state.counter == 0:
        lock_time = time.time()
        lock_state.lock.acquire()
        lock_time = time.time() - lock_time
        logger.debug(
            "process {} locked git backend {} in {} seconds".format(
                PID,
                realm,
                int(lock_time)))
    lock_state.counter += 1


def unlock_backend(realm: str):
    lock_state = _get_lock_state(read_write_locked, realm)
    assert lock_state.counter > 0
    lock_state.counter -= 1
    if lock_state.counter == 0:
        logger.debug("process {} unlocks git backend {}".format(PID, realm))
        lock_state.lock.release()
