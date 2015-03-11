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

import os
import tempfile
import subprocess
from fsresck.image import Image
from fsresck.write import Write

class TestImage(unittest.TestCase):
    def test___init__(self):
        image = Image(None, None)

        self.assertIsNotNone(image)

    def test___repr__(self):
        image = Image("/tmp/test.1", [Write(lba=4, data='aa')])

        self.assertEqual("Image(image_name='/tmp/test.1', "\
                         "writes=[<Write lba=4, "\
                         "len(data)=2>])", repr(image))

    def test___repr___adter_create_image(self):
        image = Image("/tmp/test.1", [Write(lba=4, data='aa')])
        image.temp_image_name = '/tmp/test.2'

        self.assertEqual("Image(image_name='/tmp/test.2', writes=[])",
                         repr(image))

    def test_create_image_and_cleanup(self):
        image = Image("/tmp/test.1", [Write(lba=4, data='aa')])

        # mock setup
        patcher = mock.patch.object(builtins,
                                    'open',
                                    mock.mock_open())
        mock_open = patcher.start()
        self.addCleanup(patcher.stop)

        mkstemp = mock.create_autospec(tempfile.mkstemp)
        mkstemp.return_value = (-33, '/tmp/fsresck.xxxx')
        
        patcher = mock.patch.object(tempfile,
                                    'mkstemp',
                                    mkstemp)
        mock_mkstemp = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(os,
                                    'close',
                                    mock.create_autospec(os.close))
        mock_close = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(subprocess,
                                    'call',
                                    mock.create_autospec(os.close,
                                                         return_value=0))
        mock_call = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(os,
                                    'unlink',
                                    mock.create_autospec(os.unlink))
        mock_unlink = patcher.start()
        self.addCleanup(patcher.stop)
                                                        
        # test
        image_name = image.create_image('/tmp')
        self.assertEqual('/tmp/fsresck.xxxx', image_name)
        
        image.cleanup()

        self.assertEqual(None, image.temp_image_name)

        # mock asserts
        self.assertEqual(mock_open.call_count, 1)
        self.assertEqual(mock_open.call_args, mock.call('/tmp/fsresck.xxxx',
                                                        'w+b'))
        handle = mock_open()
        self.assertEqual(handle.seek.call_args, mock.call(4))
        self.assertEqual(handle.write.call_args, mock.call('aa'))

        self.assertEqual(mock_mkstemp.call_count, 1)
        self.assertEqual(mock_mkstemp.call_args, mock.call(prefix='fsresck.',
                                                           dir='/tmp'))

        self.assertEqual(mock_close.call_count, 1)
        self.assertEqual(mock_close.call_args, mock.call(-33))

        self.assertEqual(mock_call.call_count, 1)
        self.assertEqual(mock_call.call_args, mock.call(['cp',
                                                         '--reflink=auto',
                                                         '--sparse=always',
                                                         '/tmp/test.1',
                                                         '/tmp/fsresck.xxxx']))

        self.assertEqual(mock_unlink.call_count, 1)
        self.assertEqual(mock_unlink.call_args, mock.call('/tmp/fsresck.xxxx'))
