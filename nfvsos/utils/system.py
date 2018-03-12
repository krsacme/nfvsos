import os

KERNEL_CMDLINE = '/proc/cmdline'


def get_cmdline(basedir):
    cmdline_path = os.path.join(basedir, KERNEL_CMDLINE[1:])
    cmdline = []
    with open(cmdline_path) as f:
        cmdline_str = f.read().strip()
        cmdline = cmdline_str.split(' ')
    return cmdline
