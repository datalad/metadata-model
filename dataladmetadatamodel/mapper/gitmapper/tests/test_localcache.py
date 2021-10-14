import subprocess
import unittest

from ..localcache import (
    cache_object,
    get_cache_realm,
)


known_remote_repo = "https://github.com/datalad/datalad.git"
known_object_id = "b97c71ce4005cd9db0d5f2dda25bdbac303dabe7"


class TestLocalCache(unittest.TestCase):

    def test_local_cache(self):
        cache_object(known_remote_repo, known_object_id)
        result = subprocess.run(
            [
                "git",
                "-P",
                f"--git-dir={get_cache_realm(known_remote_repo) / '.git'}",
                "show",
                known_object_id
            ],
            stdout=subprocess.PIPE)

        self.assertTrue(result.stdout.decode().startswith("commit "))
