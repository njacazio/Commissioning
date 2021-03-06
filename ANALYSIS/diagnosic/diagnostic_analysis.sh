#! /usr/bin/env bash

if [ -z "$1" ]; then
    echo "usage: ./diagnostic_analysis [filein] [fileout]"
    exit 1
fi
FILEIN=$1

if [ -z "$2" ]; then
    echo "usage: ./diagnostic_analysis [filein] [fileout]"
    exit 1
fi
FILEOUT=$2

atc-file-proxy -b \
	       --atc-file-proxy-conet-mode \
	       --atc-file-proxy-input-filename ${FILEIN} \
    | \
    o2-tof-compressor -b \
		      --tof-compressor-conet-mode \
    | \
    o2-tof-compressed-analysis -b \
			       --tof-compressed-analysis-conet-mode \
			       --tof-compressed-analysis-filename diagnostic_analysis.C \
			       --tof-compressed-analysis-function "diagnostic_analysis(\"$FILEOUT\")"
