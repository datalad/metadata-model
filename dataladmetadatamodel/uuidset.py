from typing import Dict, Optional
from uuid import UUID

from .mapper import get_mapper
from .mapper.reference import Reference
from .versionlist import VersionList
from .connector import ConnectedObject, Connector
from .connectordict import ConnectorDict


class UUIDSet(ConnectedObject):
    def __init__(self,
                 mapper_family: str,
                 realm: str,
                 initial_set: Optional[Dict[UUID, Connector]] = None):
        self.mapper_family = mapper_family
        self.realm = realm
        self.uuid_set = ConnectorDict()
        if initial_set:
            self.uuid_set.update(initial_set)

    def save(self, force_write: bool = False) -> Reference:
        """
        This method persists the bottom-half of all modified
        connectors by delegating it to the ConnectorDict. Then
        it saves the properties of the UUIDSet and the top-half
        of the connectors with the appropriate class mapper.
        """
        self.uuid_set.save_bottom_half(self.mapper_family, self.realm, force_write)
        return Reference(
            self.mapper_family,
            self.realm,
            "UUIDSet",
            get_mapper(self.mapper_family, "UUIDSet")(self.realm).unmap(self))

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
        self.uuid_set[uuid] = Connector.from_object(version_list)

    def get_version_list(self, uuid) -> VersionList:
        """
        Get the version list for uuid. If it is not mapped yet,
        it will be mapped.
        """
        return self.uuid_set[uuid].load_object()

    def unget_version_list(self, uuid, force_write: bool = False):
        """
        Remove a version list from memory. First, persist the
        current status, if it was changed or force_write
        is true.
        """
        self.uuid_set[uuid].unmap(self.mapper_family, self.realm, force_write)
        self.uuid_set[uuid].purge()

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "UUIDSet":

        """ copy a UUID set optionally with a new mapper or a new realm """
        new_mapper_family = new_mapper_family or self.mapper_family
        new_realm = new_realm or self.realm
        copied_uuid_set = UUIDSet(new_mapper_family, new_realm)

        for uuid, version_list_connector in self.uuid_set.items():
            copied_uuid_set.uuid_set[uuid] = version_list_connector.deepcopy(
                new_mapper_family,
                new_realm)

        return copied_uuid_set
