#! /usr/bin/env bash

### all crates --> x:TOF/RAWDATA
### crate 6    --> A:TOF/RAWDATA/768
### crate 7    --> B:TOF/RAWDATA/1024
### crate 10   --> C:TOF/RAWDATA/1280
### crate 11   --> D:TOF/RAWDATA/1536

o2-dpl-raw-proxy -b --session default \
    --dataspec "A:TOF/RAWDATA/768;B:TOF/RAWDATA/1024;C:TOF/RAWDATA/1280;D:TOF/RAWDATA/1536" \
    --channel-config "name=readout-proxy,type=pull,method=connect,address=ipc:///tmp/stf-builder-dpl-pipe-0,transport=shmem,rateLogging=1" \
    | o2-tof-compressor -b --tof-compressor-rdh-version 6 \
    --tof-compressor-config "A:TOF/RAWDATA"  \
    | o2-tof-compressed-inspector -b --tof-compressed-inspector-rdh-version 6 --tof-compressed-inspector-filename inspector.root --timeout 60
