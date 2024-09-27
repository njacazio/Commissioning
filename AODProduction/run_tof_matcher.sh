#!/bin/bash

GLOSET="--disable-mc --shm-segment-size 5000000000 --hbfutils-config o2_tfidinfo.root "
o2-global-track-cluster-reader "$GLOSET" --track-types "TPC,TPC-TRD,ITS-TPC,ITS-TPC-TRD" --cluster-types TOF |
    o2-tof-matcher-workflow "$GLOSET" -b --run --track-sources TPC,TPC-TRD,ITS-TPC,ITS-TPC-TRD --output-type matching-info --tof-lanes 1
