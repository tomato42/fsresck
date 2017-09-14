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
except ImportError:
    import unittest.mock as mock

import os
from itertools import chain

from fsresck.writesshuffler import WritesShuffler
from fsresck.image import Image
from fsresck.write import Write

class TestWritesShuffler(unittest.TestCase):
    def test___init__(self):
        ws = WritesShuffler(None, None)

        self.assertIsNotNone(ws)

    def test_generator(self):
        image = Image("/dev/null", [])
        # mock the object to not create an image copy
        image.create_image = lambda x: "/tmp/some-name"
        writes = [
            Write(offset=0, data=bytearray(512)),
            ]

        ws = WritesShuffler(image, writes)
        tests = list(ws.generator())
        self.assertEqual(len(tests), 2)
        self.assertEqual(len(tests[0]), 2)
        image, writes = tests[0]
        self.assertEqual(image.image_name, "/tmp/some-name")
        self.assertEqual(image.writes, [])
        self.assertEqual(writes, tuple())
        image, writes = tests[1]
        self.assertEqual(image.image_name, "/tmp/some-name")
        self.assertEqual(image.writes, [Write(offset=0, data=bytearray(512))])
        self.assertEqual(writes, tuple())

    def test_generator_with_invalid_data(self):
        ws = WritesShuffler(None, [])

        with self.assertRaises(TypeError):
            next(ws.generator())

        ws = WritesShuffler('/dev/null', None)

        with self.assertRaises(TypeError):
            next(ws.generator())

    def test_generator_with_many_writes(self):
        image = Image("/dev/null", [])
        # mock the object to not create an image copy
        image.create_image = lambda x: "/tmp/some-name"
        # writes need to overlap to create permutations instead of combinations
        writes = [
            Write(offset=0, data=bytearray(512)),
            Write(offset=1, data=bytearray(512)),
            Write(offset=2, data=bytearray(512)),
            Write(offset=3, data=bytearray(512))
            ]

        ws = WritesShuffler(image, writes)

        tests = list(ws.generator())

        self.assertEqual(len(tests), 27)
        self.assertEqual(len(tests[0]), 2)

        test_image, test_writes = tests[0]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, tuple())

        test_image, test_writes = tests[1]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[1], ))

        test_image, test_writes = tests[2]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[1], writes[0]))

        test_image, test_writes = tests[3]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[1], writes[0], writes[2]))

        test_image, test_writes = tests[4]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[1], writes[2]))

        test_image, test_writes = tests[5]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[1], writes[2], writes[0]))

        test_image, test_writes = tests[6]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[2], ))

        test_image, test_writes = tests[7]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[2], writes[0]))

        test_image, test_writes = tests[8]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[2], writes[0], writes[1]))

        test_image, test_writes = tests[9]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[2], writes[1]))

        test_image, test_writes = tests[10]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[2], writes[1], writes[0]))

        test_image, test_writes = tests[11]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, tuple())

        test_image, test_writes = tests[12]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[2], ))

        test_image, test_writes = tests[13]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[2], writes[1]))

        test_image, test_writes = tests[14]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[2], writes[1], writes[3]))

        test_image, test_writes = tests[15]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[2], writes[3]))

        test_image, test_writes = tests[16]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[2], writes[3], writes[1]))

        test_image, test_writes = tests[17]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[3], ))

        test_image, test_writes = tests[18]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[3], writes[1]))

        test_image, test_writes = tests[19]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[3], writes[1], writes[2]))

        test_image, test_writes = tests[20]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[3], writes[2]))

        test_image, test_writes = tests[21]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[3], writes[2], writes[1]))

        test_image, test_writes = tests[22]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0], writes[1]])
        self.assertEqual(test_writes, tuple())

        test_image, test_writes = tests[23]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0], writes[1]])
        self.assertEqual(test_writes, (writes[3], ))

        test_image, test_writes = tests[24]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0], writes[1]])
        self.assertEqual(test_writes, (writes[3], writes[2]))

        test_image, test_writes = tests[25]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0], writes[1], writes[2]])
        self.assertEqual(test_writes, tuple())

        test_image, test_writes = tests[26]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, writes)
        self.assertEqual(test_writes, tuple())

    def test_generator_with_large_amount_of_writes(self):
        image = Image("/dev/null", [])
        image.create_image = lambda x: "/tmp/some-name"
        writes = [Write(i, bytearray(512)) for i in range(20)]

        ws = WritesShuffler(image, writes)

        all_combinations = set()
        for test_image, test_writes in ws.generator():
            comb = tuple(chain(test_image.writes, test_writes))
            self.assertNotIn(comb, all_combinations)
            all_combinations.add(comb)
        self.assertIn(tuple(writes), all_combinations)

    def test_generator_with_larger_group_size(self):
        image = Image("/dev/null", [])
        image.create_image = lambda x: "/tmp/some-name"
        writes = [Write(i, bytearray(512)) for i in range(20)]

        ws = WritesShuffler(image, writes)

        all_combinations = set()
        for test_image, test_writes in ws.generator(5):
            comb = tuple(chain(test_image.writes, test_writes))
            self.assertNotIn(comb, all_combinations)
            all_combinations.add(comb)
        self.assertIn(tuple(writes), all_combinations)

    def test_generator_with_large_amount_of_non_overlapping_writes(self):
        image = Image("/dev/null", [])
        image.create_image = lambda x: "/tmp/some-name"
        writes = [Write(512*i, bytearray(512)) for i in range(20)]

        ws = WritesShuffler(image, writes)

        all_combinations = set()
        for test_image, test_writes in ws.generator():
            comb = frozenset(chain(test_image.writes, test_writes))
            self.assertNotIn(comb, all_combinations)
            all_combinations.add(comb)
        self.assertIn(frozenset(writes), all_combinations)

    def test_generator_with_non_overlapping_writes(self):
        image = Image("/dev/null", [])
        # mock the object to not create an image copy
        image.create_image = lambda x: "/tmp/some-name"
        writes = [
            Write(offset=0, data=bytearray(512)),
            Write(offset=512, data=bytearray(512)),
            Write(offset=1024, data=bytearray(512)),
            Write(offset=1536, data=bytearray(512))
            ]

        ws = WritesShuffler(image, writes)

        tests = list(ws.generator())

        # if the writes are non-overlapping we are expecting combinations
        # not permutations
        self.assertEqual(len(tests), 12)
        self.assertEqual(len(tests[0]), 2)

        test_image, test_writes = tests[0]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, tuple())

        test_image, test_writes = tests[1]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[1], ))

        test_image, test_writes = tests[2]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[1], writes[2]))

        test_image, test_writes = tests[3]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [])
        self.assertEqual(test_writes, (writes[2], ))

        test_image, test_writes = tests[4]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, tuple())

        test_image, test_writes = tests[5]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[2], ))

        test_image, test_writes = tests[6]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[2], writes[3]))

        test_image, test_writes = tests[7]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0]])
        self.assertEqual(test_writes, (writes[3], ))

        test_image, test_writes = tests[8]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0], writes[1]])
        self.assertEqual(test_writes, tuple())

        test_image, test_writes = tests[9]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0], writes[1]])
        self.assertEqual(test_writes, (writes[3], ))

        test_image, test_writes = tests[10]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, [writes[0], writes[1], writes[2]])
        self.assertEqual(test_writes, tuple())

        test_image, test_writes = tests[11]
        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(test_image.writes, writes)
        self.assertEqual(test_writes, tuple())

    def test_cleanup(self):
        patcher = mock.patch.object(os,
                                    'unlink',
                                    mock.MagicMock())
        os_unlink = patcher.start()
        self.addCleanup(patcher.stop)

        image = Image("/dev/null", [])

        def dumb_create_image(arg):
            image.temp_image_name = "/tmp/some-name"
            return image.temp_image_name
        image.create_image = mock.MagicMock(side_effect=dumb_create_image)

        writes = [
            Write(offset=0, data=bytearray(1)),
            Write(offset=1, data=bytearray(1)),
            Write(offset=2, data=bytearray(1))
            ]

        ws = WritesShuffler(image, writes)
        next(ws.generator())
        ws.cleanup()

        self.assertEqual(os_unlink.call_count, 1)
        self.assertEqual(os_unlink.call_args, mock.call("/tmp/some-name"))

    def test_shuffle_with_bad_image(self):
        ws = WritesShuffler(None, [])

        with self.assertRaises(TypeError):
            next(ws.shuffle())

    def test_shuffle_with_bad_writes(self):
        ws = WritesShuffler("/tmp/test", 22)

        with self.assertRaises(TypeError):
            next(ws.shuffle())

    def test_image_dir(self):
        image = Image("/dev/null", [])
        image.create_image = mock.MagicMock(return_value="/test/some-name")

        ws = WritesShuffler(image, [Write(offset=0, data=None)])
        ws.image_dir = "/test"

        test_image, test_writes = next(ws.generator())

        self.assertEqual(image.create_image.call_count, 1)
        self.assertEqual(image.create_image.call_args, mock.call("/test"))

        self.assertEqual(test_image.image_name, "/test/some-name")

    def test_shuffle(self):

        image = Image("/tmp/test", [])
        image.create_image = lambda x: "/tmp/some-name"

        writes = [
            Write(offset=0, data=bytearray(1)),
            Write(offset=1, data=bytearray(1)),
            Write(offset=2, data=bytearray(1)),
            ]
        ws = WritesShuffler(image, writes)

        test_image, test_writes = next(ws.shuffle())

        self.assertEqual(test_image.image_name, "/tmp/some-name")
        self.assertEqual(len(test_writes), 3)
        self.assertNotEqual(test_writes[0], writes[0])

    def test_shuffle_multiple_times(self):
        image = Image("/tmp/test", [])
        image.create_image = lambda x: "/tmp/some-name"

        writes = [
            Write(offset=0, data=bytearray(1)),
            Write(offset=1, data=bytearray(1)),
            ]
        ws = WritesShuffler(image, writes)

        for i in range(10):
            test_image, test_writes = next(ws.shuffle())
            self.assertNotEqual(test_writes[0], writes[0])
