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
from itertools import permutations, islice
from collections import deque

from .write import overlapping


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
        shuffled in a way that makes them unique. Takes into account if the
        writes are overlapping.

        The group_size specifies how big the permutation group will be, where
        the group is a set of last written blocks to image.
        """
        if self.base_image is None:
            raise TypeError("base_image can't be None")
        if self.writes is None:
            raise TypeError("writes can't be None")
        image = self.base_image.create_image(self.image_dir)

        # process writes in memory efficient way
        iter_writes = iter(self.writes)
        writes = deque(islice(iter_writes, group_size))
        base_writes = list()

        new_write = True
        while True:
            # first return the base image with writes in order
            yield (Image(image, list(base_writes)), tuple())
            existing_lists = set()
            existing_sets = set()
            # slice the permutations so that we get partial non-in-order writes
            for draw_group in (i[:l] for i in permutations(writes)
                    for l in range(1, group_size+1)):
                # make sure we do not return the same list of writes
                # as we are slicing the tuples returned by permutations()
                # so for large group sizes there would be a lot of duplication
                if draw_group in existing_lists:
                    continue
                existing_lists.add(draw_group)
                # if the writes are in-order, skip them as they will be
                # returned as a base image
                if writes and writes[0] == draw_group[0]:
                    continue
                # if the writes overlap then the order matters so return them
                if overlapping(draw_group):
                    yield (Image(image, list(base_writes)), draw_group)
                else:
                    # if they don't overlap, then order doesn't matter
                    # so don't return duplicates of such lists
                    if set(draw_group) in existing_sets:
                        continue
                    existing_sets.add(frozenset(draw_group))
                    # that also means that we should skip ones that are just
                    # permutation of the first few writes as those will be
                    # returned as base image
                    if set(draw_group) == set(islice(writes, len(draw_group))):
                        continue
                    # or ones that include the first element (as this has the
                    # same effect as an in-order set of writes for overlapping)
                    if writes and writes[0] in draw_group:
                        continue
                    yield (Image(image, list(base_writes)), draw_group)

            if not writes:
                break
            # move the first ordered write to base image, get new one to
            # permutations, if available
            base_writes.append(writes.popleft())
            new_write = next(iter_writes, None)
            if new_write:
                writes.append(new_write)
            # TODO fold down base image when base_writes grows very large?

    def cleanup(self):
        """Remove the temporary image created by generator and shuffle."""
        self.base_image.cleanup()
