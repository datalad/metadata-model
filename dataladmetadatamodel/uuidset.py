from typing import (
    Dict,
    Optional
)

from uuid import UUID

from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.mapper.reference import Reference
from dataladmetadatamodel.versionlist import VersionList
from dataladmetadatamodel.connector import (
    ConnectedObject,
    Connector
)
from dataladmetadatamodel.connectordict import ConnectorDict


class UUIDSet(ConnectedObject):
    def __init__(self,
                 mapper_family: str,
                 realm: str,
                 initial_set: Optional[Dict[UUID, Connector]] = None):

        super().__init__()
        self.mapper_family = mapper_family
        self.realm = realm
        self.uuid_set = ConnectorDict()

        if initial_set:
            self.uuid_set.update(initial_set)

    def save(self) -> Reference:
        """
        This method persists the bottom-half of all modified
        connectors by delegating it to the ConnectorDict. Then
        it saves the properties of the UUIDSet and the top-half
        of the connectors with the appropriate class mapper.
        """
        self.un_touch()

        self.uuid_set.save()

        return self.unmap_myself(self.mapper_family, self.realm)

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
        self.uuid_set[uuid] = Connector.from_object(version_list)

    def get_version_list(self, uuid) -> VersionList:
        """
        Get the version list for uuid. If it is not mapped yet,
        it will be mapped.
        """
        return self.uuid_set[uuid].load_object()

    def unget_version_list(self, uuid):
        """
        Remove a version list from memory. First, persist the
        current status, if it was changed.
        """
        self.uuid_set[uuid].save_object()
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
