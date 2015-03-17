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

import sys
if sys.version_info[0] == 2:
    import __builtin__ as builtins
else:
    import builtins

import io
from fsresck.imagegenerator import BaseImageGenerator, LogReader, LogHeader
from fsresck.write import Write
from fsresck.errors import TruncatedFileError

class TestBaseImageGenerator(unittest.TestCase):
    def test___init__(self):
        generator = BaseImageGenerator("aaa", "bbb")

        self.assertEqual(generator.image_name, "aaa")
        self.assertEqual(generator.log_name, "bbb")
        self.assertEqual(generator.ops_to_test, 5)

    def test_generate(self):
        writes = []

        patcher = mock.patch.object(LogReader,
                                    'reader',
                                    mock.Mock(return_value=iter(writes)))
        mock_reader = patcher.start()
        self.addCleanup(patcher.stop)

        generator = BaseImageGenerator("aaa", "bbb")

        image_pairs = list(generator.generate())

        self.assertEqual(len(image_pairs), 1)
        image, test_writes = image_pairs[0]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [])
        self.assertEqual(test_writes, [])

    def test_generate_with_one_write(self):
        writes = [Write(lba=0, data=bytearray(10))]

        patcher = mock.patch.object(LogReader,
                                    'reader',
                                    mock.Mock(return_value=iter(writes)))
        mock_reader = patcher.start()
        self.addCleanup(patcher.stop)

        generator = BaseImageGenerator("aaa", "bbb")
        generator.ops_to_test = 1

        image_pairs = list(generator.generate())

        self.assertEqual(len(image_pairs), 2)

        image, test_writes = image_pairs[0]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [])
        self.assertEqual(test_writes, [writes[0]])

        image, test_writes = image_pairs[1]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [writes[0]])
        self.assertEqual(test_writes, [])

    def test_generate_with_two_write(self):
        writes = [Write(lba=0, data=bytearray(10)),
                  Write(lba=512, data=bytearray(10))]

        patcher = mock.patch.object(LogReader,
                                    'reader',
                                    mock.Mock(return_value=iter(writes)))
        mock_reader = patcher.start()
        self.addCleanup(patcher.stop)

        generator = BaseImageGenerator("aaa", "bbb")
        generator.ops_to_test = 1

        image_pairs = list(generator.generate())

        self.assertEqual(len(image_pairs), 3)

        image, test_writes = image_pairs[0]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [])
        self.assertEqual(test_writes, [writes[0]])

        image, test_writes = image_pairs[1]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [writes[0]])
        self.assertEqual(test_writes, [writes[1]])

        image, test_writes = image_pairs[2]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [writes[0], writes[1]])
        self.assertEqual(test_writes, [])

    def test_generate_with_five_writes(self):
        writes = [Write(lba=0, data=bytearray(10)),
                  Write(lba=512, data=bytearray(10)),
                  Write(lba=1024, data=bytearray(10)),
                  Write(lba=1536, data=bytearray(10)),
                  Write(lba=2048, data=bytearray(10))]

        patcher = mock.patch.object(LogReader,
                                    'reader',
                                    mock.Mock(return_value=iter(writes)))
        mock_reader = patcher.start()
        self.addCleanup(patcher.stop)

        generator = BaseImageGenerator("aaa", "bbb")
        generator.ops_to_test = 2

        image_pairs = list(generator.generate())

        self.assertEqual(len(image_pairs), 6)

        image, test_writes = image_pairs[0]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [])
        self.assertEqual(test_writes, [writes[0], writes[1]])

        image, test_writes = image_pairs[1]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [writes[0]])
        self.assertEqual(test_writes, [writes[1], writes[2]])

        image, test_writes = image_pairs[2]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [writes[0], writes[1]])
        self.assertEqual(test_writes, [writes[2], writes[3]])

        image, test_writes = image_pairs[3]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [writes[0], writes[1], writes[2]])
        self.assertEqual(test_writes, [writes[3], writes[4]])

        image, test_writes = image_pairs[4]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [writes[0], writes[1], writes[2],
                                        writes[3]])
        self.assertEqual(test_writes, [writes[4]])

        image, test_writes = image_pairs[5]
        self.assertEqual(image.image_name, "aaa")
        self.assertEqual(image.writes, [writes[0], writes[1], writes[2],
                                        writes[3], writes[4]])
        self.assertEqual(test_writes, [])

class TestLogReader(unittest.TestCase):
    def test___init__(self):
        log_reader = LogReader('/tmp/log')

        self.assertEqual(log_reader.log_name, '/tmp/log')

    def test_reader(self):
        log_reader = LogReader('/tmp/log')

        log = (\
            b'\x00'*3 + b'\x01' +           # write operation
            b'\x00'*8 +                     # start_time = 0
            b'\x00'*8 +                     # end_time = 0
            b'\x00'*8 +                     # offset = 0
            b'\x00'*3 + b'\x0a' +           # length = 10 bytes
            b'\x01'*10                      # data
            )

        open_mock = mock.MagicMock(return_value=io.BytesIO(log))
        patcher = mock.patch.object(builtins,
                                    'open',
                                    open_mock)
        mock_open = patcher.start()
        self.addCleanup(patcher.stop)

        writes = list(log_reader.reader())

        write = Write(lba=0, data=bytearray(b'\x01'*10))
        write.set_times(0.0, 0.0)
        self.assertEqual(writes, [write])

    def test_reader_with_truncated_file(self):
        log_reader = LogReader('/tmp/log')

        log = (\
            b'\x00'*3 + b'\x01' +           # write operation
            b'\x00'*8 +                     # start_time = 0
            b'\x00'*8 +                     # end_time = 0
            b'\x00'*8 +                     # offset = 0
            b'\x00'*3 + b'\x0a' +           # length = 10 bytes
            b'\x01'*9                       # data
            )

        if sys.version_info[0] == 2:
            log = str(log)

        open_mock = mock.MagicMock(return_value=io.BytesIO(log))
        patcher = mock.patch.object(builtins,
                                    'open',
                                    open_mock)
        mock_open = patcher.start()
        self.addCleanup(patcher.stop)

        with self.assertRaises(TruncatedFileError):
            next(log_reader.reader())

class TestLogHeader(unittest.TestCase):
    def test___init__(self):
        header = LogHeader()

        self.assertEqual(header.operation, 0)
        self.assertEqual(header.start_time, 0.0)
        self.assertEqual(header.end_time, 0.0)
        self.assertEqual(header.offset, 0)
        self.assertEqual(header.length, 0)

    def test_write(self):
        header = LogHeader()

        header.operation = 1
        header.offset = 512
        header.length = 1024

        self.assertEqual(\
                b'\x00'*3 + b'\x01' +       # operation
                b'\x00'*8 +                 # start_time
                b'\x00'*8 +                 # end_time
                b'\x00'*6 + b'\x02\x00' +   # offset
                b'\x00'*2 + b'\x04\x00'
                , header.write())
