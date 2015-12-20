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

"""Python 2 and Python 3 compatibility."""

import sys


if sys.version_info >= (3, 0):
    def compat_str(byte_array):
        """
        Python 2 and 3 converter for bytearrays.

        Provides strings in Python 2 and bytes in Python 3, so that socket
        can handle the inputs
        """
        return bytes(byte_array)

else:
    def compat_str(byte_array):
        """
        Python 2 and 3 converter for bytearrays.

        Provides strings in Python 2 and bytes in Python 3, so that socket
        can handle the inputs
        """
        return str(byte_array)
