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

import os
import tempfile
import subprocess
from fsresck.image import Image
from fsresck.write import Write
from fsresck.errors import FSCopyError

class TestImage(unittest.TestCase):
    def test___init__(self):
        image = Image(None, None)

        self.assertIsNotNone(image)

    def test___repr__(self):
        image = Image("/tmp/test.1", [Write(offset=4, data='aa')])

        self.assertEqual("Image(image_name='/tmp/test.1', "\
                         "writes=[<Write offset=4, "\
                         "len(data)=2>])", repr(image))

    def test___repr___adter_create_image(self):
        image = Image("/tmp/test.1", [Write(offset=4, data='aa')])
        image.temp_image_name = '/tmp/test.2'

        self.assertEqual("Image(image_name='/tmp/test.2', writes=[])",
                         repr(image))

    def test_create_image_and_cleanup(self):
        image = Image("/tmp/test.1", [Write(offset=4, data='aa')])

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
                                    mock.MagicMock())
        mock_close = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(subprocess,
                                    'call',
                                    mock.create_autospec(subprocess.call,
                                                         return_value=0))
        mock_call = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(os,
                                    'unlink',
                                    mock.MagicMock())
        mock_unlink = patcher.start()
        self.addCleanup(patcher.stop)

        # test
        image_name = image.create_image('/tmp')

        self.assertEqual('/tmp/fsresck.xxxx', image_name)
        self.assertEqual(image_name, image.create_image("/tmp"))

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
                                                         '--sparse=auto',
                                                         '/tmp/test.1',
                                                         '/tmp/fsresck.xxxx']))

        self.assertEqual(mock_unlink.call_count, 1)
        self.assertEqual(mock_unlink.call_args, mock.call('/tmp/fsresck.xxxx'))

    def test_create_image_with_failed_copy(self):
        image = Image("/tmp/test.1", [Write(offset=4, data='aa')])

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
                                    mock.MagicMock())
        mock_close = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(subprocess,
                                    'call',
                                    mock.create_autospec(subprocess.call,
                                                         return_value=1))
        mock_call = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(os,
                                    'unlink',
                                    mock.MagicMock())
        mock_unlink = patcher.start()
        self.addCleanup(patcher.stop)

        # test
        with self.assertRaises(FSCopyError):
            image.create_image('/tmp')

        # mock asserts
        self.assertEqual(mock_open.call_count, 0)

        self.assertEqual(mock_mkstemp.call_count, 1)
        self.assertEqual(mock_mkstemp.call_args, mock.call(prefix='fsresck.',
                                                           dir='/tmp'))

        self.assertEqual(mock_close.call_count, 1)
        self.assertEqual(mock_close.call_args, mock.call(-33))

        self.assertEqual(mock_call.call_count, 1)
        self.assertEqual(mock_call.call_args, mock.call(['cp',
                                                         '--reflink=auto',
                                                         '--sparse=auto',
                                                         '/tmp/test.1',
                                                         '/tmp/fsresck.xxxx']))

        self.assertEqual(mock_unlink.call_count, 0)

    def test_create_image_twice(self):
        image = Image("/tmp/test.1", [Write(offset=4, data='aa')])

        # mock setup
        patcher = mock.patch.object(builtins,
                                    'open',
                                    mock.mock_open())
        mock_open = patcher.start()
        open_patcher = patcher

        mkstemp = mock.create_autospec(tempfile.mkstemp)
        mkstemp.return_value = (-33, '/tmp/fsresck.xxxx')

        patcher = mock.patch.object(tempfile,
                                    'mkstemp',
                                    mkstemp)
        mock_mkstemp = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(os,
                                    'close',
                                    mock.MagicMock())
        mock_close = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(subprocess,
                                    'call',
                                    mock.create_autospec(subprocess.call,
                                                         return_value=0))
        mock_call = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(os,
                                    'unlink',
                                    mock.MagicMock())
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
                                                         '--sparse=auto',
                                                         '/tmp/test.1',
                                                         '/tmp/fsresck.xxxx']))

        self.assertEqual(mock_unlink.call_count, 1)
        self.assertEqual(mock_unlink.call_args, mock.call('/tmp/fsresck.xxxx'))

        # make space for second run
        open_patcher.stop()
        patcher = mock.patch.object(builtins,
                                    'open',
                                    mock.mock_open())
        mock_open = patcher.start()
        self.addCleanup(patcher.stop)

        mock_mkstemp.reset_mock()
        mock_close.reset_mock()
        mock_call.reset_mock()
        mock_unlink.reset_mock()

        # change temporary file name
        mock_mkstemp.return_value = (-33, '/tmp/fsresck.yyyy')

        # test
        image_name = image.create_image('/tmp')

        self.assertEqual('/tmp/fsresck.yyyy', image_name)

        image.cleanup()

        # check if the second run creates the file with same contents
        # the second run is to get "handle"
        self.assertEqual(mock_open.call_count, 1)
        self.assertEqual(mock_open.call_args, mock.call('/tmp/fsresck.yyyy',
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
                                                         '--sparse=auto',
                                                         '/tmp/test.1',
                                                         '/tmp/fsresck.yyyy']))

        self.assertEqual(mock_unlink.call_count, 1)
        self.assertEqual(mock_unlink.call_args, mock.call('/tmp/fsresck.yyyy'))
