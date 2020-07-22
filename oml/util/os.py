import os
import platform


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def rchmod(path, mode, follow_symlinks=False):
    for root, dirs, files in os.walk(path):
        for f in files:
            os.chmod(os.path.join(root, f), mode,
                follow_symlinks=follow_symlinks)


def get_user():
    if platform.system() == 'Windows':
        return '{}\\{}'.format(os.environ['USERDOMAIN'], os.environ['USERNAME'])
    return os.environ['USER']
