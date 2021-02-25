"""
A representation of metadata sources.

A MetadataSource objects makes the underlying
storage system visible. E.g. a MetadataSource
object for git-stored metadata, bring the
implementation to read, write, and copy
this data from, to, and between git
repositories. (This is in contrast to
the metadata model classes, that never
deal with a backend, e.g. a git-repository,
for their persistence, instead they are
mapped by mappers onto a specific backend.)
"""
import abc
import enum
import json
import subprocess
import tempfile
from typing import Any, List, Optional, Union

from . import JSONObject
from .text import Text


TempRepositoryObject = tempfile.TemporaryDirectory()
TempRepository = TempRepositoryObject.name
subprocess.run(["git", "init", TempRepository])


class GitRunner:
    def __init__(self,
                 remote_repository_url: Optional[str],
                 local_repository_path: Optional[str]
                 ):
        self.remote_repository_url = remote_repository_url
        self.local_repository_path = local_repository_path

    def _assemble_command_line(self,
                               command: str,
                               arguments: List[str]
                               ) -> List[str]:
        return [
            "git", "-P", "--git-dir",
            self.local_repository_path + "/.git",
            command] + arguments

    def _execute(self,
                 arguments: List[str],
                 stdin_content: Optional[Union[str, bytes]] = None,
                 stdout_descriptor: Optional[Any] = None
                 ) -> Any:

        return subprocess.run(
            arguments,
            **{
                **{
                    "input":
                        stdin_content.encode()
                        if isinstance(stdin_content, str)
                        else stdin_content
                    for _ in [None] if stdin_content is not None
                },
                **{
                    "stdout": stdout_descriptor
                    for _ in [None] if stdout_descriptor is not None
                }})

    def run(self,
            command: str,
            arguments: List[str],
            stdin_content: Optional[Union[str, bytes]] = None,
            stdout_descriptor: Optional[Any] = None
            ) -> Any:

        return self._execute(
            self._assemble_command_line(command, arguments),
            stdin_content,
            stdout_descriptor)

    def checked_run(self,
                    command: str,
                    arguments: List[str],
                    stdin_content: Optional[Union[str, bytes]] = None,
                    stdout_descriptor: Optional[Any] = None
                    ) -> Any:

        result = self.run(
            command,
            arguments,
            stdin_content,
            stdout_descriptor)

        if result.returncode != 0:
            raise RuntimeError(
                f"command failed (exit code: {result.returncode}) "
                f"{' '.join(arguments)}:\n"
                f"STDOUT:\n"
                f"{result.stdout.decode()}"
                f"STDERR:\n"
                f"{result.stderr.decode()}")


TempRepoGitRunner = GitRunner(None, TempRepository)


class MetadataSourceKey(str, enum.Enum):
    TYPE = "type"


class MetadataSource(abc.ABC):
    """
    Base class for all metadata source handlers
    """
    @abc.abstractmethod
    def write_object_to(self, file_descriptor):
        raise NotImplementedError

    @abc.abstractmethod
    def copy_object_to(self, destination: str):
        raise NotImplementedError

    @abc.abstractmethod
    def to_json_obj(self) -> JSONObject:
        raise NotImplementedError

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_obj())


class LocalGitMetadataSource(MetadataSource):
    def __init__(self,
                 git_repository_path: str,
                 object_reference: str
                 ):
        self.git_repository_path = git_repository_path
        self.object_reference = object_reference
        self.git_runner = GitRunner(None, self.git_repository_path)

    def write_object_to(self, file_descriptor):
        self.git_runner.checked_run(
            "cat-file",
            ["blob", self.object_reference],
            None,
            file_descriptor)

    def copy_object_to(self, destination: str):
        """
        copy an object from the LocalGitMetadataSource
        instance into a local repository.
        """
        destination_runner = GitRunner(None, destination)
        destination_runner.checked_run(
            "fetch",
            [self.git_repository_path, self.object_reference])

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="LocalGitMetadataSource",
                version="1.0"
            ),
            "git_repository_path": self.git_repository_path,
            "object_reference": self.object_reference
        }


class GitMetadataSource(MetadataSource):
    def __init__(self,
                 git_repository_url: str,
                 object_reference: str
                 ):

        self.git_repository_url = git_repository_url
        self.object_reference = object_reference

    def write_object_to(self, file_descriptor):
        # Fetch object into the temporary store
        raise NotImplementedError

        # Write the object from the local store
        local_git_metadata_source = LocalGitMetadataSource(
            TempRepository,
            self.object_reference)
        local_git_metadata_source.write_object_to(file_descriptor)

    def copy_object_to(self, destination: str):
        raise NotImplementedError
        # If the destination is remote, fetch object into the
        # temporary store and push it to the destination

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="GitMetadataSource",
                version="1.0"
            ),
            "git_repository_url": self.git_repository_url,
            "object_reference": self.object_reference
        }


class ImmediateMetadataSource(MetadataSource):
    def __init__(self,
                 content: Union[str, bytes]
                 ):
        self.git_repository_path = git_repository_path
        self.content = content

        self.text_object = Text("git", git_repository_path)
            self.git_repository_path = git_repository_path
        self.object_reference = object_reference
        self.git_runner = GitRunner(None, self.git_repository_path)

    def write_object_to(self, file_descriptor):
        self.git_runner.checked_run(
            "cat-file",
            ["blob", self.object_reference],
            None,
            file_descriptor)

    def copy_object_to(self, destination: str):
        """
        copy an object from the LocalGitMetadataSource
        instance into a local repository.
        """
        destination_runner = GitRunner(None, destination)
        destination_runner.checked_run(
            "fetch",
            [self.git_repository_path, self.object_reference])

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="LocalGitMetadataSource",
                version="1.0"
            ),
            "git_repository_path": self.git_repository_path,
            "object_reference": self.object_reference
        }


