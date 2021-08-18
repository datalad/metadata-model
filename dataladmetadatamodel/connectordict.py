"""
A ConnectorDict contains a set of connectors that
are mapped onto keys, much like a dictionary.

The connector dict supports saving the bottom
half of all its connectors
"""
from typing import Optional

from dataladmetadatamodel.connector import ConnectedObject


class ConnectorDict(dict, ConnectedObject):
    def __init__(self):
        dict.__init__(self)
        ConnectedObject.__init__(self)

    def save(self):
        self.un_touch()
        for key, connector in self.items():
            connector.save_object()

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "ConnectorDict":

        copied_connector_dict = ConnectorDict()
        for key, connector in self.items():
            copied_connector_dict[key] = connector.deepcopy(
                new_mapper_family,
                new_realm)

        return copied_connector_dict
