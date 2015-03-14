#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2015 Hubert Kario. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""Utility functions"""

import subprocess
import tempfile
import os
from .errors import FSCopyError

def copy(source, destination):
    """
    copy file from source to destination

    Copy a file using the os `cp` command with options that should preserve
    sparse information and CoW status
    """
    # we want the copy to be CoW aware and preserve sparse locations
    # so we need to use the native cp command
    ret = subprocess.call(['cp', '--reflink=auto', '--sparse=always',
                           source, destination])
    if ret != 0:
        raise FSCopyError("File copy failed, error {0}".format(ret))

def get_temp_file_name(directory, prefix='fsresck.'):
    """
    Create a file with unique name in directory

    Create a File in provided directory with unique name in safe and atomic
    way
    """
    handle, file_name = tempfile.mkstemp(prefix=prefix, dir=directory)
    os.close(handle)
    return file_name
