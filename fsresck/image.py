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
"""Disk image handlers"""

import os
from . import utils

class Image(object):

    """
    Object for creating temporary copies of FS image with modifications

    Object for keeping disk image (in form of a file) together with writes
    to modify it, methods to apply those writes to temporary file and cleanup
    after the temporary file is no longer useful (or was modified).
    """

    def __init__(self, image_name, writes):
        """Combine disk file image with writes"""
        self.image_name = image_name
        self.writes = writes
        self.temp_image_name = None

    def __repr__(self):
        """Return human readable representation of object"""
        if self.temp_image_name is not None:
            return "Image(image_name={0!r}, writes=[])"\
                    .format(self.temp_image_name)
        return "Image(image_name={0!r}, writes={1!r})".format(self.image_name,
                                                              self.writes)

    def create_image(self, path):
        """
        Create temporary image file

        Copy the base image to temporary file in 'path', apply writes to it
        and return its name.
        """
        if self.temp_image_name is None:
            self.temp_image_name = utils.get_temp_file_name(path)

            utils.copy(self.image_name, self.temp_image_name)

            # apply writes to the copied image
            with open(self.temp_image_name, "w+b") as image:
                for write in self.writes:
                    image.seek(write.lba)
                    image.write(write.data)

        return self.temp_image_name

    def cleanup(self):
        """
        Remove temporary image file

        Remove the temporary image name, make it possible to create a new
        temporary copy with appplied writes
        """
        os.unlink(self.temp_image_name)
        self.temp_image_name = None
