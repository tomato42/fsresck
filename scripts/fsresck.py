#!/usr/bin/python

from fsresck.imagegenerator import BaseImageGenerator
from fsresck.fragmenter import Fragmenter
from fsresck.writesshuffler import WritesShuffler
import fsresck.utils as utils
import os

def main():

    # get the unmodified image file name
    unmodified_image = "/tmp/file"

    # get the change log for the file system image
    log = "/tmp/file-writes"

    base_gen = BaseImageGenerator(unmodified_image, log)

    for base_image, writes in base_gen.generate():

        fragmenter = Fragmenter(sector_size=512)
        writes = fragmenter.fragment(writes)

        shuffler = WritesShuffler(base_image, writes)

        for image, shuffled_writes in shuffler.generator():

            temp_image = image.create_image()

            test_image = utils.get_empty_image_name("/tmp")
            utils.copy(temp_image, test_image)

            # test test_image

            os.unlink(test_image)

            for write in shuffled_writes:

                with open(temp_image, "w+b") as image_file:
                    image_file.seek(write.offset)
                    image_file.write(write.data)

                test_image = utils.get_empty_image_name("/tmp")
                utils.copy(temp_image, test_image)

                # test test_image

                os.unlink(test_image)

            image.cleanup()

        shuffler.cleanup()

if __name__ == '__main__':
    main()
