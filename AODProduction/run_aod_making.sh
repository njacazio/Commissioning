#!/bin/bash


GLOSET="--shm-segment-size 24000000000 --hbfutils-config o2_tfidinfo.root,upstream --timeframes-rate-limit 3 --timeframes-rate-limit-ipcid 1 "
export DPL_REPORT_PROCESSING=1
o2-reader-driver-workflow $GLOSET | o2-aod-producer-workflow $GLOSET -b --run