__author__ = 'hzlaimingxing'

import sys
import os
import tempfile
import unittest

pkg_root = os.path.realpath(os.path.join(os.path.realpath(__file__), os.path.pardir, os.path.pardir))
sys.path.append(pkg_root)

from nbs import NBS

def fake_success_execute():
    return 0

def fake_failed_execute():
    return 1

class TestNbsDisk(unittest.TestCase):

    def setUp(self):
        self.fake_mounts_data = ['rootfs / rootfs rw 0 0\n',
                             'rpc_pipefs /var/lib/nfs/rpc_pipefs rpc_pipefs rw,relatime 0 0\n',
                             '/dev/vdc /ebs xfs rw,relatime,attr2,delaylog,noquota 0 0\n']
        self.fake_mounts_file = os.path.join(tempfile.gettempdir(), 'mounts')

        self.fake_fstab_data = ['# /etc/fstab: static file system information.\n',
                             'UUID=a2de457e-f8a4-4031-9704-f56ac2666309 / ext4 errors=remount-ro 0       1\n']
                             #'/dev/nbs/xdjo /ebs xfs defaults 0 0\n']
        self.fake_fstab_file = os.path.join(tempfile.gettempdir(), 'fstab')

        with open(self.fake_fstab_file, 'w') as f:
            f.writelines(self.fake_fstab_data)
        with open(self.fake_mounts_file, 'w') as f:
            f.writelines(self.fake_mounts_data)

        self.disk = NBS()
        self.disk.set_test_data(self.fake_fstab_file, self.fake_mounts_file)


    def test_add_and_clear_record_for_fastb(self):
        self.assertTrue(self.disk._add_record_to_fstab('/dev/vdc'))
        with open(self.fake_fstab_file) as f:
            data = f.readlines()
        self.assertTrue(any( row.split()[1] == '/ebs'  for row in data if not row.startswith('#') ))

        self.disk._clear_from_fstab()
        with open(self.fake_fstab_file) as f:
            data = f.readlines()
        self.assertFalse(any( row.split()[1] == '/ebs'  for row in data if not row.startswith('#') ))


    def tearDown(self):
        if os.path.exists(self.fake_fstab_file):
            os.remove(self.fake_fstab_file)
        if os.path.exists(self.fake_mounts_file):
            os.remove(self.fake_mounts_file)

if __name__ == '__main__':
    unittest.main()

