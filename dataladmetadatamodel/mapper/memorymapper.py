from collections import defaultdict

from .basemapper import BaseMapper as _BaseMapper
from .reference import Reference as _Reference


class MemoryMapper(_BaseMapper):
    instance = None

    def __init__(self):
        super().__init__("memory")
        self.objects = dict()
        self.index = 1000

    def __call__(self, *args, **kwargs):
        return self

    def map(self, reference: _Reference):
        index = int(reference.location)
        print(f"mapper: loading reference {reference}: {self.objects[index]}")
        return self.objects[index]

    def unmap(self, obj) -> _Reference:
        location = str(self.index)
        print(f"mapper: saving object {obj}: {location}")
        self.objects[self.index] = obj
        self.index += 1
        return _Reference("memory", "memory", type(obj).__name__, location)

    @classmethod
    def get_instance(cls):
        if MemoryMapper.instance is None:
            MemoryMapper.instance = MemoryMapper()
        return MemoryMapper.instance


MEMORY_MAPPER_FAMILY = defaultdict(MemoryMapper)


MEMORY_MAPPER_LOCATIONS = ("0", "1")
