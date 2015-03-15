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

from collections import deque
from itertools import islice
from .image import Image

class LogReader(object):

    """Parser for log files"""

    def __init__(self, log_name):
        """Open log file"""
        self.log_name = log_name

    def reader(self):
        """Generator for reads in file"""
        raise NotImplementedError()

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
