"""
Instances of the Text class just contain
text. Their main use is as dummy-element
during model development.
"""
from dataclasses import dataclass

from model.connector import ConnectedObject


@dataclass
class Text(ConnectedObject):
    content: str
