import fcntl
import os


PID = os.getpid()
GIT_MAPPER_LOCKFILE_NAME = ".datalad-git-backend.lock"


def lock_backend(realm: str):
    fd = open(realm + "/" + GIT_MAPPER_LOCKFILE_NAME, "w")
    fcntl.lockf(fd, fcntl.LOCK_EX)
    fd.write(str(PID) + "\n")
    fd.close()


def unlock_backend(realm: str):
    fd = open(realm + "/" + GIT_MAPPER_LOCKFILE_NAME, "r")
    fcntl.lockf(fd, fcntl.LOCK_UN)
    fd.close()
