#! /usr/bin/env bash

o2-dpl-raw-proxy -b --session default \
    --dataspec "A:TOF/RAWDATA" \
    --channel-config "name=readout-proxy,type=pull,method=connect,address=ipc:///tmp/stf-builder-dpl-pipe-0,transport=shmem,rateLogging=1" \
    | o2-tof-compressor -b --tof-compressor-rdh-version 6 \
    | o2-dpl-output-proxy -b --session default \
    --dataspec "downstream:TOF/CRAWDATA" \
    --channel-config "name=downstream,type=push,method=bind,address=ipc:///tmp/stf-pipe-0,rateLogging=1,transport=shmem"
