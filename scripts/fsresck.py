#!/usr/bin/python

from fsresck.fragmenter import Fragmenter
from fsresck.writesshuffler import WritesShuffler

def main():

    for base_image, writes in BaseImageGenerator([(image, log)]):

        # fragment writes to sector sized chunks
        fragmenter = Fragmenter(sector_size=512)
        writes = fragmenter.fragment(writes)

        # generate permutations of writes to apply to image
        shuffler = WritesShuffler(base_image, writes)

        for image, shuffled_writes in shuffler.generator():

            temp_image = image.create_image()

            # copy temp_image to test_image

            # test test_image

            # remove test_image

            for write in shuffled_writes:
                # apply write to temp_image file

                # copy temp_image to test_image

                # test test_image

                # remove temp_image

            image.cleanup()

        shuffler.cleanup()

if __name__ == '__main__':
    main()
