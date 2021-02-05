import sys
from typing import Optional
from uuid import UUID

from tools.metadata_creator.execute import checked_execute


def get_dataset_id(path) -> Optional[UUID]:
    config_file_path = path + "/.datalad/config"
    try:
        with open(config_file_path) as f:
            for line in f.readlines():
                elements = line.split()
                if elements[:2] == ["id", "="]:
                    return UUID(elements[2])
        print("WARNING: no dataset id in config file: " + config_file_path, file=sys.stderr)
        return None
    except FileNotFoundError:
        print("WARNING: could not open config file: " + config_file_path, file=sys.stderr)
        return None


def get_dataset_version(path) -> Optional[str]:
    git_dir = path + "/.git"
    try:
        return checked_execute(
            ["git", f"--git-dir", git_dir, "log", "-1", "--pretty=format:%H"]
        )[0].strip()
    except RuntimeError:
        return None

