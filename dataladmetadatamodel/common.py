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

    if sub_dataset_id is not None:
        metadata_root_record = get_metadata_root_record_from_top_nodes(
            tree_version_list,
            uuid_set,
            sub_dataset_id,
            sub_dataset_version,
            prefix_path,
            dataset_tree_path,
            dataset_id,
            primary_data_version,
            auto_create)
    else:
        metadata_root_record = get_metadata_root_record_from_top_nodes(
            tree_version_list,
            uuid_set,
            dataset_id,
            primary_data_version,
            prefix_path,
            dataset_tree_path,
            None,
            None,
            auto_create)

    return tree_version_list, uuid_set, metadata_root_record


def get_metadata_root_record_from_top_nodes(
        tree_version_list: TreeVersionList,
        uuid_set: UUIDSet,
        dataset_id: UUID,
        primary_data_version: str,
        prefix_path: MetadataPath,
        dataset_tree_path: MetadataPath,
        root_dataset_id: Optional[UUID],
        root_dataset_version: Optional[str],
        auto_create: Optional[bool] = False
) -> Optional[MetadataRootRecord]:

    """
    Return a metadata root record for the dataset id `dataset_id` and the
    dataset version `primary_data_version`. If `root_dataset_id` and
    `root_dataset_version` or not `None`, and if `dataset_tree_path` is not
    None, the metadata record will be in the dataset tree of the root dataset
    version.

    If auto_create is True, create all necessary tree nodes and the metadata
    root record with empty dataset metadata and an empty file-tree. It will
    also add the datasets to the UUID set and the tree version list, if
    necessary.

    If auto_create is False and the metadata root record does not exist None
    is returned.

    If you want to preserve any changes or any created metadata objects, you
    have to save the returned objects (or their containers) and flush the
    realm.
    """
    if uuid_set is None or tree_version_list is None:
        return None

    is_sub_dataset = dataset_tree_path != MetadataPath("")
    if is_sub_dataset:
        assert root_dataset_id is not None
        assert root_dataset_version is not None

    # If there is a root dataset id, make sure that the root dataset elements
    # exist or return if `auto_create` is `False`.
    if is_sub_dataset:
        if root_dataset_id in uuid_set.uuids():
            root_uuid_version_list = uuid_set.get_version_list(root_dataset_id)
        else:
            if auto_create is False:
                return None
            root_uuid_version_list = VersionList()
            uuid_set.set_version_list(root_dataset_id, root_uuid_version_list)

        if (root_dataset_version, prefix_path) in tree_version_list.versions_and_prefix_paths():
            _, _, dataset_tree = tree_version_list.get_dataset_tree(
                primary_data_version=root_dataset_version,
                prefix_path=prefix_path)
        else:
            if auto_create is False:
                return None
            dataset_tree = DatasetTree()
            tree_version_list.set_dataset_tree(
                primary_data_version=root_dataset_version,
                time_stamp=str(time.time()),
                prefix_path=prefix_path,
                dataset_tree=dataset_tree)

        if MetadataPath("") not in dataset_tree:
            if auto_create is False:
                return None
            root_mrr = MetadataRootRecord(
                dataset_identifier=root_dataset_id,
                dataset_version=root_dataset_version,
                dataset_level_metadata=Metadata(),
                file_tree=FileTree())
            dataset_tree.add_dataset(MetadataPath(""), root_mrr)
        else:
            root_mrr = dataset_tree.get_metadata_root_record(MetadataPath(""))

        if (root_dataset_version, prefix_path) not in root_uuid_version_list.versions_and_prefix_paths():
            root_uuid_version_list.set_versioned_element(
                primary_data_version=root_dataset_version,
                time_stamp=str(time.time()),
                prefix_path=prefix_path,
                element=root_mrr)

        prefix_path = MetadataPath("")
    else:

        # Get the dataset tree
        if (primary_data_version, prefix_path) in tree_version_list.versions_and_prefix_paths():
            _, _, dataset_tree = tree_version_list.get_dataset_tree(
                primary_data_version=primary_data_version,
                prefix_path=prefix_path)
        else:
            if auto_create is False:
                return None
            dataset_tree = DatasetTree()
            tree_version_list.set_dataset_tree(
                primary_data_version=primary_data_version,
                time_stamp=str(time.time()),
                prefix_path=prefix_path,
                dataset_tree=dataset_tree)

    if dataset_id in uuid_set.uuids():
        uuid_version_list = uuid_set.get_version_list(dataset_id)
    else:
        if auto_create is False:
            return None
        uuid_version_list = VersionList()
        uuid_set.set_version_list(dataset_id, uuid_version_list)

    if dataset_tree_path not in dataset_tree:
        if auto_create is False:
            return None
        metadata_root_record = MetadataRootRecord(
            dataset_identifier=dataset_id,
            dataset_version=primary_data_version,
            dataset_level_metadata=Metadata(),
            file_tree=FileTree())
        dataset_tree.add_dataset(dataset_tree_path, metadata_root_record)
    else:
        metadata_root_record = dataset_tree.get_metadata_root_record(
            dataset_tree_path)

    if (primary_data_version, prefix_path) not in uuid_version_list.versions_and_prefix_paths():
        uuid_version_list.set_versioned_element(
            primary_data_version=primary_data_version,
            time_stamp=str(time.time()),
            prefix_path=prefix_path,
            element=metadata_root_record)

    return metadata_root_record
