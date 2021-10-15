from uuid import UUID

from dataladmetadatamodel.mapper.gitmapper.objectreference import GitReference
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_ls_tree,
    git_save_tree,
    git_update_ref
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class UUIDSetGitMapper(Mapper):

    def map_in_impl(self,
                    uuid_set: "UUIDSet",
                    realm: str,
                    reference: Reference) -> None:

        from dataladmetadatamodel.uuidset import UUIDSet
        from dataladmetadatamodel.versionlist import VersionList

        assert isinstance(uuid_set, UUIDSet)
        assert isinstance(realm, str)
        assert isinstance(reference, Reference)

        uuid_set.uuid_set = dict()
        for line in git_ls_tree(realm, reference.location):
            line_elements = line.split()
            version_list = VersionList(
                realm=realm,
                reference=Reference("VersionList", line_elements[2]))

            uuid_set.uuid_set[UUID(line_elements[3])] = version_list

    def map_out_impl(self,
                     uuid_set: "UUIDSet",
                     realm: str,
                     force_write: bool) -> Reference:

        from dataladmetadatamodel.uuidset import UUIDSet
        assert isinstance(uuid_set, UUIDSet)

        tree_entries = [
            (
                "100644",
                "blob",
                version_list.write_out(realm).location,
                str(uuid)
            )
            for uuid, version_list in uuid_set.uuid_set.items()
        ]
        location = git_save_tree(realm, set(tree_entries))
        git_update_ref(realm, GitReference.UUID_SET.value, location)
        return Reference("UUIDSet", location)
