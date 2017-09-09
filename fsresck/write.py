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
"""Handling of image modification requests (writes)."""


def overlapping(iterator):
    """Check if the writes in iterator are not overlapping each other."""
    writes = list(iterator)

    for i, write in enumerate(writes):
        for other_write in writes[i+1:]:
            write_start = write.offset
            write_end = write.offset + len(write.data)
            other_write_start = other_write.offset
            other_write_end = other_write.offset + len(other_write.data)

            if other_write_start < write_end < other_write_end:
                return True
            if other_write_start <= write_start < other_write_end:
                return True
    return False


class Write(object):

    """Single image modification request."""

    def __init__(self, offset, data, disk_id=None):
        """
        Create an object instance.

        @type offset: int
        @param offset: the start place for the write modification request
        @type data: bytearray
        @param data: data to write at L{offset}
        @param disk_id: base image disk UUID
        """
        self.offset = offset
        self.data = data
        self.disk_id = disk_id
        self.start_time = None
        self.end_time = None

    def __repr__(self):
        """Return human-readable representation of the object."""
        if self.disk_id is None and self.start_time is None and \
                self.end_time is None:
            return "<Write offset={0}, len(data)={1}>".format(
                self.offset, len(self.data))
        elif self.start_time is None and self.end_time is None:
            return "<Write offset={0}, len(data)={1}, disk_id={2}>".format(
                self.offset, len(self.data), self.disk_id)
        else:
            return "<Write offset={0}, len(data)={1}, disk_id={2}, "\
                   "start_time={3}, end_time={4}>".format(
                       self.offset, len(self.data), self.disk_id,
                       self.start_time, self.end_time)

    def set_times(self, start_time, end_time):
        """Add the issuence time and completion time of original operation."""
        self.start_time = start_time
        self.end_time = end_time

    def __eq__(self, other):
        """
        Check if objects are identical.

        Compare the object with another to check if it represents the
        same modification.
        """
        return (isinstance(other, Write) and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        """
        Check if objects are different.

        Compare the object with another to check if they are different
        """
        return not self.__eq__(other)
