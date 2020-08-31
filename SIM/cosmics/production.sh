#! /usr/bin/env bash

### raw
o2-tof-digi2raw

### compressor
o2-raw-file-reader-workflow -b --input-conf o2-raw-file-reader-workflow.ini | \
    o2-tof-compressor -b | \
    o2-tof-compressed-inspector -b --tof-compressed-inspector-rdh-version 6

