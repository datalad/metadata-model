
from dataladmetadatamodel.connector import Connector


class GitFileTreeConnector(Connector):
    """
    A connector that connects git blob-references, found in
    git-trees, which point to persisted references with the
    referenced object
    """
    pass

