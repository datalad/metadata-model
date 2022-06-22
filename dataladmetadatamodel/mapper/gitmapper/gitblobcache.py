import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import (
    Dict,
    List,
    Tuple,
    Union,
)

from .gitbackend.subprocess import git_save_file_list


def hash_blob(blob: Union[str, bytes]) -> str:
    if isinstance(blob, str):
        blob = bytearray(blob.encode())
    else:
        blob = bytearray(blob)

    object_to_hash = f"blob {len(blob)}".encode() + b"\x00" + blob
    return hashlib.sha1(object_to_hash).hexdigest()


class GitBlobCache:
    def __init__(self,
                 realm: str,
                 maxsize: int = 2000):

        self.realm = realm
        self.maxsize = maxsize
        self.cached_objects: List[Tuple[Union[str, bytes], str]] = list()
        self.flushed_objects: Dict[Union[str, bytes], str] = dict()
        self.temporary_directory = TemporaryDirectory()
        self.temp_dir_path = Path(self.temporary_directory.name)

        # Assert after member initialisation, so in case of an
        # exception the destructor does still work
        assert isinstance(realm, str)

    def __del__(self):
        if len(self.cached_objects) > 0:
            raise RuntimeError("deleting a non-flushed JSON object cache")
        self.temporary_directory.cleanup()

    def cache_blob(self,
                   realm: str,
                   blob: Union[str, bytes]):

        assert realm == self.realm, \
            "realm of cached object and realm of cache instance differ"

        if len(self.cached_objects) == self.maxsize:
            self.flush()
        expected_hash = hash_blob(blob)
        self.cached_objects.append((blob, expected_hash))
        return expected_hash

    def flush(self):
        """
        Write all cached objects to a git repository,
        associate the objects with their hash in
        self.cached_objects.

        Writing is done by creating files in a
        temporary directory and calling git hash-object
        with the list of files.

        :return: None
        """
        def check_hash(hash: str, expected_hash: str):
            assert hash == expected_hash

        file_list = []
        for index, (blob, expected_hash) in enumerate(self.cached_objects):
            temp_file_path = self.temp_dir_path / str(index)
            with temp_file_path.open("tw") as f:
                f.write(blob)
            file_list.append(str(temp_file_path))

        hash_values = git_save_file_list(self.realm, file_list)
        assert len(hash_values) == len(file_list), \
            f"hash value list length ({len(hash_values)}) and file list length " \
            f"({len(file_list)}) differ.\n{hash_values}\n{file_list}"

        hash_dict = {
            blob: hash_values[index]
            for index, (blob, expected_hash) in enumerate(self.cached_objects)
            if check_hash(hash_values[index], expected_hash)
        }
        self.flushed_objects.update(hash_dict)
        self.cached_objects = []
