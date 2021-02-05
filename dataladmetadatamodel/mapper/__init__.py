
from .memorymapper import MEMORY_MAPPER_FAMILY
from .gitmapper import GIT_MAPPER_FAMILY_MEMBERS


GIT_MAPPER_FAMILY_NAME = "git"
MEMORY_MAPPER_FAMILY_NAME = "memory"


MAPPER_FAMILIES = {
    MEMORY_MAPPER_FAMILY_NAME: MEMORY_MAPPER_FAMILY,
    GIT_MAPPER_FAMILY_NAME: GIT_MAPPER_FAMILY_MEMBERS
}


def get_mapper(mapper_family: str, class_name: str):
    family_class_mappers = MAPPER_FAMILIES.get(mapper_family, None)
    if family_class_mappers is None:
        raise ValueError(f"Unknown mapper family: {mapper_family}")

    class_mapper = family_class_mappers.get(class_name, None)
    if class_mapper is None:
        raise ValueError(
            f"No mapper for class: '{class_name}' "
            f"in mapper family: '{mapper_family}'")
    return class_mapper
