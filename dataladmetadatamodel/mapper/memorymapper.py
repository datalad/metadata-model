from collections import defaultdict
from typing import Any

from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class MemoryMapper(Mapper):
    instance = None

    def __init__(self):
        super().__init__("memory")
        self.objects = dict()
        self.index = 1000

    def __call__(self, *args, **kwargs):
        return self

    def map_impl(self, reference: Reference) -> Any:
        index = int(reference.location)
        print(f"mapper: loading reference {reference}: {self.objects[index]}")
        return self.objects[index]

    def unmap_impl(self, obj) -> Reference:
        location = str(self.index)
        print(f"mapper: saving object {obj}: {location}")
        self.objects[self.index] = obj
        self.index += 1
        return Reference("memory", "memory", type(obj).__name__, location)

    @classmethod
    def get_instance(cls):
        if MemoryMapper.instance is None:
            MemoryMapper.instance = MemoryMapper()
        return MemoryMapper.instance


MEMORY_MAPPER_FAMILY = defaultdict(MemoryMapper)


MEMORY_MAPPER_LOCATIONS = ("0", "1")
