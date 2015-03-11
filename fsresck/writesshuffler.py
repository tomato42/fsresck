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

from .image import Image

import random

class WritesShuffler(object):
    def __init__(self, base_image, writes):
        self.base_image = base_image
        self.writes = writes

    def generator(self):
        """
        Iterator that returns pairs of images and logs of writes that are
        shuffled in a way that makes them unique
        """
        if self.base_image is None:
            raise TypeError("base_image can't be None")

        image = self.base_image.create_image("/tmp")
        for i in range(len(self.writes)-1, -1, -1):
            image_writes = self.writes[:i]
            writes = self.writes[:i]

            # TODO all permutations of writes
            # TODO random permutation of writes (statistical generator)

            random.shuffle(writes)

            yield (Image(image, image_writes), writes)
