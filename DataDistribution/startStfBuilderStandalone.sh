#! /usr/bin/env bash

StfBuilder \
    --id stf_builder-0 \
    --transport shmem \
    --detector TOF \
    --detector-rdh 6 \
    --channel-config "name=readout,type=pull,method=connect,address=ipc:///tmp/readout-pipe-0,transport=shmem,rateLogging=1" \
    --stand-alone

