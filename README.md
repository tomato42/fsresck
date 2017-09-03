[![Build Status](https://travis-ci.org/tomato42/fsresck.svg?branch=master)](https://travis-ci.org/tomato42/fsresck)
[![Coverage Status](https://coveralls.io/repos/tomato42/fsresck/badge.svg?branch=master)](https://coveralls.io/r/tomato42/fsresck?branch=master)
[![Code Health](https://landscape.io/github/tomato42/fsresck/master/landscape.svg?style=flat)](https://landscape.io/github/tomato42/fsresck/master)
[![Code Climate](https://codeclimate.com/github/tomato42/fsresck/badges/gpa.svg)](https://codeclimate.com/github/tomato42/fsresck)

File System Resilience Checker
==============================

This tool is used for checking how file systems deal with storage subsystem
errors or shortcommings: partial writes, lack of barriers, write errors, etc.

Proof of concept stage (early alpha)

Theory of operation
===================

The system works in two steps. The first step aims to collect disk accesses
(writes, barriers, sync operations), something similar to a network packet
dump. The second step exercises the actual implementation of the layer built
on top of the block device (MD RAID, LVM or file system).

Collection of traces
--------------------

To collect traces, the system creates virtual block devices, using NBD
(network block device), proxies all the disk accesses through itself and saves
any modifications to a file. This can be done from the start, by using empty
files as the original block device, or it can be done on existing file system.
End result of the process is the original state of the device and a log file
that allows for recreation of the state of the block device at any moment in
time after introduction of the fsresck.

Exercising of implementation
----------------------------

Testing of the actual implementation starts with a copy of the original device
file that is then modified using log file. When such prepared state is ready
for testing, it is mounted using loop device and the testing of implementation
can begin (running fsck, mounting the file system, etc.). Once that is done,
a file with different state is prepared and the process continues.

Algorithm
=========

Because any single write can be comprise of multiple sectors (it's not uncommon
to write a full page (4KiB) at a time), the generation of images can work
in two main modes - write mode, where the atomic operation is a single write
or block mode, where the atomic operation is a single sector.

First step is to prepare a base image, that is done by taking the original
image, and replying the log up to specific point in time. Few reads past that
point are taken and permutated in order. That permutation is then written
write by write and tested, but only if it would not cause testing the same
permutation multiple times.

Full list of permutations of three element list would look like this:
```
list(i[:l] for i in itertools.permutations([0, 1, 2]) for l in range(1, 4)) =
[(0,), (0, 1), (0, 1, 2), (0,), (0, 2), (0, 2, 1), (1,), (1, 0), (1, 0, 2),
 (1,), (1, 2), (1, 2, 0), (2,), (2, 0), (2, 0, 1), (2,), (2, 1), (2, 1, 0)]
```

This has quite clearly a lot of duplication, if we remove it, we end up with
something like this:
```
collections.OrderedDict((i[:l], None)
                         for i in itertools.permutations([0, 1, 2])
                         for l in range(1, 4)).keys() =
[(0,), (0, 1), (0, 1, 2), (0, 2), (0, 2, 1), (1,), (1, 0), (1, 0, 2), (1, 2),
 (1, 2, 0), (2,), (2, 0), (2, 0, 1), (2, 1), (2, 1, 0)]
```

Since the first three permutations, are in order, we do not test them, as
that would duplicate the testing of the base images.

If we assume that all writes overlap (e.g. all change the exact same sectors),
we thus end up with a following list of writes that need to be tested (assuming
a 3-element queue):
```
[(0, 2), (0, 2, 1), (1,), (1, 0), (1, 0, 2), (1, 2),
 (1, 2, 0), (2,), (2, 0), (2, 0, 1), (2, 1), (2, 1, 0)]
```

If the writes do not overlap, and every one of them modifies a different
part of the block device, then modifications like (0, 2) and (2, 0) are
identical.

Thus we arrive at something like this:
```
[tuple(i) for i in OrderedDict((frozenset(i[:l]), None)
                                for i in itertools.permutations([0, 1, 2])
                                for l in range(1, 4)).keys()] =
[(0,), (0, 1), (0, 1, 2), (0, 2), (1,), (1, 2), (2,)]
```

Again, we need to ignore the first elements that propose writes in order,
getting the following order of operations in the end:
```
[(0, 2), (1,), (1, 2), (2,)]
```
