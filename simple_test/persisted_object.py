import logging
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Union
)


from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_load_str,
    git_save_json,
    git_save_str
)


logging.basicConfig(level=logging.DEBUG)
repo_dir: str = "/home/cristian/tmp/mapptest"


SReference = str
SJSON = Union[str, int, float, Dict, List]


class Mapper:
    def read_in(self, mappable_object: "MappableObject", SReference):
        raise NotImplementedError

    def write_out(self, mappable_object: "MappableObject") -> SReference:
        raise NotImplementedError


mapper: Dict[str, Mapper] = dict()


class ModifiableObject:
    """
    Object that tracks modification status.

    Responsibilities:
     - allow touching and cleaning
     - determine modification state based
       on subclass-implementation of is_modified_impl()
    """
    def __init__(self):
        # A modifiable object is assumed
        # to be unmodified upon creation
        self.dirty = False

    def touch(self):
        self.dirty = True

    def clean(self):
        self.dirty = False

    def is_modified(self) -> bool:
        """
        Determine whether the object or one of its contained
        objects was modified.
        """
        if not self.dirty:
            self.dirty = self._sub_elements_modified()
        return self.dirty

    def _sub_elements_modified(self):
        return any(map(lambda element: element.is_modified(), self.get_modifiable_mapped_sub_elements()))

    def xxxsub_elements_modified(self) -> bool:
        """
        By default modification state is determined by
        the dirty flag in this object, i.e. whether
        self.clean() or self.touch() has been invoked
        latest.

        :return: True if any sub-element exists that is
                 modified, else False
        """
        return False

    def get_modifiable_mapped_sub_elements(self) -> Iterable:
        return []


class MappableObject(ModifiableObject):
    """
    Base class for objects that can
    be mapped onto a storage backend
    """
    def __init__(self, reference: Optional[SReference]):
        super().__init__()
        self.reference = reference
        if reference is None:
            self.mapped = True
        else:
            self.mapped = False

    def read_in(self):
        if self.mapped:
            return
        assert self.reference is not None
        mapper[type(self).__name__].read_in(self, self.reference)
        self.mapped = True
        self.clean()

    def write_out(self) -> SReference:
        if self.mapped:
            self.reference = mapper[type(self).__name__].write_out(self)
            self.clean()
        assert self.reference is not None
        return self.reference

    def purge(self):
        if self.mapped:
            self.purge_impl()
            self.mapped = False
            self.clean()

    def purge_impl(self):
        raise NotImplementedError


class MappableDict(MappableObject):
    def __init__(self, reference: Optional[SReference] = None):
        super().__init__(reference)
        self.content = dict()

    def put(self, key: str, value: SJSON):
        self.content[key] = value
        self.touch()

    def get(self, key: str) -> SJSON:
        return self.content[key]

    def purge_impl(self):
        self.content = dict()


class ComplexDict(MappableObject):
    def __init__(self, reference: Optional[SReference] = None):
        super().__init__(reference)
        self.content = dict()

    def put(self, key: str, value: SJSON):
        self.content[key] = value
        self.touch()

    def get(self, key: str) -> SJSON:
        return self.content[key]

    def purge_impl(self):
        self.content = dict()


class CTree(MappableObject):
    def __init__(self, reference: Optional[SReference] = None):
        super().__init__(reference)
        self.tree = dict()

    def put_c(self, path: str, mappable_dict: MappableDict):
        self.tree[path] = mappable_dict
        self.touch()

    def get_c(self, path: str) -> MappableDict:
        mappable_dict = self.tree[path]
        mappable_dict.read_in()
        return mappable_dict

    def purge_impl(self):
        self.tree = dict()

    def get_modifiable_mapped_sub_elements(self) -> Iterable:
        yield from self.tree.values()


class MappedDictMapper(Mapper):

    def read_in(self, mappable_object: MappableDict, reference: SReference):
        mappable_object.content = git_load_json(repo_dir, str(reference))

    def write_out(self, mappable_object: MappableDict) -> SReference:
        return git_save_json(repo_dir, mappable_object.content)


class ComplexDictMapper(Mapper):

    def read_in(self, complex_dict: ComplexDict, reference: SReference):
        first_level = git_load_json(repo_dir, str(reference))
        for key, value in first_level.items():
            complex_dict.content[key] = git_load_str(repo_dir, first_level[key])

    def write_out(self, complex_dict: ComplexDict) -> SReference:
        first_level = {
            key: git_save_str(repo_dir, value)
            for key, value in complex_dict.content.items()
        }
        return git_save_json(repo_dir, first_level)


class CTreeMapper(Mapper):

    def read_in(self, c_tree: CTree, reference: SReference):
        first_level = git_load_json(repo_dir, str(reference))
        logging.debug(f"CTreeMapper: read_in: first_level: {first_level}")
        for key, value in first_level.items():
            c_tree.tree[key] = MappableDict(git_load_str(repo_dir, first_level[key])[5:])

    def write_out(self, c_tree: CTree) -> SReference:
        first_level = {
            key: git_save_str(repo_dir, "link:" + mapped_dict.write_out())
            for key, mapped_dict in c_tree.tree.items()
        }
        logging.debug(f"CTreeMapper: write_out: first_level: {first_level}")
        return git_save_json(repo_dir, first_level)


mapper["MappableDict"] = MappedDictMapper()
mapper["ComplexDict"] = ComplexDictMapper()
mapper["CTree"] = CTreeMapper()


def test():

    ct = CTree()
    for path in ["a/b/c1", "a/b/c2", "a/b/c3"]:
        sub_elment = MappableDict()
        for ext in ("-v0", "-v1", "-v2"):
            sub_elment.put(path + ext, "This is value for: " + path + ext)
        ct.put_c(path, sub_elment)

    print(ct.is_modified())

    reference = ct.write_out()
    print(reference)

    print(ct.is_modified())

    md = ct.get_c("a/b/c1")
    md.put("test-mod", "a key to test modification")

    print(ct.is_modified())

    reference = ct.write_out()
    print(reference)

    ct.purge()

    ct2 = CTree(reference)
    ct2.read_in()

    print(ct2)

    return

    cd = ComplexDict()
    for key, value in (("a", "this is a"),
                       ("b", "bbbb is here!")):
        cd.put(key, value)

    print(cd.is_modified())

    reference = cd.write_out()
    print(reference)

    cd.purge()
    cd.read_in()
    print(cd.content)

    return
    md = MappableDict()
    for i in range(32):
        md.put(str(i), hex(i))

    print(md.is_modified())

    reference = md.write_out()
    print(reference)

    md.purge()
    md.read_in()
    print(md.content)


    md2 = MappableDict(reference)
    md2.read_in()
    print(md2.content)


if __name__ == "__main__":
    test()
