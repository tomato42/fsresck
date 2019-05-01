#!/bin/bash

if ! [[ -e /dev/loop0 ]]; then
    echo Loop module not loaded, aborting
    exit 1
fi
if ! [[ -e /dev/nbd0 ]]; then
    echo NBD module not loaded, aborting
    exit 1
fi
if ! [[ -e scripts/write-capture.py ]]; then
    echo "can't find scripts/write-capture.py script, aborting"
    exit 1
fi

count="4"
size="5G"
cache_dir="/exports/tmp/disks"
devices=()
base_files=()
working_copies=()
pid_files=()
log_files=()
start_port=10810

for (( i=1; i <= $count; i++)); do
    base_files+=("$cache_dir/base$(printf "%02i" $i).img")
    working_copies+=("$cache_dir/working_copy$(printf "%02i" $i).img")
    pid_files+=("$cache_dir/working_copy$(printf "%02i" $i).pid")
    log_files+=("$cache_dir/base$(printf "%02i" $i).log")
done

if [[ -e ${base_files[0]} ]]; then
    echo base file exists: ${base_files[0]}, refusing to continue
    exit 1
fi

echo "base_files: ${base_files[*]}"

for file in "${base_files[@]}"; do
    truncate -s $size "$file"
    dev=$(losetup -f --show "$file")
    devices+=("$dev")
done

# perform the initial setup here
# (assemble MD RAID, mkfs, create files on the file system)
# don't forget to unmount the FS, stop the MD, etc.!
# the ${devices[@]} variable contains the list of block devices to use as members

mkfs.btrfs "${devices[@]}"

# end of initial setup

for dev in "${devices[@]}"; do
    losetup -d "$dev"
done

for i in "${!base_files[@]}"; do
    cp --reflink=auto --sparse=auto "${base_files[$i]}" "${working_copies[$i]}"
    touch "${log_files[$i]}"
    PYTHONPATH=. nbdkit --port $((start_port + i)) --pidfile "${pid_files[$i]}" python scripts/write-capture.py disk="${working_copies[$i]}" log="${log_files[$i]}"
done

dev_no=0
devices=()
for (( i=0; i<$count; i++ )); do
    while true; do
        # find an unused nbd handle
        if ! [[ -e /dev/nbd$dev_no ]]; then
            echo "exhausted nbd device names"
            exit 2
        fi
        if ! nbd-client -c /dev/nbd$dev_no; then
            break
        fi
        ((dev_no++))
    done
    nbd-client localhost $((start_port + i)) /dev/nbd$dev_no
    devices+=("/dev/nbd$dev_no")
done
sync
sleep 5
echo devices for the stress test script: ${devices[@]}

# perform the stress test here
# (re-assemble the MD raid, mount the fs, create or modify files)
# the ${devices[@]} variable contains the list of block devices to use as members
# don't forget to unmount the FS, stop the MD, etc.!

mount ${devices[0]} /mnt/test
for i in $(seq 1 20); do
    for j in $(seq 1 20); do
        mkdir -p /mnt/test/$i/$j
        echo "I'm a file in $i/$j" > /mnt/test/$i/$j/file.txt
    done
    btrfs filesystem sync /mnt/test
done
sync
for j in $(seq 1 20); do
    for i in $(seq 1 20); do
        echo "I'm a modified file in $i/$j" > /mnt/test/$i/$j/file.txt
    done
    btrfs filesystem sync /mnt/test
done
sync
umount /mnt/test

# end of stress test

for dev in "${devices[@]}"; do
    nbd-client -d $dev
done
sync
for file in "${pid_files[@]}"; do
    pid="$(cat "$file")"
    kill $pid
done
