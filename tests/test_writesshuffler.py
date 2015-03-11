#!/usr/bin/python
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Description: File system resilience testing application
#   Author: Hubert Kario <hkario@redhat.com>
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
        image.create_image = lambda x: "/dev/null"
        writes = [
            Write(lba=0, data=bytearray(512)),
            ]

        ws = WritesShuffler(image, writes)
        tests = [i for i in ws.generator()]
        self.assertEqual(len(tests), 1)
        self.assertEqual(len(tests[0]), 2)
        image, writes = tests[0]
        # XXX this should be random name in directory specified in
        # WritesShuffler generator
        self.assertEqual(image.image_name, "/dev/null")
        self.assertEqual(image.writes, [])
        self.assertEqual(writes, [])

    def test_generator_with_invalid_data(self):
        ws = WritesShuffler(None, None)

        with self.assertRaises(TypeError):
            next(ws.generator())

    def test_generator_with_many_writes(self):
        image = Image("/dev/null", [])
        # mock the object to not create an image copy
        image.create_image = lambda x: "/dev/null"
        writes = [
            Write(lba=0, data=bytearray(512)),
            Write(lba=512, data=bytearray(512)),
            Write(lba=1024, data=bytearray(512)),
            ]

        ws = WritesShuffler(image, writes)
        tests = [i for i in ws.generator()]
        self.assertEqual(len(tests), 3)
        self.assertEqual(len(tests[0]), 2)
        image, writes = tests[0]
        # XXX this should be random name in directory specified in
        # WritesShuffler generator
        self.assertEqual(image.image_name, "/dev/null")
        self.maxDiff = None
        # XXX verify the writes are corrct sizes
