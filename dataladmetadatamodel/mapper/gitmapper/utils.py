import fcntl
import logging
import os
import time


PID = os.getpid()
GIT_MAPPER_LOCKFILE_NAME = ".datalad-git-backend.lock"

logger = logging.getLogger("datalad.metadata.model")

locked = 0
locked_file = None


def lock_backend(realm: str):
    global locked, locked_file

    if locked == 0:
        locked_file = open(realm + "/" + GIT_MAPPER_LOCKFILE_NAME, "w")
        lock_time = time.time()
        fcntl.lockf(locked_file, fcntl.LOCK_EX)
        lock_time_ms = int((time.time() - lock_time) * 1000)
        locked_file.write(str(PID) + "\n")
        locked_file.flush()
        logger.debug("process {} locked git backend {} in {} milli seconds".format(PID, realm, lock_time_ms))
    locked += 1


def unlock_backend(realm: str):
    global locked, locked_file

    assert locked > 0
    locked -= 1
    if locked == 0:
        logger.debug("process {} unlocks git backend {}".format(PID, realm))
        locked_file.truncate(0)
        fcntl.lockf(locked_file, fcntl.LOCK_UN)
        locked_file.close()
        locked_file = None
