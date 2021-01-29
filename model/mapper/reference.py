import json
from typing import Optional


class Reference:
    def __init__(self,
                 mapper_family: str,
                 class_name: str,
                 location: Optional[str] = None):
        self.mapper_family = mapper_family
        self.class_name = class_name
        self.location = location

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"Reference(mapper_family='{self.mapper_family}', "
            f"class_name='{self.class_name}', "
            f"location={repr(self.location)})")

    def to_json(self):  # TODO: rename to to_json_str
        return json.dumps({
            "@": dict(
                type="Reference",
                version="1.0",
            ),
            **dict(
                mapper_family=self.mapper_family,
                class_name=self.class_name,
                location=self.location)})

    @classmethod
    def from_json(cls, json_str: str) -> "Reference":   # TODO: rename to from_json_str
        obj = json.loads(json_str)
        assert obj["@"]["type"] == "Reference"
        assert obj["@"]["version"] == "1.0"
        return cls(
            obj["mapper_family"],
            obj["class_name"],
            obj["location"])
