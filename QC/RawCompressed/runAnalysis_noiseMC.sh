#! /usr/bin/env bash

if [ -z "$1" ]; then
    echo "usage: ./runAnalysis_noiseMC.sh [fileout]"
    exit 1
fi
FILEOUT=$1

o2-raw-file-reader-workflow -b --input-conf o2-raw-file-reader-workflow.ini \
    | \
    o2-tof-compressor -b \
    | \
    o2-tof-compressed-analysis -b \
			       --tof-compressed-analysis-filename ../../ANALYSIS/noise/noise_analysis.C \
			       --tof-compressed-analysis-function "noise_analysis(4096, 36864, \"$FILEOUT\")" \
			       --run
