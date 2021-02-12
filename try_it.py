from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata, ExtractorConfiguration, MetadataInstance
from dataladmetadatamodel.text import Text
from dataladmetadatamodel.uuidset import UUIDSet
from dataladmetadatamodel.versionlist import VersionList
from dataladmetadatamodel.mapper.reference import Reference
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references


MAPPER_FAMILY = "git"
REALM = "/home/cristian/tmp/mod_1"


uuid_0 = UUID("00000000000000000000000000000000")
uuid_1 = UUID("00000000000000000000000000000001")
uuid_2 = UUID("00000000000000000000000000000002")


try_create_metadata_from_dataset = True
try_create_tree_version_list = True
try_metadata_objects = True
try_dataset_tree = True
try_tree = True
try_read = True
try_write = False


if try_create_metadata_from_dataset:
    from tools.metadata_creator.mimic import create_metadata_from_dataset

    realm = "/home/cristian/tmp/mm3"
    dataset_path = "/home/cristian/datalad/datasets.datalad.org"
    #dataset_path = "/home/cristian/datalad/tset1"

    result = create_metadata_from_dataset(
        "git",
        realm, dataset_path
    )
    print(result)
    exit(0)


if try_create_tree_version_list:
    from tools.metadata_creator.treeversionlistcreator import create_tree_version_list
    from tools.metadata_creator.uuidsetcreator import create_uuid_set

    realm = "/home/cristian/tmp/mm2"
    dataset_path = "/home/cristian/datalad/datasets.datalad.org"
    #dataset_path = "/home/cristian/datalad/tset1"

    tvl = create_tree_version_list(
        "git",
        realm,
        dataset_path,
        {
            "p1": "v1"
        }
    )
    tvl.save()
    uuids = create_uuid_set(
        "git",
        realm,
        dataset_path,
        {
            "p2": "v2"
        }
    )
    uuids.save()
    flush_object_references(realm)
    exit(0)


if try_metadata_objects:
    ec1 = ExtractorConfiguration(
        "1.0",
        {
            "param_1": "1.1",
            "param_2": "2.1",
            "param_3": "3.1",
            "param_4": "4.1",
        }
    )

    ec2 = ExtractorConfiguration(
        "1.0",
        {
            "param_1": "1.2",
            "param_2": "2.2",
            "param_3": "3.2",
            "param_4": "4.2",
        }
    )

    ec3 = ExtractorConfiguration(
        "1.0",
        {
            "param_1": "1.3",
            "param_2": "2.3",
            "param_3": "3.3",
            "param_4": "4.3",
        }
    )

    mi1 = MetadataInstance(
        "01:00:00",
        "x y",
        "x.y@mail.com",
        ec1,
        "source for blob 1"
    )

    mi2 = MetadataInstance(
        "02:00:00",
        "x y",
        "x.y@mail.com",
        ec2,
        "source for blob 2"
    )

    mi3 = MetadataInstance(
        "03:00:00",
        "x y",
        "x.y@mail.com",
        ec3,
        "source for blob 3"
    )

    m1 = Metadata(
        MAPPER_FAMILY,
        REALM,
        {"core-extractor": {mi1, mi2, mi3}}
    )

    if not (try_tree or try_dataset_tree):
        exit(0)


if try_dataset_tree:
    mrr = MetadataRootRecord(
        MAPPER_FAMILY,
        REALM,
        uuid_2,
        "aaa34239081abea9087987897",
        Connector.from_object(Text("dataset-level-metadata-connector")),
        Connector.from_object(Text("file-tree-connector")),
    )

    dt = DatasetTree(MAPPER_FAMILY, REALM)
    dt.add_dataset("a/b/c/d", mrr)
    dt.add_dataset("a/b", mrr)

    reference = dt.save()
    print(reference)

    dt_2_con = Connector.from_reference(reference)
    dt_2 = dt_2_con.load_object(MAPPER_FAMILY, REALM)
    reference2 = dt_2_con.save_object(MAPPER_FAMILY, REALM)
    print(reference2)

    exit(0)


if try_tree:

    paths = [
        "a.1/b.1/c.1",
        "a.1/b.1/c.2",
        "a.1/b.1/c.3",
        "a.1/b.1/c.4",
        "a.1/b.2/c.1",
        "a.2/b.2/c.1",
        "a.2/b.2/c.2",
    ]

    ft = FileTree(MAPPER_FAMILY, REALM)
    for path in paths:
        ft.add_metadata(path, m1)
    reference = ft.save()
    print(reference)

    exit(0)



if try_read:

    # Read an object hierarchy
    c = Connector.from_reference(
        Reference(
            MAPPER_FAMILY,
            "UUIDSet",
            "refs/develop/dataset-set"
        )
    )

    loaded_uuid_set: UUIDSet = c.load_object(MAPPER_FAMILY, REALM)
    version_list_uuid_0 = loaded_uuid_set.get_version_list(uuid_0)
    mrr = version_list_uuid_0.get_dataset_tree("pd-version-1.1")

    print(loaded_uuid_set)
    print(mrr)

    exit(0)


if try_write:

    # Save an in-memory create object hierarchy
    MetadataRootRecord = Text

    version_list_1 = VersionList(MAPPER_FAMILY, REALM)
    version_list_1.set_metadata_root_record("pd-version-1.1", "10:00:00", "/uuid-1", Text("metadata-for pd-version-1.1"))
    version_list_1.set_metadata_root_record("pd-version-1.2", "12:02:00", "/uuid-1", Text("metadata-for pd-version-1.2"))

    version_list_2 = VersionList(MAPPER_FAMILY, REALM)
    version_list_2.set_metadata_root_record("pd-version-2.1", "20:00:00", "/uuid-2", Text("metadata-for pd-version-2.1"))
    version_list_2.set_metadata_root_record("pd-version-2.2", "22:02:00", "/uuid-2", Text("metadata-for pd-version-2.2"))

    uuid_set = UUIDSet(MAPPER_FAMILY, REALM)
    uuid_set.set_version_list(uuid_0, version_list_1)
    uuid_set.set_version_list(uuid_1, version_list_2)

    reference = uuid_set.save()
    print(reference)

    exit(0)
