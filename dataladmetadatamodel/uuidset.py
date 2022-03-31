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
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(initial_set, (type(None), dict))
        assert isinstance(realm, (type(None), str))
        assert isinstance(reference, (type(None), Reference))

        super().__init__(realm, reference)
        self.uuid_set = initial_set or dict()

    def modifiable_sub_objects_impl(self) -> Iterable[MappableObject]:
        return self.uuid_set.values()

    def purge_impl(self):
        for version_list in self.uuid_set.values():
            version_list.purge()
        self.uuid_set = dict()

    def uuids(self):
        self.ensure_mapped()
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

    def get_version_list(self, uuid: UUID) -> VersionList:
        """
        Get the version list for uuid. If it is not mapped yet,
        it will be mapped.
        """
        self.ensure_mapped()
        return self.uuid_set[uuid].read_in()

    def unget_version_list(self, uuid):
        """
        Remove a version list from memory. First, persist the
        current status, if it was changed.
        """
        self.uuid_set[uuid].write_out()
        self.uuid_set[uuid].purge()

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "UUIDSet":

        copied_uuid_set = UUIDSet()
        for uuid, version_list in self.uuid_set.items():
            copied_uuid_set.uuid_set[uuid] = version_list.deepcopy(
                new_mapper_family,
                new_destination)

        copied_uuid_set.write_out(new_destination)
        copied_uuid_set.purge()
        return copied_uuid_set
