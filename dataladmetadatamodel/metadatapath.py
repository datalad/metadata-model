from pathlib import PurePosixPath

from dataladmetadatamodel.log import logger


class MetadataPath(PurePosixPath):
    def __new__(cls, *args):

        posix_args = []
        for arg in args:
            if isinstance(arg, str):
                arg.replace("\\", "/")
            posix_args.append(arg)

        original_path = PurePosixPath(*posix_args)
        if not original_path.is_absolute():
            created_path = super().__new__(
                cls,
                "/".join(original_path.parts))
        else:
            modified_path = "/".join(original_path.parts[1:])
            created_path = super().__new__(cls, modified_path)
            logger.warning(
                f"Denied creation of absolute metadata path: {original_path}, "
                f"created {modified_path} instead. This is considered an error "
                f"in the calling code.")

        return created_path

    def __str__(self):
        path_str = PurePosixPath.__str__(self)
        return (
            ""
            if path_str == "."
            else path_str)

    def __len__(self):
        return len(self.parts)
