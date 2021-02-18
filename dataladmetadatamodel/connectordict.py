"""
A ConnectorDict contains a set of connectors that
are mapped onto keys, much like a dictionary.

The connector dict supports saving the bottom
half of all its connectors
"""
from typing import Optional

from .connector import ConnectedObject as _ConnectedObject


class ConnectorDict(dict, _ConnectedObject):
    def __init__(self):
        super(dict, self).__init__()

    def save_bottom_half(self, family, realm, force_write: bool = False):
        for key, connector in self.items():
            connector.save_object(family, realm, force_write)

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
