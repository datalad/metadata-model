from typing import Optional

from dataladmetadatamodel.mapper.gitmapper.objectreference import (
    GitReference,
    add_tree_reference
)
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_ls_tree_recursive,
    git_save_tree
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


DATALAD_ROOT_RECORD_NAME = ".datalad_metadata_root_record"


class DatasetTreeGitMapper(Mapper):

    def _save_dataset_tree(self,
                           node: "TreeNode",
                           destination: str
                           ) -> Optional[str]:
        dir_entries = []

        if node.value is not None:
            from dataladmetadatamodel.metadatarootrecord import \
                MetadataRootRecord

            assert isinstance(node.value, MetadataRootRecord)
            mrr_reference = node.value.write_out(destination)
            dir_entries.append((
                "100644",
                "blob",
                mrr_reference.location,
                DATALAD_ROOT_RECORD_NAME))

        for name, child_node in node.child_nodes.items():
            sub_dir_hash = self._save_dataset_tree(child_node, destination)
            if sub_dir_hash:
                dir_entries.append((
                    "040000",
                    "tree",
                    sub_dir_hash,
                    name))

        if dir_entries:
            return git_save_tree(destination, dir_entries)
        else:
            return None

    def map_in_impl(self,
                    dataset_tree: "DatasetTree",
                    reference: Reference) -> None:

        from dataladmetadatamodel.datasettree import DatasetTree
        from dataladmetadatamodel.metadatapath import MetadataPath
        from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
        from dataladmetadatamodel.treenode import TreeNode

        assert isinstance(dataset_tree, DatasetTree)

        # Empty dataset trees are identified by a None-reference
        if reference.is_none_reference():
            dataset_tree.child_nodes = {}
            dataset_tree.value = None
            return

        # List all leaf-nodes. Those should only end with the datalad
        # root record-name. Add the hierarchy except the leaf-node,
        # read the metadata root record from the leave node, and
        # add it as value to the hierarchy.
        for line in git_ls_tree_recursive(reference.realm, reference.location):

            _, _, location, path_string = line.split()
            path = MetadataPath(path_string)
            assert path.name == DATALAD_ROOT_RECORD_NAME

            # TODO: this is quite ugly. We should provide a general
            #  mechanism to read an object from the backend instead
            #  of initializing an empty object and the filling it.
            metadata_root_record = MetadataRootRecord(
                dataset_identifier=None,
                dataset_version=None,
                dataset_level_metadata=None,
                file_tree=None,
                reference=Reference(
                    "git",
                    reference.realm,
                    "MetadataRootRecord",
                    location))

            metadata_root_record.read_in()

            dataset_tree.add_node_hierarchy(
                MetadataPath(*path.parts[:-1]),
                TreeNode(metadata_root_record),
                allow_leaf_node_conversion=True)

    def map_out_impl(self,
                     dataset_tree: "DatasetTree",
                     destination: str,
                     force_write: bool) -> Reference:
        """
        Save DatasetTree as git tree with DATALAD_ROOT_RECORD_NAME
        nodes for each MetadataRootRecord instance.
        """
        from dataladmetadatamodel.datasettree import DatasetTree

        assert isinstance(dataset_tree, DatasetTree)

        if dataset_tree.child_nodes == {} and dataset_tree.value is None:
            return Reference.get_none_reference("DatasetTree")

        dataset_tree_hash = self._save_dataset_tree(dataset_tree, destination)
        add_tree_reference(GitReference.DATASET_TREE, dataset_tree_hash)
        return Reference("git", destination, "DatasetTree", dataset_tree_hash)
