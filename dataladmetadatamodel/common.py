"""
Commonly used functionality
"""
import time
from pathlib import Path
from typing import (
    Optional,
    Tuple,
    Union,
)
from uuid import UUID

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.uuidset import UUIDSet
from dataladmetadatamodel.versionlist import (
    TreeVersionList,
    VersionList,
)
from dataladmetadatamodel.mapper.reference import Reference


def _get_tree_version_list_reference(location: str
                                     ) -> Reference:

    return Reference("TreeVersionList", location)


def _get_uuid_set_reference(
        mapper_family: str,
        realm: str,
        location: str) -> Reference:

    return Reference(
        "UUIDSet",
        location)


def get_top_level_metadata_objects(
        mapper_family: str,
        realm: Union[str, Path]
        ) -> Tuple[Optional[TreeVersionList], Optional[UUIDSet]]:

    """
    Load the two top-level metadata elements from a realm, i.e.
    the tree version list and the uuid list.

    We do this be creating references from known locations
    in the mapper family and loading the referenced objects.
    """
    from dataladmetadatamodel.mapper import (
        get_uuid_set_location,
        get_tree_version_list_location)

    realm = str(realm)

    tree_version_list = TreeVersionList(
        realm=realm,
        reference=_get_tree_version_list_reference(
            get_tree_version_list_location(mapper_family)))

    uuid_set = UUIDSet(
        realm=realm,
        reference=_get_uuid_set_reference(
            mapper_family,
            realm,
            get_uuid_set_location(mapper_family)))

    try:
        return tree_version_list.read_in(), uuid_set.read_in()
    except RuntimeError:
        return None, None


def get_top_nodes_and_metadata_root_record(
        mapper_family: str,
        realm: str,
        dataset_id: UUID,
        primary_data_version: str,
        prefix_path: MetadataPath,
        dataset_tree_path: MetadataPath,
        sub_dataset_id: Optional[UUID],
        sub_dataset_version: Optional[str],
        auto_create: Optional[bool] = False
) -> Tuple[Optional[TreeVersionList], Optional[UUIDSet], Optional[MetadataRootRecord]]:

    """
    Return the top nodes and metadata root record for a given dataset id
    and a given dataset version.

    If auto_create is True, create missing entries for the given dataset
    version, down to and including the metadata root record with empty
    dataset metadata and an empty file-tree connected to it.

    If auto_create is False and any of the elements: uuid set, version tree
    list, or metadata root record does not exist, (None, None, None) is
    returned.

    If you want to preserve any changes, are created metadata objects,
    you have to save the returned objects and flush the realm
    """
    tree_version_list, uuid_set = get_top_level_metadata_objects(
        mapper_family,
        realm)

    if tree_version_list is None and auto_create:
        tree_version_list = TreeVersionList()

    if uuid_set is None and auto_create:
        uuid_set = UUIDSet()

    if uuid_set is None or tree_version_list is None:
        return None, None, None

    metadata_root_record = get_metadata_root_record_from_top_nodes(
        tree_version_list,
        uuid_set,
        dataset_id,
        primary_data_version,
        prefix_path,
        dataset_tree_path,
        sub_dataset_id,
        sub_dataset_version,
        auto_create)

    return tree_version_list, uuid_set, metadata_root_record


def get_metadata_root_record_from_top_nodes(
        tree_version_list: TreeVersionList,
        uuid_set: UUIDSet,
        dataset_id: UUID,
        primary_data_version: str,
        prefix_path: MetadataPath,
        dataset_tree_path: MetadataPath,
        sub_dataset_id: Optional[UUID],
        sub_dataset_version: Optional[str],
        auto_create: Optional[bool] = False
) -> Optional[MetadataRootRecord]:

    """
    The metadata root record for a given dataset id and a given dataset version.

    If auto_create is True, create the metadata root record with empty
    dataset metadata and an empty file-tree connected to it.

    If auto_create is False and the metadata root record does not exist, None
    is returned.

    If you want to preserve any changes, to the created metadata objects,
    you have to save the returned objects (or their containers) and flush the
    realm.
    """
    if uuid_set is None or tree_version_list is None:
        return None

    if dataset_id in uuid_set.uuids():
        uuid_version_list = uuid_set.get_version_list(dataset_id)
    else:
        if auto_create is False:
            return None
        uuid_version_list = VersionList()
        uuid_set.set_version_list(dataset_id, uuid_version_list)

    # Get the dataset tree
    if (primary_data_version, prefix_path) in tree_version_list.versions_and_prefix_paths():
        time_stamp, prefix_path, dataset_tree = \
            tree_version_list.get_dataset_tree(primary_data_version, prefix_path)
    else:
        if auto_create is False:
            return None
        time_stamp = str(time.time())
        dataset_tree = DatasetTree()
        # TODO: set prefix_path
        # TODO: distinguish between unversioned prefix_path and dataset tree prefix_path
        tree_version_list.set_dataset_tree(
            primary_data_version=primary_data_version,
            time_stamp=time_stamp,
            prefix_path=prefix_path,
            dataset_tree=dataset_tree)

    if dataset_tree_path not in dataset_tree:
        if auto_create is False:
            return None

        dataset_level_metadata = Metadata()
        file_tree = FileTree()
        if dataset_tree_path != MetadataPath(""):
            assert sub_dataset_id is not None
            assert sub_dataset_version is not None
            metadata_root_record = MetadataRootRecord(
                sub_dataset_id,
                sub_dataset_version,
                dataset_level_metadata,
                file_tree)
        else:
            metadata_root_record = MetadataRootRecord(
                dataset_id,
                primary_data_version,
                dataset_level_metadata,
                file_tree)
        dataset_tree.add_dataset(dataset_tree_path, metadata_root_record)
    else:
        metadata_root_record = dataset_tree.get_metadata_root_record(
            dataset_tree_path)

    uuid_version_list.set_versioned_element(
        primary_data_version,
        str(time.time()),
        dataset_tree_path,
        metadata_root_record)

    return metadata_root_record
