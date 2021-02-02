import abc
import binascii
import hashlib
import os
import time
import zlib
from collections import Counter
from functools import cmp_to_key
from itertools import chain
from typing import List, Optional, Union


def hash2hex(hash: bytes) -> str:
    return binascii.b2a_hex(hash).decode()


def hex2hash(hex_string: str) -> bytes:
    return binascii.a2b_hex(hex_string)


class TreeEntry(object):
    def __init__(self, flags: str, ref: Union[bytes, str], path: str):
        self.flags = flags
        self.ref = ref if isinstance(ref, bytes) else hex2hash(ref)
        self.path = path


class _GitObject(abc.ABC):
    def _get_header(self) -> bytes:
        return '{} {}'.format(self.get_node_type(), len(self.get_data())).encode() + b'\x00'

    def write(self, objects_dir: Optional[str] = ".") -> bytes:

        digest = self.get_hash()
        hex_digest = hash2hex(digest)
        dir_name = os.path.join(objects_dir, hex_digest[:2])
        file_name = os.path.join(dir_name, hex_digest[2:])

        os.makedirs(dir_name, exist_ok=True)
        try:
            with open(file_name, "xb") as stream:
                compressor = zlib.compressobj()
                stream.write(compressor.compress(self._get_header()))
                stream.write(compressor.compress(self.get_data()))
                stream.write(compressor.flush())
        except FileExistsError:
            pass

        return digest

    def get_hash(self) -> bytes:
        header = self._get_header()
        sha1_hasher = hashlib.sha1()
        sha1_hasher.update(header)
        sha1_hasher.update(self.get_data())
        return sha1_hasher.digest()

    def get_hash_hex(self) -> str:
        return hash2hex(self.get_hash())

    @abc.abstractmethod
    def get_node_type(self) -> str:
        pass

    @abc.abstractmethod
    def get_data(self) -> bytes:
        pass


class GitBlob(_GitObject):
    def __init__(self, data: Optional[Union[str, bytes, bytearray]] = None):
        if data:
            self.data = bytearray(data) if isinstance(data, (bytearray, bytes)) else bytearray(data.encode())
        else:
            self.data = bytearray()

    def get_data(self) -> bytes:
        return self.data

    def get_node_type(self):
        return 'blob'


class GitTree(_GitObject):
    Flags2Type = {
        "040000": "tree",
        "100644": "blob",
        "160000": "commit"
    }

    def __init__(self, entries: Optional[List[TreeEntry]] = None):
        self.entries = [] if entries is None else entries
        self._check_entries()

    def __str__(self):
        return (
            f"TREE {self.get_hash()}:\n"
            + "\n".join([
                f"{entry.flags} {self.Flags2Type[entry.flags]} "
                f"{hash2hex(entry.ref)}\t{entry.path}"
                for entry in self.entries])
            + "\n")

    def _check_entries(self):
        counter = Counter([entry.path for entry in self.entries])
        assert all(map(lambda count: count == 1, counter.values()))

    def get_node_type(self):
        return 'tree'

    def add_entry(self, entry: TreeEntry):
        self.add_entries([entry])

    def add_entries(self, entries: List[TreeEntry]):
        self.entries.extend(entries)
        self._check_entries()

    def get_data(self) -> bytes:
        def _git_tree_sort_compare(entry_a, entry_b):
            a, b = entry_a.path, entry_b.path
            if len(a) > len(b):
                if a.startswith(b) and a[len(b)] == "-":
                    return -1
            elif len(b) > len(a) and b[len(a)] == "-":
                if b.startswith(a):
                    return 1
            if a < b:
                return -1
            if a > b:
                return 1
            return 0

        return bytes(
            chain.from_iterable([
                '{} {}'.format(entry.flags.lstrip("0"), entry.path).encode()
                + b'\x00'
                + entry.ref
                for entry in sorted(self.entries, key=cmp_to_key(_git_tree_sort_compare))]))


class _GitCommit(_GitObject):
    """ Helper class to add _GitObject type annotations to GitObject """
    @abc.abstractmethod
    def get_node_type(self) -> str:
        pass

    @abc.abstractmethod
    def get_data(self) -> bytes:
        pass


class GitCommit(_GitCommit):
    def __init__(self,
                 message: str,
                 author: str,
                 committer: str,
                 tree: Union[GitTree, bytes],
                 parents: Optional[List[Union[_GitCommit, bytes]]] = None):

        self.message = message
        self.author = author
        self.committer = committer
        self.tree_hash = tree if isinstance(tree, bytes) else tree.get_hash()
        self.parent_hashes = [
            (commit if isinstance(commit, bytes) else commit.get_hash())
            for commit in parents or []]

    def get_node_type(self):
        return 'commit'

    def get_data(self) -> bytes:
        if self.parent_hashes:
            return (
               f"tree {hash2hex(self.tree_hash)}\n"
               + "\n".join([f"parent {hash2hex(parent)}" for parent in self.parent_hashes]) + "\n"
               + f"author {self.author} {int(time.time())} +0200\n"
               + f"committer {self.committer} {int(time.time())} +0200\n"
               + "\n"
               + self.message
            ).encode()
        else:
            return (
               f"tree {hash2hex(self.tree_hash)}\n"
               + f"author {self.author} {int(time.time())} +0200\n"
               + f"committer {self.committer} {int(time.time())} +0200\n"
               + "\n"
               + self.message
            ).encode()


class DataladMetadataCommit(_GitCommit):
    def __init__(self,
                 message: str,
                 author: str,
                 committer: str,
                 tree: Union[GitTree, bytes],
                 primary_data_commit: Union[GitCommit, bytes],
                 parents: Optional[List[Union[_GitCommit, bytes]]] = None):

        self.message = message
        self.author = author
        self.committer = committer
        self.tree_hash = tree if isinstance(tree, bytes) else tree.get_hash()
        self.primary_data_commit_hash = primary_data_commit\
            if isinstance(primary_data_commit, bytes)\
            else primary_data_commit.get_hash()
        self.parent_hashes = [
            (commit if isinstance(commit, bytes) else commit.get_hash())
            for commit in parents or []]

    def get_node_type(self):
        return 'commit'

    def get_data(self) -> bytes:
        if self.parent_hashes:
            return (
                    f"tree {hash2hex(self.tree_hash)}\n"
                    + "\n".join([f"parent {hash2hex(parent)}" for parent in self.parent_hashes]) + "\n"
                    + f"author {self.author} {int(time.time())} +0200\n"
                    + f"committer {self.committer} {int(time.time())} +0200\n"
                    + f"primary_data {hash2hex(self.primary_data_commit_hash)}\n"
                    + "\n"
                    + f"primary_data {hash2hex(self.primary_data_commit_hash)}\n"
                    + "\n"
                    + self.message
            ).encode()
        else:
            return (
                    f"tree {hash2hex(self.tree_hash)}\n"
                    + f"author {self.author} {int(time.time())} +0200\n"
                    + f"committer {self.committer} {int(time.time())} +0200\n"
                    + f"primary_data {hash2hex(self.primary_data_commit_hash)}\n"
                    + "\n"
                    + f"primary_data {hash2hex(self.primary_data_commit_hash)}\n"
                    + "\n"
                    + self.message
            ).encode()
