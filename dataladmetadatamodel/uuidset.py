from typing import (
    Dict,
    Iterable,
    Optional
)

from uuid import UUID

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.versionlist import VersionList
from dataladmetadatamodel.mapper.reference import Reference


class UUIDSet(MappableObject):
    def __init__(self,
                 initial_set: Optional[Dict[UUID, VersionList]] = None,
                 reference: Optional[Reference] = None):

        super().__init__()
        self.uuid_set = initial_set or dict()

    def get_modifiable_sub_objects(self) -> Iterable["ModifiableObject"]:
        raise NotImplementedError

    def purge_impl(self, force: bool):
        raise NotImplementedError

    def uuids(self):
        return self.uuid_set.keys()

    def set_version_list(self,
                         uuid: UUID,
                         version_list: VersionList):
        """
        Set a new or updated version list for the uuid.
        Existing references are deleted.
        The entry is marked as dirty.
        """
        self.touch()
        self.uuid_set[uuid] = version_list

    def get_version_list(self, uuid) -> VersionList:
        """
        Get the version list for uuid. If it is not mapped yet,
        it will be mapped.
        """
        return self.uuid_set[uuid].read_in()

    def unget_version_list(self, uuid):
        """
        Remove a version list from memory. First, persist the
        current status, if it was changed.
        """
        self.uuid_set[uuid].write_out()
        self.uuid_set[uuid].purge()

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "UUIDSet":

        raise NotImplementedError

        """ copy a UUID set optionally with a new mapper or a new realm """
        new_mapper_family = new_mapper_family or self.mapper_family
        new_realm = new_realm or self.realm
        copied_uuid_set = UUIDSet(new_mapper_family, new_realm)

        for uuid, version_list_connector in self.uuid_set.items():
            copied_uuid_set.uuid_set[uuid] = version_list_connector.deepcopy(
                new_mapper_family,
                new_realm)

        return copied_uuid_set
