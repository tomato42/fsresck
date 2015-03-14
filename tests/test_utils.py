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

import subprocess
import tempfile
import os
from fsresck.utils import copy, get_temp_file_name
from fsresck.errors import FSCopyError

class TestCopy(unittest.TestCase):
    def test_copy_with_error(self):

        patcher = mock.patch.object(subprocess,
                                    'call',
                                    mock.MagicMock(return_value=3))
        mock_call = patcher.start()
        self.addCleanup(patcher.stop)

        with self.assertRaises(FSCopyError):
            copy("file-A", "file-B")

    def test_copy(self):
        patcher = mock.patch.object(subprocess,
                                    'call',
                                    mock.MagicMock(return_value=0))
        mock_call = patcher.start()
        self.addCleanup(patcher.stop)

        copy("file-A", "file-B")

        self.assertEqual(1, mock_call.call_count)
        self.assertEqual("file-A", mock_call.call_args[0][0][-2])
        self.assertEqual("file-B", mock_call.call_args[0][0][-1])

    def test_get_temp_file_name(self):
        patcher = mock.patch.object(tempfile,
                                    'mkstemp',
                                    mock.MagicMock(return_value=(-33, "name3")))
        mock_mkstemp = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(os,
                                    'close',
                                    mock.MagicMock())
        mock_close = patcher.start()
        self.addCleanup(patcher.stop)

        name = get_temp_file_name('/dir-name')

        self.assertEqual(name, "name3")

        mock_mkstemp.assert_called_once_with(prefix='fsresck.', dir='/dir-name')
        mock_close.assert_called_once_with(-33)
