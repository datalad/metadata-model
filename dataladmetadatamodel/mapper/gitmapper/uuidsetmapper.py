from typing import Any
from uuid import UUID

from dataladmetadatamodel.versionlist import VersionList
from dataladmetadatamodel.mapper.gitmapper.objectreference import GitReference
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_ls_tree,
    git_save_tree,
    git_update_ref
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class UUIDSetGitMapper(Mapper):

    def map_in(self,
               uuid_set: "UUIDSet",
               reference: Reference) -> None:
        from dataladmetadatamodel.uuidset import UUIDSet

        assert isinstance(uuid_set, UUIDSet)
        assert isinstance(reference, Reference)

        initial_set = dict()
        for line in git_ls_tree(reference.realm, reference.location):
            line_elements = line.split()

            version_list = VersionList(
                reference=Reference(
                    "git", reference.realm, "VersionList", line_elements[2]))

            initial_set[UUID(line_elements[3])] = version_list

        return UUIDSet("git", self.realm, initial_set)

    def unmap_impl(self, uuid_set: Any) -> Reference:
        """
        Store the data in the UUIDSet, including
        the top-half of the connectors.
        """
        # Import here to prevent recursive imports
        from dataladmetadatamodel.uuidset import UUIDSet
        assert isinstance(uuid_set, UUIDSet)

        top_half = [
            (
                "100644",
                "blob",
                version_list_connector.reference.location,
                str(uuid)
            )
            for uuid, version_list_connector in uuid_set.uuid_set.items()
        ]
        if not top_half:
            raise ValueError("Cannot unmap an empty UUID")

        location = git_save_tree(self.realm, set(top_half))
        git_update_ref(self.realm, GitReference.UUID_SET.value, location)
        return Reference("git", self.realm, "UUIDSet", location)
