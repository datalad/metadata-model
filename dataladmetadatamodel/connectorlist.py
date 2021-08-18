"""
A ConnectorList contains a list of connectors,
much like a list.

The connector list supports saving the bottom
half of all its connectors
"""
from typing import Optional

from dataladmetadatamodel.connector import ConnectedObject


class ConnectorList(list, ConnectedObject):
    def __init__(self):
        list.__init__(self)
        ConnectedObject.__init__(self)

    def save(self):
        self.un_touch()
        for index, connector in enumerate(self):
            connector.save_object()

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
