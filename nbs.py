# -*- coding:UTF-8 -*-

__author__ = 'hzlaimingxing'

import os
import time
import tempfile

from util import execute


class NBS(object):

    def __init__(self, mount_dir=r'/ebs'):
        self.mount_dir = mount_dir
        self.fstab = '/etc/fstab'
        self.tmp_fstab = os.path.join(tempfile.gettempdir(), 'fstab.tmp')
        self.mounts = '/proc/mounts'

    def set_test_data(self, fstab, mounts):
        self.fstab = fstab
        self.mounts = mounts


    def _add_record_to_fstab(self, device):
        """
         把device信息写入fstab文件，写入前，先备份当前fstab，然后写入fstab，
         如果写入成功，则用备份文件覆盖修改过的文件，如果写入成功，删除备份文件。
        """
        with open(self.fstab) as source, open(self.tmp_fstab, 'w') as target:
            target.write(source.read())

        with open(self.tmp_fstab, 'a') as target:
            target.write('{0} {1} xfs defaults 0 0'.format(device, self.mount_dir))

        return execute("sudo cp -f {0} {1}".format(self.tmp_fstab, self.fstab))


    def _clear_from_fstab(self):
        """ 从fstab文件中删除ebs信息 """
        with open(self.fstab) as source:
            lines = source.readlines()

        data = [ line.split() for line in lines if not line.startswith('#') ]
        """ [
          ['UUID=a56ac2666309', '/', 'ext4', 'errors=remount-ro', '0', '1'],
          ['/dev/nbs/xdjo', '/ebs', 'xfs', 'defaults', '0', '0'] ] """
        data = [row for row in data if row[1] != '{0}'.format(self.mount_dir) ]
        with open(self.tmp_fstab) as target:
            target.writeline(data)
        return execute("sudo mv {0} {1}".format(self.tmp_fstab, self.fstab))


    def _is_mounted_already(self):
        """
        读取/proc/mounts文件，判断是否有我们的挂载点，如果有，则说明磁盘已经挂载成功

        rds-user@lmx:~$ cat /proc/mounts
        udev /dev devtmpfs rw,relatime,size=10240k,nr_inodes=764909,mode=755 0 0
        /dev/vdc /ebs xfs rw,relatime,attr2,delaylog,noquota 0 0
        """
        with open(self.mounts) as f:
            data = f.readlines()
        return (row.split()[1] == '/ebs' for row in data)


    def _ensure_device_exists(self, device):
        return os.path.exists(device)


    def mount(self, device):
        """ 磁盘挂载 """
        if self._is_mounted_already():
            return True

        if not self._ensure_device_exists(device):
            return False

        # 检查挂载路径是否存在，不存在则创建路径
        if not os.path.exists(self.mount_dir):
            execute("sudo mkdir {0}".format(self.mount_dir))

        if not self._add_record_to_fstab(device):
            return False

        # 挂载磁盘到指定目录
        return execute("sudo mount -t xfs {0} {1}".format(device, self.mount_dir))


    def _do_umount_disk(self):
        # 断开所有该盘上的连接
        execute("sudo fuser -mk {0}".format(self.mount_dir))
        # 卸载当前盘
        execute("sudo umount {0}".format(self.mount_dir))


    def umount(self):

        if not self._clear_from_fstab():
            return False

        retry_count = 50
        while retry_count:
            retry_count -= 1
            if not self._is_mounted_already():
                return True   # 已经卸载，则返回
            else:
                time.sleep(1)
                self._do_umount_disk()

        return False


    def format(self, device):
        """
         格式化磁盘，调用mkfs.xfs命令
        """
        if self._is_mounted_already():
            return True

        if not self._ensure_device_exists(device):
            return False

        return execute("sudo mkfs.xfs -f {0}".format(device))
