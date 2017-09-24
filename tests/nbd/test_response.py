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

# compatibility with Python 2.6, for that we need unittest2 package,
# which is not available on 3.3 or 3.4
try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    import mock
    from mock import call
except ImportError:
    import unittest.mock as mock
    from unittest.mock import call


from fsresck.nbd.response import NBDResponseSocket, NBDResponse
from fsresck.errors import FSError

class TestNBDResponseSocket(unittest.TestCase):
    def test___init__(self):
        obj = NBDResponseSocket(None, None, None)

        self.assertIsInstance(obj, NBDResponseSocket)

    @mock.patch('fsresck.nbd.response.recvexactly')
    def test_recv(self, mock_mthd):
        mock_mthd.side_effect = [bytearray(
                b'\x67\x44\x66\x98'  # magic value
                b'\x00\x00\x00\x00'  # error - none
                b'\x50\xe4\x93\x01\x00\x88\xff\xff'),  # handle
                bytearray(b'\x00' * 4096)]
        d = dict()
        d[0x50e493010088ffff] = 4096

        obj = NBDResponseSocket(None, None, d).recv()

        self.assertEqual(obj.handle, 0x50e493010088ffff)
        self.assertEqual(obj.error, 0)
        self.assertEqual(obj.data, bytearray(b'\x00' * 4096))
        self.assertEqual(len(d), 0)

    @mock.patch('fsresck.nbd.response.recvexactly')
    def test_recv_with_invalid_magic(self, mock_mthd):
        mock_mthd.side_effect = [bytearray(
                b'\xff\xff\x66\x98'  # magic value
                b'\x00\x00\x00\x00'  # error - none
                b'\x50\xe4\x93\x01\x00\x88\xff\xff'),  # handle
                bytearray(b'\x00' * 4096)]
        d = dict()
        d[0x50e493010088ffff] = 4096

        sock = NBDResponseSocket(None, None, d)

        with self.assertRaises(FSError):
            sock.recv()

    @mock.patch('fsresck.nbd.response.recvexactly')
    def test_recv_with_error(self, mock_mthd):
        mock_mthd.side_effect = [bytearray(
                b'\x67\x44\x66\x98'  # magic value
                b'\x00\x00\x00\x01'  # error - none
                b'\x50\xe4\x93\x01\x00\x88\xff\xff'),  # handle
                bytearray(b'\x00' * 4096)]
        d = dict()
        d[0x50e493010088ffff] = 4096

        sock = NBDResponseSocket(None, None, d)

        with self.assertRaises(FSError):
            sock.recv()

    def test_send(self):
        sock_out = mock.MagicMock()

        sock = NBDResponseSocket(None, sock_out, None)

        response = NBDResponse(0, 44)
        response.data = bytearray(b'\x00' * 1024)

        sock.send(response)

        sock_out.sendall.assert_called_with(bytearray(b'\x67\x44\x66\x98'
                                                      b'\x00\x00\x00\x00'
                                                      b'\x00\x00\x00\x00'
                                                      b'\x00\x00\x00\x2c' +
                                                      b'\x00' * 1024))
    def test_send_without_data(self):
        sock_out = mock.MagicMock()

        sock = NBDResponseSocket(None, sock_out, None)

        response = NBDResponse(0, 45)

        sock.send(response)

        sock_out.sendall.assert_called_with(bytearray(b'\x67\x44\x66\x98'
                                                      b'\x00\x00\x00\x00'
                                                      b'\x00\x00\x00\x00'
                                                      b'\x00\x00\x00\x2d'))
