import shlex
import subprocess
from typing import Any, List, Optional, Tuple, Union


def execute(arguments: Union[str, List[str]],
            stdin_content: Optional[Union[str, bytes]] = None) -> Any:

    return subprocess.run(
        shlex.split(arguments) if isinstance(arguments, str) else arguments,
        input=stdin_content.encode() if isinstance(stdin_content, str) else stdin_content,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)


def checked_execute(arguments: Union[str, List[str]],
                    stdin_content: Optional[Union[str, bytes]] = None) -> Tuple[str, str]:

    result = execute(arguments, stdin_content)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed (exit code: {result.returncode}) {' '.join(arguments)}:\n"
            f"STDOUT:\n"
            f"{result.stdout.decode()}"
            f"STDERR:\n"
            f"{result.stderr.decode()}")
    return result.stdout.decode(), result.stderr.decode()
