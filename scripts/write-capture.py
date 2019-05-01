# Run it like this
#
#   nbdkit -f -v python ./plugins/python/example.py disk=hd0.raw log=hd0.log
#
# The -f -v arguments are optional.  They cause the server to stay in
# the foreground and print debugging, which is useful when testing.
#
# disk specifies the name of the file that contains the raw image of the block
# device (it will be modified if clients request writes)
#
# log specifies the name of the file that will store the modifications as they
# happen
#
# You can connect to the server using guestfish or qemu, eg:
#
#   guestfish --format=raw -a nbd://localhost
#   ><fs> run
#   ><fs> part-disk /dev/sda mbr
#   ><fs> mkfs ext2 /dev/sda1
#   ><fs> list-filesystems
#   ><fs> mount /dev/sda1 /
#   ><fs> [etc]
from __future__ import print_function
import builtins

import nbdkit
import errno
import os
import sys
import time

from fsresck.imagegenerator import LogHeader

disk = None
disk_log = None


# This just prints the extra command line parameters, but real plugins
# should parse them and reject any unknown parameters.
def config(key, value):
    print(sys.version_info, file=sys.stderr)
    if key == "disk":
        global disk
        disk = builtins.open(value, "r+b")
    elif key == "log":
        global disk_log
        disk_log = builtins.open(value, "r+b")
    elif key == "script":
        pass  # ignoring
    else:
        raise ValueError("unknown parameter {0}={1}".format(key, value))


def open(readonly):
    print("open: readonly=%d" % readonly)

    # You can return any non-NULL Python object from open, and the
    # same object will be passed as the first arg to the other
    # callbacks [in the client connected phase].
    return 1


def get_size(h):
    global disk
    disk.seek(0, os.SEEK_END)
    return disk.tell()


def pread(h, count, offset):
    global disk
    disk.seek(offset, os.SEEK_SET)
    return bytearray(disk.read(count))


def pwrite(h, buf, offset):
    global disk
    # we need a timer that is consistent between processes
    # so that we know which writes happen in what order in multi-device
    # tests
    start = time.clock_gettime_ns(time.CLOCK_REALTIME)
    disk.seek(offset, os.SEEK_SET)
    disk.write(buf)
    header = LogHeader()
    header.operation = 1
    header.start_time = start
    header.end_time = time.clock_gettime_ns(time.CLOCK_REALTIME)
    header.offset = offset
    header.length = len(buf)
    disk_log.write(header.write())
    disk_log.write(buf)


def zero(h, count, offset, may_trim):
    global disk
    if not may_trim:
        nbdkit.set_error(errno.EOPNOTSUPP)
        raise ValueError("trim not supported")

    start = time.clock_gettime_ns(time.CLOCK_REALTIME)

    disk.seek(offset, os.SEEK_SET)
    disk.write(bytearray(count))
    header = LogHeader()
    header.operation = 1
    header.start_time = start
    header.end_time = time.clock_gettime_ns(time.CLOCK_REALTIME)
    header.offset = offset
    header.length = count
    disk_log.write(header.write())
    disk_log.write(bytearray(count))
