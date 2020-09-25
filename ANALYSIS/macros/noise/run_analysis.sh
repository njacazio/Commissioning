#! /usr/bin/env bash

o2-raw-file-reader-workflow -b --input-conf o2-raw-file-reader-workflow.ini | \
    o2-tof-compressor -b | \
    o2-tof-compressed-analysis -b \
    --tof-compressed-analysis-filename noise_analysis.C \
    --tof-compressed-analysis-function "noise_analysis(4096, 36864)"
