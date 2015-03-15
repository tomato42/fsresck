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

from fsresck.write import Write
from fsresck.fragmenter import Fragmenter

class TestFragmenter(unittest.TestCase):
    def test___init__(self):
        fragmenter = Fragmenter()

        self.assertIsNotNone(fragmenter)

    def test_fragment(self):
        fragmenter = Fragmenter()

        writes = [
            Write(lba=0, data=bytearray(512))
            ]

        ret = [i for i in fragmenter.fragment(writes)]

        self.assertEqual([Write(lba=0, data=bytearray(512))],
                         ret)

    def test_fragment_with_long_data(self):
        fragmenter = Fragmenter()

        writes = [
            Write(lba=0, data=bytearray(1024))
            ]

        ret = [i for i in fragmenter.fragment(writes)]

        self.assertEqual(len(ret), 2)
        self.assertEqual(len(ret[0].data), 512)
        self.assertEqual(ret[0].lba, 0)
        self.assertEqual(len(ret[1].data), 512)
        self.assertEqual(ret[1].lba, 512)

    def test_fragment_with_non_aligned_data(self):
        fragmenter = Fragmenter()

        writes = [
            Write(lba=0, data=bytearray(1022))
            ]

        ret = [i for i in fragmenter.fragment(writes)]

        self.assertEqual(len(ret), 2)
        self.assertEqual(ret[0].data, bytearray(512))
        self.assertEqual(ret[0].lba, 0)
        self.assertEqual(ret[1].data, bytearray(510))
        self.assertEqual(ret[1].lba, 512)

    def test_fragment_with_non_standard_sector_size(self):
        fragmenter = Fragmenter(sector_size=1)

        writes = [
            Write(lba=0, data=bytearray(10))
            ]

        ret = [i for i in fragmenter.fragment(writes)]
        self.assertEqual(len(ret), 10)

        for write in fragmenter.fragment(writes):
            self.assertEqual(bytearray(1), write.data)

        self.assertEqual(9, ret[9].lba)

    def test_fragment_with_multiple_writes(self):
        fragmenter = Fragmenter()

        writes = [
            Write(lba=0, data=bytearray(1024)),
            Write(lba=65536, data=bytearray(2))
            ]

        ret = [i for i in fragmenter.fragment(writes)]

        self.assertEqual(len(ret), 3)
        self.assertEqual(ret[0].data, bytearray(512))
        self.assertEqual(ret[1].data, bytearray(512))
        self.assertEqual(ret[2].data, bytearray(2))
