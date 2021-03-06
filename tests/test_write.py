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

from fsresck.write import Write, overlapping

class TestWrite(unittest.TestCase):
    def test___init__(self):
        write = Write(None, None, None)

        self.assertIsNotNone(write)

    def test___init___with_min_options(self):
        write = Write(None, None)

        self.assertIsNotNone(write)

    def test___init___with_real_data(self):
        write = Write(0, bytearray(512))

        self.assertIsNotNone(write)
        self.assertEqual(0, write.offset)
        self.assertEqual(bytearray(512), write.data)
        self.assertEqual(None, write.disk_id)
        self.assertEqual(None, write.start_time)
        self.assertEqual(None, write.end_time)

    def test___eq__(self):
        write1 = Write(None, None)
        write2 = Write(None, None)

        self.assertTrue(write1 == write2)

    def test___eq___with_different_writes(self):
        write1 = Write(0, bytearray(512))
        write2 = Write(0, bytearray(1024))

        self.assertFalse(write1 == write2)

    def test___ne__(self):
        write1 = Write(0, bytearray(512))
        write2 = Write(0, bytearray(512))

        self.assertFalse(write1 != write2)

    def test___eq__with_non_Write_other(self):
        write1 = Write(0, bytearray(512))
        write2 = None

        self.assertFalse(write1 == write2)

    def test___str__(self):
        write = Write(offset=512, data=bytearray(65536), disk_id=1234)
        write.set_times(33, 22)

        self.assertEqual("<Write offset=512, len(data)=65536, disk_id=1234, "
                         "start_time=33, end_time=22>",
                         str(write))

    def test___repr___with_just_offset_and_data(self):
        write = Write(offset=512, data=bytearray(1024))

        self.assertEqual("<Write offset=512, len(data)=1024>", repr(write))

    def test___repr___with_just_offset_data_and_disk_id(self):
        write = Write(offset=1, data=bytearray(2), disk_id=3)

        self.assertEqual("<Write offset=1, len(data)=2, disk_id=3>",
                         repr(write))

    def test_set_times(self):
        write = Write(offset=0, data=bytearray(65536))

        write.set_times(12, 14)

        self.assertEqual(write.start_time, 12)
        self.assertEqual(write.end_time, 14)

class TestOverlapping(unittest.TestCase):
    def test_non_overlapping(self):
        writes = [Write(offset=0, data=bytearray(512)),
                  Write(offset=512, data=bytearray(512)),
                  Write(offset=1024, data=bytearray(512))]

        self.assertFalse(overlapping(writes))

    def test_overlapping_second_beginning(self):
        writes = [Write(offset=512, data=bytearray(512)),
                  Write(offset=1023, data=bytearray(512))]

        self.assertTrue(overlapping(writes))

    def test_overlapping_second_end(self):
        writes = [Write(offset=512, data=bytearray(512)),
                  Write(offset=0, data=bytearray(513))]

        self.assertTrue(overlapping(writes))

    def test_overlapping_first_beginning(self):
        writes = [Write(offset=1023, data=bytearray(512)),
                  Write(offset=512, data=bytearray(512))]

        self.assertTrue(overlapping(writes))

    def test_overlapping_first_end(self):
        writes = [Write(offset=0, data=bytearray(513)),
                  Write(offset=512, data=bytearray(512))]

        self.assertTrue(overlapping(writes))

    def test_overlapping_different_disks(self):
        writes = [Write(0, bytearray(512), disk_id=1),
                  Write(0, bytearray(512), disk_id=2)]

        self.assertFalse(overlapping(writes))

    def test_non_overlapping_different_disks(self):
        writes = [Write(0, bytearray(512), disk_id=1),
                  Write(512, bytearray(512), disk_id=2)]

        self.assertFalse(overlapping(writes))
