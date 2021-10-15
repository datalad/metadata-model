import json
import shlex
import subprocess
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union
)

from dataladmetadatamodel.log import logger
from dataladmetadatamodel.mapper.reference import Reference


def execute(arguments: Union[str, List[str]],
            stdin_content: Optional[Union[str, bytes]] = None) -> Any:

    logger.debug(f"gitbackend: execute({arguments}, {stdin_content})")
    return subprocess.run(
        shlex.split(arguments) if isinstance(arguments, str) else arguments,
        input=(
            stdin_content.encode()
            if isinstance(stdin_content, str)
            else stdin_content),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)


def checked_execute(arguments: Union[str, List[str]],
                    stdin_content: Optional[Union[str, bytes]] = None
                    ) -> Tuple[List[str], List[str]]:

    result = execute(arguments, stdin_content)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed (exit code: {result.returncode}) "
            f"{' '.join(arguments)}:\n"
            f"STDOUT:\n"
            f"{result.stdout.decode()}"
            f"STDERR:\n"
            f"{result.stderr.decode()}")
    return (
        result.stdout.decode().splitlines(),
        result.stderr.decode().splitlines())


def git_command_line(repo_dir: str,
                     command: str,
                     arguments: List[str]
                     ) -> List[str]:

    return [
               "git",
               "-P",
               "--git-dir",
               repo_dir + "/.git",
               command
           ] + arguments


def git_text_result(cmd_line):
    result = checked_execute(cmd_line)[0]
    return "\n".join(result)


def adapt_for_remote(repo_dir: str, object_reference: str) -> str:
    from dataladmetadatamodel.mapper.gitmapper.localcache import (
        cache_object,
        get_cache_realm,
    )

    if Reference.is_remote(repo_dir):
        cache_object(repo_dir, object_reference)
        return str(get_cache_realm(repo_dir))
    return repo_dir


def git_load_str(repo_dir: str, object_reference: str) -> str:
    repo_dir = adapt_for_remote(repo_dir, object_reference)
    cmd_line = git_command_line(repo_dir, "show", [object_reference])
    return git_text_result(cmd_line)


def git_load_json(repo_dir: str, object_reference: str) -> Union[Dict, List]:
    repo_dir = adapt_for_remote(repo_dir, object_reference)
    return json.loads(git_load_str(repo_dir, object_reference))


def git_init(repo_dir: str) -> None:
    cmd_line = ["git", "init", repo_dir]
    checked_execute(cmd_line)


def git_object_exists_locally(repo_dir: str,
                              object_reference) -> bool:
    cmd_line = git_command_line(repo_dir, "cat-file", ["-e", object_reference])
    return execute(cmd_line).returncode == 0


def git_read_tree_node(repo_dir: str,
                       object_reference) -> List[str]:
    repo_dir = adapt_for_remote(repo_dir, object_reference)
    cmd_line = git_command_line(repo_dir, "cat-file", ["-p", object_reference])
    return checked_execute(cmd_line)[0]


def git_ls_tree(repo_dir, object_reference) -> List[str]:
    repo_dir = adapt_for_remote(repo_dir, object_reference)
    cmd_line = git_command_line(repo_dir, "ls-tree", [object_reference])
    return checked_execute(cmd_line)[0]


def git_ls_tree_recursive(repo_dir, object_reference, show_intermediate=False) -> List[str]:
    repo_dir = adapt_for_remote(repo_dir, object_reference)
    if show_intermediate is True:
        cmd_line = git_command_line(repo_dir, "ls-tree", ["-r", "-t", object_reference])
    else:
        cmd_line = git_command_line(repo_dir, "ls-tree", ["-r", object_reference])
    return checked_execute(cmd_line)[0]


def git_save_str(repo_dir, content: str) -> str:
    cmd_line = git_command_line(repo_dir, "hash-object", ["-w", "--stdin"])
    return checked_execute(cmd_line, stdin_content=content)[0][0]


def git_save_json(repo_dir, json_object: Union[Dict, List]) -> str:
    return git_save_str(repo_dir, json.dumps(json_object))


def git_save_tree_node(repo_dir,
                       entry_set: Iterable[Tuple[str, str, str, str]]
                       ) -> str:

    tree_spec = "\n".join([
        f"{flag} {node_type} {object_hash}\t{name}"
        for flag, node_type, object_hash, name in entry_set
    ]) + "\n"
    cmd_line = git_command_line(repo_dir, "mktree", ["--missing", ])
    return checked_execute(cmd_line, stdin_content=tree_spec)[0][0]


def git_save_tree(repo_dir,
                  entry_set: Iterable[Tuple[str, str, str, str]]
                  ) -> str:
    tree_spec = "\n".join([
        f"{flag} {node_type} {object_hash}\t{name}"
        for flag, node_type, object_hash, name in entry_set
    ]) + "\n"
    cmd_line = git_command_line(repo_dir, "mktree", ["--missing", ])
    return checked_execute(cmd_line, stdin_content=tree_spec)[0][0]


def git_update_ref(repo_dir: str, ref_name: str, location: str) -> None:
    cmd_line = git_command_line(
        repo_dir,
        "update-ref",
        [ref_name, location])
    checked_execute(cmd_line)


def git_fetch_object(repo_dir: str,
                     remote_repo: str,
                     remote_reference: str):
    return git_fetch_reference(repo_dir, remote_repo, remote_reference)


def git_fetch_reference(repo_dir: str,
                        remote_repo: str,
                        remote_reference: str,
                        local_reference: Optional[str] = None):
    cmd_line = git_command_line(
        repo_dir,
        "fetch",
        [
            remote_repo,
            "-f",
            "--no-tags",
            "--no-recurse-submodules",
            remote_reference + (
                f":{local_reference}"
                if local_reference is not None
                else ""
            )
        ]
    )
    checked_execute(cmd_line)
