"""
A ConnectorList contains a list of connectors,
much like a list.

The connector list supports saving the bottom
half of all its connectors
"""


from .connector import ConnectedObject as _ConnectedObject


class ConnectorList(list, _ConnectedObject):
    def __init__(self):
        super(list, self).__init__()

    def save_bottom_half(self, family, realm):
        for index, connector in enumerate(self):
            print(f"ConnectorList.save_bottom_half: saving element #{index}: {connector}")  # TODO: remove me
            connector.unmap(family, realm)
