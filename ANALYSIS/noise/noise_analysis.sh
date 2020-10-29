#! /usr/bin/env bash

#VERBOSE="--tof-compressor-verbose --tof-compressor-decoder-verbose --tof-compressor-encoder-verbose --tof-compressor-checker-verbose"
VERBOSE=""

if [ -z "$1" ]; then
    echo "usage: ./noise_analysis [filein] [fileout]"
    exit 1
fi
FILEIN=$1

if [ -z "$2" ]; then
    echo "usage: ./noise_analysis [filein] [fileout]"
    exit 1
fi
FILEOUT=$2

atc-file-proxy -b --rate 100 \
	       --atc-file-proxy-conet-mode \
	       --atc-file-proxy-input-filename ${FILEIN} \
	       --atc-file-proxy-start-from 0 \ # 332643308 \ # 355521064 \
    | \
    o2-tof-compressor -b \
		      --tof-compressor-conet-mode $VERBOSE \
    | \
    o2-tof-compressed-analysis -b \
			       --tof-compressed-analysis-conet-mode \
			       --tof-compressed-analysis-filename noise_analysis.C \
			       --tof-compressed-analysis-function "noise_analysis(4096, 36864, \"$FILEOUT\")" \
			       --run
