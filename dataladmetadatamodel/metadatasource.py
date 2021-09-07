"""
A representation of metadata sources.

A MetadataSource objects makes the underlying
storage system visible. E.g. a MetadataSource
object for git-stored metadata, supports the
implementation to read, write, and copy
this data from, to, and between git
repositories. (This is in contrast to
the metadata model classes, that never
deals with a backend, e.g. a git-repository,
for their persistence, instead they are
mapped by mappers onto a specific backend.)
"""
import abc
import json
import logging
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import IO, Optional

from dataladmetadatamodel import (
    JSONObject,
    check_serialized_version,
    version_string
)


logger = logging.getLogger("datalad.metadata.model")


class MetadataSource(abc.ABC):
    """
    Base class for all metadata source handlers
    """

    TYPE_KEY = "metadata_source_type"

    @abc.abstractmethod
    def write_object_to(self, file_descriptor):
        raise NotImplementedError

    @abc.abstractmethod
    def copy_object_to(self, destination: Path):
        raise NotImplementedError

    @abc.abstractmethod
    def to_json_obj(self) -> JSONObject:
        raise NotImplementedError

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_obj())

    @staticmethod
    def from_json_obj(json_obj: JSONObject) -> Optional["MetadataSource"]:
        source_type = json_obj.get(MetadataSource.TYPE_KEY, None)
        if source_type is None:
            logger.error(
                f"key `{MetadataSource.TYPE_KEY}´ not found in "
                f"json object: {json.dumps(json_obj)}.")
            return None
        if source_type == LocalGitMetadataSource.TYPE:
            return LocalGitMetadataSource.from_json_obj(json_obj)
        elif source_type == ImmediateMetadataSource.TYPE:
            return ImmediateMetadataSource.from_json_obj(json_obj)
        else:
            logger.error(f"unknown metadata source type: `{source_type}´")
            return None

    @staticmethod
    def from_json_str(json_string: str) -> Optional["MetadataSource"]:
        return MetadataSource.from_json_obj(json.loads(json_string))


class LocalGitMetadataSource(MetadataSource):

    TYPE = "LocalGitMetadataSource"

    def __init__(self,
                 git_repository_path: Path,
                 object_reference: str
                 ):

        assert isinstance(object_reference, str)
        super().__init__()
        self.git_repository_path = git_repository_path
        self.object_reference = object_reference.strip()

    def __eq__(self, other):
        return (
            isinstance(other, LocalGitMetadataSource)
            and self.git_repository_path == other.git_repository_path
            and self.object_reference == other.object_reference)

    def write_object_to(self, file_descriptor: IO):
        command = f"git --git-dir {self.git_repository_path / '.git'} " \
                  f"cat-file blob {self.object_reference}"
        result = subprocess.run(command, stdout=file_descriptor, shell=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"subprocess returned {result.returncode}, "
                f"command: {command}")

    def copy_object_to(self, destination_repository: Path) -> str:
        """
        copy an object from the LocalGitMetadataSource
        instance into the git repository given by
        destination_repository.
        """
        command = f"git --git-dir {self.git_repository_path / '.git'} " \
                  f"cat-file blob {self.object_reference}|" \
                  f"git --git-dir {destination_repository / '.git'} " \
                  f"hash-object -w --stdin"
        copied_object_reference = subprocess.check_output(
            command,
            shell=True).decode().strip()
        assert copied_object_reference == self.object_reference
        return copied_object_reference

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="LocalGitMetadataSource",
                version=version_string
            ),
            MetadataSource.TYPE_KEY: LocalGitMetadataSource.TYPE,
            "git_repository_path": self.git_repository_path.as_posix(),
            "object_reference": self.object_reference}

    @staticmethod
    def from_json_obj(json_obj: JSONObject) -> Optional["LocalGitMetadataSource"]:
        try:
            assert json_obj["@"]["type"] == "LocalGitMetadataSource"
            check_serialized_version(json_obj)
            assert json_obj[MetadataSource.TYPE_KEY] == LocalGitMetadataSource.TYPE
            return LocalGitMetadataSource(
                Path(json_obj["git_repository_path"]),
                json_obj["object_reference"])
        except KeyError as key_error:
            logger.error(
                f"could not read LocalGitMetadataSource from {json_obj}, "
                f"reason: {key_error}")
            return None


class ImmediateMetadataSource(MetadataSource):

    TYPE = "ImmediateMetadataSource"

    def __init__(self, content: JSONObject):
        super().__init__()
        self.content = content

    def __eq__(self, other):
        return (
            isinstance(other, ImmediateMetadataSource)
            and self.content == other.content)

    def copy_object_to(self, destination: Path):
        pass

    def write_object_to(self, file_descriptor: IO):
        json.dump(self.content, file_descriptor)

    def deepcopy(self):
        return ImmediateMetadataSource(deepcopy(self.content))

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="ImmediateMetadataSource",
                version=version_string
            ),
            MetadataSource.TYPE_KEY: ImmediateMetadataSource.TYPE,
            "content": self.content}

    @staticmethod
    def from_json_obj(json_obj: JSONObject) -> Optional["ImmediateMetadataSource"]:
        try:
            assert json_obj["@"]["type"] == "ImmediateMetadataSource"
            check_serialized_version(json_obj)
            assert json_obj[MetadataSource.TYPE_KEY] == ImmediateMetadataSource.TYPE
            return ImmediateMetadataSource(json_obj["content"])
        except KeyError as key_error:
            logger.error(
                f"could not read ImmediateMetadataSource from {json_obj}, "
                f"reason: {key_error}")
            return None
