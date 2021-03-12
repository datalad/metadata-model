from pathlib import PurePosixPath


class MetadataPath(PurePosixPath):
    def __str__(self):
        path_str = PurePosixPath.__str__(self)
        return (
            ""
            if path_str == "."
            else path_str)
