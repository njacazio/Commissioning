#! /usr/bin/env bash

#VERBOSE="--tof-compressor-verbose --tof-compressor-decoder-verbose --tof-compressor-encoder-verbose --tof-compressor-checker-verbose"
VERBOSE=""

if [ -z "$1" ]; then
    echo "usage: ./qc_analysis [filein] [fileout]"
    exit 1
fi
FILEIN=$1

atc-file-proxy -b --rate 100 \
	       --atc-file-proxy-conet-mode \
	       --atc-file-proxy-input-filename ${FILEIN} \
	       --atc-file-proxy-start-from 0 \ # 332643308 \ # 355521064 \
    | \
    o2-tof-compressor -b \
		      --tof-compressor-conet-mode $VERBOSE \
    | \
    o2-qc -b --config json://${QUALITYCONTROL_ROOT}/etc/tofdiagnostics.json
#    o2-qc -b --config json://${QUALITYCONTROL_ROOT}/etc/tofcompressed.json

