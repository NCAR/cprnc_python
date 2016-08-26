
import os
import shutil
import subprocess

#OS Dependant utility
def find_tmpfs():
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

def get_tmpfname(fpath, tmpfs):
    fname = os.path.basename(fpath)
    return os.path.join(tmpfs, fname)

def tmpfs_copy(fpath, tmpfs):
    tmpfname = get_tmpfname(fpath, tmpfs)
    shutil.copyfile(fpath, tmpfname)

def tmpfs_copy_sh(fpath, tmpfs):
    tmpfname = get_tmpfname(fpath, tmpfs)
    cpcmd = ['cp', fpath, tmpfname]
    p = subprocess.Popen(cpcmd)
    p.wait()

def rm_tmpfs_copy(fpath, tmpfs):
    tmpfname = get_tmpfname(fpath, tmpfs)
    os.remove(tmpfname)
