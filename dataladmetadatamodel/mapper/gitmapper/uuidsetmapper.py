from typing import Any
from uuid import UUID

from .execute import checked_execute
from .gittools import git_command_line, git_ls_tree, git_save_tree
from ..basemapper import BaseMapper
from ..reference import Reference


class UUIDSetGitMapper(BaseMapper):

    def map(self, ref: Reference) -> Any:
        from dataladmetadatamodel.connector import Connector
        from dataladmetadatamodel.uuidset import UUIDSet
        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"

        initial_set = {
            UUID(line.split()[3]): Connector.from_reference(
                Reference("git", "VersionList", line.split()[2])
            )
            for line in git_ls_tree(self.realm, ref.location)
        }
        return UUIDSet("git", self.realm, initial_set)

    def unmap(self, uuid_set: Any) -> str:
        """
        Store the data in the UUIDSet, including
        the top-half of the connectors.
        """
        # Import UUIDSet here to prevent recursive imports
        from dataladmetadatamodel.uuidset import UUIDSet
        assert isinstance(uuid_set, UUIDSet)

        top_half = [
            ("100644", "blob", version_list_connector.reference.location, str(uuid))
            for uuid, version_list_connector in uuid_set.uuid_set.items()
        ]
        if not top_half:
            raise ValueError("Cannot unmap an empty UUID")

        location = git_save_tree(self.realm, top_half)
        cmd_line = git_command_line(
            self.realm,
            "update-ref",
            ["refs/develop/dataset-set", location])
        checked_execute(cmd_line)
        return "refs/develop/dataset-set"
