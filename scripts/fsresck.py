

def main():

    for base_image, writes in BaseImageGenerator([(image, log)]):

        # fragment writes to sector sized chunks
        fragmenter = Fragmenter(sector_size=512)
        writes = fragmenter.fragment(writes)

        # shuffler starts from end, first creates a image without
        # last write, then without 2 writes with two writes swapped
        # then image without 3 writes and shuffled_writes and then
        # permutations of writes excluding writes in order or with first
        # write being in order
        for image, shuffled_writes in writesShuffler(base_image, writes):

            # create image file

            # copy image to temp_image
            # test temp_image

            for write in shuffled_writes:
                # copy image to temp_image
                # damage write and write it to temp_image
                # test temp_image

                # apply write to image file

                # copy image to temp_image
                # test temp_image
