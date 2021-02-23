"""
A ConnectorList contains a list of connectors,
much like a list.

The connector list supports saving the bottom
half of all its connectors
"""
from typing import Optional

from .connector import ConnectedObject as _ConnectedObject


class ConnectorList(list, _ConnectedObject):
    def __init__(self):
        super(list, self).__init__()

    def save_bottom_half(self, mapper_family, realm):
        for index, connector in enumerate(self):
            connector.unmap(mapper_family, realm)

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "ConnectorList":

        copied_connector_list = ConnectorList()
        for connector in self:
            copied_connector_list.append(
                connector.deepcopy(
                    new_mapper_family, new_realm))

        return copied_connector_list
