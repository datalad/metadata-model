from typing import Dict, Optional

from .connector import ConnectedObject, Connector
from .mapper import get_mapper
from .text import Text
from .mapper.reference import Reference


MetadataRootRecord = Text


class VersionRecord:
    def __init__(self,
                 time_stamp: str,
                 path: Optional[str],
                 mrr_connector: Connector):
        self.time_stamp = time_stamp
        self.path = path
        self.mrr_connector = mrr_connector


class VersionList(ConnectedObject):
    def __init__(self,
                 mapper_family: str,
                 realm: str,
                 initial_set: Optional[Dict[str, VersionRecord]] = None):
        self.mapper_family = mapper_family
        self.realm = realm
        self.version_set = initial_set or dict()

    def _get_version_record(self, primary_data_version) -> VersionRecord:
        return self.version_set[primary_data_version]

    def _get_mrr_connector(self, primary_data_version) -> Connector:
        return self._get_version_record(primary_data_version).mrr_connector

    def save(self, force_write: bool = False) -> Reference:
        """
        This method persists the bottom-half of all modified
        connectors by delegating it to the ConnectorDict. Then
        it saves the properties of the VersionList and the top-half
        of the connectors with the appropriate class mapper.
        """
        for primary_data_version, version_record in self.version_set.items():
            version_record.mrr_connector.save_object(self.mapper_family, self.realm, force_write)
        return Reference(
            self.mapper_family,
            "VersionList",
            get_mapper(self.mapper_family, "VersionList")(self.realm).unmap(self))

    def versions(self):
        return self.version_set.keys()

    def set_metadata_root_record(self,
                                 primary_data_version: str,
                                 time_stamp: str,
                                 path: str,
                                 metadata_root_record: MetadataRootRecord):
        """
        Set a new or updated metadata root record.
        Existing references are deleted.
        The entry is marked as dirty.
        """
        self.version_set[primary_data_version] = VersionRecord(
            time_stamp,
            path,
            Connector.from_object(metadata_root_record))

    def get_metadata_root_record(self, primary_data_version: str):
        """
        Get the metadata root record, its timestamp and path for the given version.
        If it is not mapped yet, it will be mapped.
        """
        version_record = self._get_version_record(primary_data_version)
        return (
            version_record.time_stamp,
            version_record.path,
            version_record.mrr_connector.load_object(
                self.mapper_family,
                self.realm))

    def unget_metadata_root_record(self,
                                   primary_data_version: str,
                                   force_write: bool = False):
        """
        Remove a metadata record from memory. First, persist the
        current status, if it was changed or if force_write
        is true.
        """
        mrr_connector = self._get_mrr_connector(primary_data_version)
        mrr_connector.save_object(self.mapper_family, self.realm, force_write)
        mrr_connector.purge()


class TreeVersionList(VersionList):
    """
    Thin wrapper around version list to support tree-version list
    specific mapping, for example in the git mapper, which will
    update a reference, if mapping an TreeVersionList instance.
    """
    def save(self, force_write: bool = False) -> Reference:
        # Save all metadata root records that are connected
        for primary_data_version, version_record in self.version_set.items():
            version_record.mrr_connector.save_object(self.mapper_family, self.realm, force_write)
        return Reference(
            self.mapper_family,
            "TreeVersionList",
            get_mapper(self.mapper_family, "TreeVersionList")(self.realm).unmap(self))
