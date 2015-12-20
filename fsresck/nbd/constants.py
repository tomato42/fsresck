# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Description: File system resilience testing application
#   Author: Hubert Kario <hubert@kario.pl>
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

"""Protocol constants definitions."""


class Magic(object):

    """Magic values from NBD protocol."""

    NBD_REQUEST_MAGIC = 0x25609513
    NBD_REPLY_MAGIC = 0x67446698


class GlobalFlags(object):

    """Flags set by server in initial transfer."""

    NBD_FLAG_FIXED_NEWSTYLE = 0x01
    NBD_FLAG_NO_ZEROES = 0x01 << 1


class RequestType(object):

    """Type of requests supported by protocol."""

    NBD_CMD_READ = 0
    NBD_CMD_WRITE = 1
    NBD_CMD_DISC = 2
    NBD_CMD_FLUSH = 3
    NBD_CMD_TRIM = 4


class Error(object):

    """Error values in NBD protocol."""

    EPERM = 1
    EIO = 5
    ENOMEM = 12
    EINVAL = 22
    ENOSPC = 28
