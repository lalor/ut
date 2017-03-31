import os
import sys
import unittest

pkg_root = os.path.realpath(os.path.join(os.path.realpath(__file__), os.path.pardir, os.path.pardir))
sys.path.append(pkg_root)

from util import execute_cmd

class TestUtil(unittest.TestCase):

    def test_execute_cmd_success(self):
        cmd = "wc -l /etc/passwd"
        return_code, stdout = execute_cmd(cmd)
        # stdout = 29 /etc/passwd\n
        self.assertTrue(return_code == 0)
        self.assertGreaterEqual(int(stdout.split()[0]), 1)

    def test_execute_cmd_fail(self):
        cmd = "wc -l /etc/passwd_not_exists"
        return_code, stdout = execute_cmd(cmd)
        self.assertFalse(return_code == 0)


if __name__ == '__main__':
    unittest.main()
