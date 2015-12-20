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

"""Handling of NBD requests."""

import struct

from .constants import Magic, RequestType
from ..compat import compat_str


class Error(Exception):

    """Exception describing what went wrong."""

    def __repr__(self):
        """Format exception."""
        return "request.{0}".format(super(Error, self).__repr__())


class NBDRequest(object):

    """Representation of single NBD protocol request."""

    def __init__(self, req_type, handle, data_from, data_length, data=None):
        """Make a NBD protocol request object."""
        self.req_type = req_type
        self.handle = handle
        self.data_from = data_from
        self.data_length = data_length
        self.data = data

    def __eq__(self, other):
        """Check if the other object is equal to this object."""
        return (isinstance(other, self.__class__) and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        """Check if the other object is different from this object."""
        return not self.__eq__(other)


def recvexactly(sock, size, flags=0):
    """recv exactly size bytes from socket."""
    buff = bytearray(size)
    view = memoryview(buff)
    pos = 0
    while pos < size:
        read = sock.recv_into(view[pos:], size - pos, flags)
        if not read:
            raise Error("Incomplete read, expected {0}, read {1}"
                        .format(size, size))
        pos += read
    return buff


class NBDRequestSocket(object):

    """Handle requests on NBD socket."""

    request_fmt = ">IIQQI"
    request_length = struct.calcsize(request_fmt)

    def __init__(self, sock):
        """Initialize the socket wrapper."""
        self.sock = sock

    def recv(self):
        """Receive a single request from socket and return it."""
        data = recvexactly(self.sock, self.request_length)
        assert len(data) == self.request_length
        data = compat_str(data)
        result_tuple = struct.unpack(self.request_fmt, data)
        magic, req_type, handle, data_from, data_length = result_tuple

        if magic != Magic.NBD_REQUEST_MAGIC:
            raise Error("Request magic invalid: {0}".format(magic))

        if req_type != RequestType.NBD_CMD_WRITE:
            return NBDRequest(req_type, handle, data_from, data_length)

        payload = recvexactly(self.sock, data_length)
        return NBDRequest(req_type, handle, data_from, data_length, payload)

    def send(self, request):
        """Send a single request through socket."""
        data = struct.pack(self.request_fmt,
                           Magic.NBD_REQUEST_MAGIC,
                           request.req_type,
                           request.handle,
                           request.data_from,
                           request.data_length)
        if request.req_type == RequestType.NBD_CMD_WRITE:
            data = data + request.data
        self.sock.sendall(data)
