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

"""Slicing log files for tests"""

import struct
from collections import deque
from itertools import islice
from .image import Image
from .write import Write
from .errors import TruncatedFileError

class LogHeader(object):

    """
    Handler for write headers in log files

    Reads the following fields in big-endian format:
    32bit unsigned int - operation type (only "1" supported - write),
    double precision floating point number - start time in seconds from epoch,
    double precision floating point number - end time in seconds from epoch,
    64bit unsigned integer - disk offset in bytes
    32bit unsigned integer - length of data payload
    """

    header_format = '!IddQi'
    header_length = struct.calcsize(header_format)

    def __init__(self):
        """init"""
        self.operation = 0
        self.start_time = 0.0
        self.end_time = 0.0
        self.offset = 0
        self.length = 0

    def parse(self, data):
        """Parse object from bytearray"""
        operation, start_time, end_time, offset, length = struct.unpack(
            self.header_format, data)

        assert operation in (1, 0)

        self.operation = operation
        self.start_time = start_time
        self.end_time = end_time
        self.offset = offset
        self.length = length

        return self

class LogReader(object):

    """Parser for log files"""

    def __init__(self, log_name):
        """Open log file"""
        self.log_name = log_name

    @staticmethod
    def _read_exact(handle, length):
        """Read exact amount of data from file, fail if unavailable"""
        data = handle.read(length)
        if len(data) == 0:
            raise EOFError("End of file reached")
        if len(data) != length:
            raise TruncatedFileError("truncated file")
        return data

    def reader(self):
        """Generator for reads in file"""
        with open(self.log_name, 'r+b') as log:
            while True:
                try:
                    header_data = self._read_exact(log, LogHeader.header_length)
                except EOFError:
                    break

                header = LogHeader().parse(header_data)

                data = self._read_exact(log, header.length)

                write = Write(lba=header.offset, data=data)
                write.set_times(header.start_time, header.end_time)

                yield write

class BaseImageGenerator(object):

    """
    Generator for pairs of images and writes to test

    Tests ops_to_test at a time by default
    """

    def __init__(self, image_name, log_name):
        """Provide name of image file and writes log"""
        self.image_name = image_name
        self.log_name = log_name
        self.ops_to_test = 5

    def generate(self):
        """Create tuples of Image and writes to test"""
        write_log = LogReader(self.log_name)
        log_reader = write_log.reader()

        writes = islice(log_reader, self.ops_to_test)
        writes = deque(writes)

        image_writes = deque()

        yield (Image(self.image_name, list(image_writes)), list(writes))

        # exhaust log_reader
        for write in log_reader:
            image_writes.append(writes.popleft())
            writes.append(write)
            yield (Image(self.image_name, list(image_writes)), list(writes))

        while len(writes) > 0:
            image_writes.append(writes.popleft())
            yield (Image(self.image_name, list(image_writes)), list(writes))
