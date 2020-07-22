import os
import shutil
import zipfile


def archive(src, dest, filename):
    os.chdir(dest)
    zf = shutil.make_archive(filename, 'zip', src)
    os.chdir(os.path.expanduser('~'))
    return zf


def extract(src, dest):
    with zipfile.ZipFile(src, 'r') as zf:
        zf.extractall(dest)
