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

"""Helper methods for creating non-repeating permutations of images."""

from .image import Image

import random
from itertools import permutations


class WritesShuffler(object):

    """
    Generate sets of writes for image files.

    Generator that takes an image, set of writes and generates permutations
    of images and writes to test

    @todo: parametrise random source
    """

    def __init__(self, base_image, writes):
        """
        Link image file with writes.

        Provide the image that will create the base for the tests and the
        writes that should get tested.
        """
        self.base_image = base_image
        self.writes = writes
        self.image_dir = "/tmp"

    def shuffle(self):
        """Return a random permutation of writes with the image."""
        if self.base_image is None:
            raise TypeError("base_image can't be None")
        self.writes = list(self.writes)

        image = self.base_image.create_image(self.image_dir)

        while True:
            writes = self.writes[:]
            random.shuffle(writes)
            # skip permutations which have writes in order
            if writes[0] == self.writes[0]:
                continue
            yield (Image(image, []), writes)

    def generator(self, group_size=3):
        """
        Return all permutations of writes on an image.

        Iterator that returns pairs of images and logs of writes that are
        shuffled in a way that makes them unique.

        The group_size specifies how big the permutation group will be, where
        the group is a set of last written blocks to image.
        """
        if self.base_image is None:
            raise TypeError("base_image can't be None")
        self.writes = list(self.writes)

        image = self.base_image.create_image(self.image_dir)

        for i in range(group_size):
            draw_group = self.writes[:group_size]
            for perm in permutations(draw_group, i):
                yield (Image(image, []), perm)

        for j, base in enumerate(self.writes[:i] for i in
                                 range(max(0,
                                           len(self.writes) -
                                           group_size + 1))):
            draw_group = self.writes[j:j+group_size]
            for perm in permutations(draw_group):
                yield (Image(image, base), perm)

    def cleanup(self):
        """Remove the temporary image created by generator and shuffle."""
        self.base_image.cleanup()
