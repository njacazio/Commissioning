#! /usr/bin/env bash

#VERBOSE="--tof-compressor-verbose --tof-compressor-decoder-verbose --tof-compressor-encoder-verbose --tof-compressor-checker-verbose"
VERBOSE=""

if [ -z "$1" ]; then
    echo "usage: ./noise_MCanalysis [fileout]"
    exit 1
fi
FILEOUT=$1

o2-raw-file-reader-workflow -b --input-conf o2-raw-file-reader-workflow.ini \
    | \
    o2-tof-compressor -b \
    | \
    o2-tof-compressed-analysis -b \
			       --tof-compressed-analysis-filename noise_analysis.C \
			       --tof-compressed-analysis-function "noise_analysis(4096, 36864, \"$FILEOUT\")" \
			       --run
