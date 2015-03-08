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

from fsresck.write import Write

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
        self.assertEqual(0, write.lba)
        self.assertEqual(bytearray(512), write.data)
        self.assertEqual(None, write.disk_id)
        self.assertEqual(None, write.start_time)
        self.assertEqual(None, write.end_time)

    def test___eq__(self):
        write1 = Write(None, None)
        write2 = Write(None, None)

        self.assertEqual(write1, write2)

    def test___eq___with_different_writes(self):
        write1 = Write(0, bytearray(512))
        write2 = Write(0, bytearray(1024))

        self.assertNotEqual(write1, write2)

    def test___eq__with_non_Write_other(self):
        write1 = Write(0, bytearray(512))
        write2 = None

        self.assertNotEqual(write1, write2)

    def test___str__(self):
        write = Write(lba=512, data=bytearray(65536))

        self.assertEqual("<Write lba=512, len(data)=65536, disk_id=None, "\
                         "start_time=None, end_time=None>",
                         str(write))
