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

from fsresck.nbd.request import NBDRequestSocket, recvexactly, Error, \
        NBDRequest
from fsresck.compat import compat_str


class TestError(unittest.TestCase):
    def test___repr__(self):
        with self.assertRaises(Error) as exception:
            raise Error('test')

        self.assertIn("request.Error('test'", repr(exception.exception))


class TestNBDRequest(unittest.TestCase):
    def test___init__(self):
        request = NBDRequest(None, None, None, None)
        self.assertIsNotNone(request)

    def test___ne__(self):
        request1 = NBDRequest(1, 2, 3, 4)
        request2 = NBDRequest(1, 2, 3, 4)

        self.assertFalse(request1 != request2)

class TestRecvexactly(unittest.TestCase):
    def test_zero_read(self):
        sock = None
        data = recvexactly(sock, 0)
        self.assertEqual(bytearray(0), data)

    def test_full_read(self):
        sock = mock.MagicMock()
        sock.recv_into.return_value = 10

        data = recvexactly(sock, 10)
        self.assertEqual(bytearray(10), data)
        sock.recv_into.assert_called_once_with(data, 10, 0)

    def test_partial_reads(self):
        sock = mock.MagicMock()
        sock.recv_into.side_effect = (4, 6)

        data = recvexactly(sock, 10)
        self.assertEqual(bytearray(10), data)
        self.assertEqual(len(sock.recv_into.call_args_list), 2)
        call = sock.recv_into.call_args_list[0]
        self.assertEqual(call[0][1:], (10, 0))
        call = sock.recv_into.call_args_list[1]
        self.assertEqual(call[0][1:], (6, 0))

    def test_broken_read(self):
        sock = mock.MagicMock()
        sock.recv_into.side_effect = (4, 0)

        with self.assertRaises(Error):
            recvexactly(sock, 10)


class TestNBDRequestSocket(unittest.TestCase):
    def test___init__(self):
        sock = NBDRequestSocket(None)
        self.assertIsNotNone(sock)

    @mock.patch('fsresck.nbd.request.recvexactly')
    def test_recv(self, mock_mthd):
        mock_mthd.return_value = bytearray(
                b'\x25\x60\x95\x13'   # magic value
                b'\x00\x00\x00\x00'   # command type - read
                b'\x50\xe4\x93\x01\x00\x88\xff\xff'  # handle
                b'\x00\x00\x00\x00\x00\x00\x00\x00'  # offset
                b'\x00\x00\x40\x00'  # length
                )

        obj = NBDRequestSocket(None).recv()

        self.assertEqual(NBDRequest(0, 0x50e493010088ffff, 0, 0x4000), obj)

    @mock.patch('fsresck.nbd.request.recvexactly')
    def test_recv_write(self, mock_mthd):
        mock_mthd.side_effect = (bytearray(
                b'\x25\x60\x95\x13'   # magic value
                b'\x00\x00\x00\x01'   # command type - write
                b'\x50\xe4\x93\x01\x00\x88\xff\xff'  # handle
                b'\x00\x00\x00\x00\x00\x00\x00\x00'  # offset
                b'\x00\x00\x00\x04'),  # length
                bytearray(
                b'\xff\xff\xff\xff'  # payload
                ))

        obj = NBDRequestSocket(None).recv()

        self.assertEqual(bytearray(b'\xff'*4), obj.data)
        self.assertEqual(NBDRequest(1, 0x50e493010088ffff, 0, 0x04,
                                    bytearray(b'\xff'*4)), obj)

    @mock.patch('fsresck.nbd.request.recvexactly')
    def test_recv_bad_write(self, mock_mthd):
        mock_mthd.return_value = bytearray(
                b'\x25\x60\x95\x14'   # bad magic value
                b'\x00\x00\x00\x00'   # command type - read
                b'\x50\xe4\x93\x01\x00\x88\xff\xff'  # handle
                b'\x00\x00\x00\x00\x00\x00\x00\x00'  # offset
                b'\x00\x00\x40\x00'  # length
                )

        sock = NBDRequestSocket(None)

        with self.assertRaises(Error):
            sock.recv()

    def test_send_read(self):
        raw_sock = mock.MagicMock()
        raw_sock.sendall.return_value = None

        cmd = NBDRequest(0, 0x134, 0, 0x4000)
        sock = NBDRequestSocket(raw_sock)
        sock.send(cmd)

        raw_sock.sendall.assert_called_once_with(compat_str(bytearray(
            b'\x25\x60\x95\x13'
            b'\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x014'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00@\x00')))

    def test_send_write(self):
        raw_sock = mock.MagicMock()
        raw_sock.sendall.return_value = None

        cmd = NBDRequest(1, 0x134, 0, 0x04, bytearray(b'\xff'*4))
        sock = NBDRequestSocket(raw_sock)
        sock.send(cmd)

        raw_sock.sendall.assert_called_once_with(compat_str(bytearray(
            b'\x25\x60\x95\x13'
            b'\x00\x00\x00\x01'
            b'\x00\x00\x00\x00\x00\x00\x014'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x04'
            b'\xff\xff\xff\xff')))
