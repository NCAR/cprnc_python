
import os
import shutil
import subprocess
import random
import string

"""
OS Dependent utility
Used to copy and remove files from a fast tmpfs filesystem
Does not work when the tmpfs directory has spaces due to mtab
"""

def find_tmpfs():
    """
    Finds all currently available tmpfs file systems from mtab
    """
    mtab = open('/etc/mtab', 'r')
    tmpfs = []
    for l in mtab:
        if 'tmpfs' in l:
            start = l.find('/')
            end = l.rfind(' tmpfs')
            path = l[start:end]
            if os.path.isabs(path) and os.path.isdir(path):
                tmpfs.append(path)
    return tmpfs

def get_tmpfname(tmpfs):
    """
    Creates a random filename for the copy,
    then returns the absolute path for the resulting copy
    """
    fname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    return os.path.join(tmpfs, fname)

def tmpfs_copy_py(fpath):
    """
    Uses Python's shutil to copy the file.
    This is slightly slower than using the subprocess module to use the copy utility
    """
    tmpfname = get_tmpfname(find_tmpfs()[0])
    shutil.copyfile(fpath, tmpfname)
    return tmpfname

def tmpfs_copy_sh(fpath):
    """
    Uses the copy utility through the subprocess module
    This is slightly less nice than using shutil, and more OS dependent
    """
    tmpfname = get_tmpfname(find_tmpfs()[0])
    cpcmd = ['cp', fpath, tmpfname]
    p = subprocess.Popen(cpcmd)
    p.wait()
    return tmpfname

tmpfs_copy = tmpfs_copy_sh
