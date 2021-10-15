import re
import subprocess
import unittest
from typing import (
    List,
    Tuple,
)

from ..localcache import (
    cache_object,
    get_cache_realm,
)


known_remote_objects = [
    (
        "https://github.com/datalad/datalad.git",
        "b97c71ce4005cd9db0d5f2dda25bdbac303dabe7",
        ["commit .*", "Author: Michael Hanke.*"]
    ),
    (
        "https://github.com/datalad/datalad-metalad.git",
        "9f718f8623e961b93f7f8b6f43f53d94fb405832",
        ["commit .*", "Merge: 9fd8929 898ff01.*"]
    )
]


known_remote_references = [
    (
        "https://github.com/datalad/datalad.git",
        "refs/tags/0.2.1",
        ["tag 0.2.1", "Tagger: Yaroslav Halchenko.*"]
    ),
    (
        "https://github.com/datalad/datalad-metalad.git",
        "refs/tags/0.2.1",
        ["tag 0.2.1", "Tagger: Michael Hanke.*"]
    )
]


class TestLocalCache(unittest.TestCase):

    def cache(self, specs: List[Tuple[str, str, List[str]]]):
        for repo, object_id, _ in specs:
            cache_object(repo, object_id)

    def check_cached(self, specs: List[Tuple[str, str, List[str]]]):
        for repo, object_id, line_patterns in specs:
            result = subprocess.run(
                [
                    "git",
                    "-P",
                    f"--git-dir={get_cache_realm(repo) / '.git'}",
                    "show",
                    object_id
                ],
                stdout=subprocess.PIPE
            )
            self.assertEqual(result.returncode, 0)
            lines = result.stdout.decode().splitlines()
            for index, pattern in enumerate(line_patterns):
                self.assertIsNotNone(re.match(pattern, lines[index]))

    def test_local_cache_object(self):
        self.cache(known_remote_objects)
        self.check_cached(known_remote_objects)

    def test_local_cache_reference(self):
        # check that identical refs in different repos
        # are kept separate
        self.cache(known_remote_references)
        self.check_cached(known_remote_references)
