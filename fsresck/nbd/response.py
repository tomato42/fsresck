# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Description: File system resilience testing application
#   Author: Hubert Kario <hubert@kario.pl>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2017 Hubert Kario. All rights reserved.
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

"""Handling of NBD replies."""

import struct
from .request import recvexactly
from ..compat import compat_str
from .constants import Magic
from ..errors import FSError

class NBDResponse(object):
    """Representation of a single NBD protocol response."""

    def __init__(self, error, handle):
        """Initialise NBD response."""
        self.error = error
        self.handle = handle
        self.data = None


class NBDResponseSocket(object):
    """Handle NBD responses on NBD socket."""

    response_fmt = ">IIQ"
    response_length = struct.calcsize(response_fmt)

    def __init__(self, sock_in, sock_out, len_dict):
        """
        Initialise the object

        :param sock_in: socket to read messages from
        :param sock_out: socket to write messages to
        :param len_dict: shared dictionary for keeping the expected lengths
            of responses
        """
        self.sock_in = sock_in
        self.sock_out = sock_out
        self.len_dict = len_dict

    def recv(self):
        """Read a single response from socket."""
        header = recvexactly(self.sock_in, self.response_length)
        assert len(header) == self.response_length
        header = compat_str(header)
        result_tuple = struct.unpack(self.response_fmt, header)
        magic, error, handle = result_tuple

        if magic != Magic.NBD_REPLY_MAGIC:
            raise FSError("Response magic invalid: {0}".format(magic))

        if error != 0:
            # TODO
            raise FSError("Received error response, don't know how to handle")

        data_len = self.len_dict.pop(handle)
        data = recvexactly(self.sock_in, data_len)

        resp = NBDResponse(error, handle)
        resp.data = data

        return resp

    def send(self, resp):
        data = struct.pack(self.response_fmt,
                           Magic.NBD_REPLY_MAGIC,
                           resp.error,
                           resp.handle)
        if resp.data:
            data += resp.data
        self.sock_out.sendall(data)
