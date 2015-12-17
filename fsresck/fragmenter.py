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

"""Methods to fragment list of writes."""

from .write import Write


class Fragmenter(object):

    """Object for fragmenting a list of writes further."""

    def __init__(self, sector_size=512):
        """
        Create an object.

        @param sector_size: maximum size of the generated fragments
        """
        self.sector_size = sector_size

    def fragment(self, writes):
        """
        Return a generator with fragmented Write objects from passed writes.

        @param writes: list of Write objects
        """
        for write in writes:
            data = write.data
            lba = write.lba
            while data:
                ret = Write(lba, data[:self.sector_size])
                lba += len(ret.data)
                data = data[self.sector_size:]
                yield ret
