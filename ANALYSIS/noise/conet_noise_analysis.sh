#! /usr/bin/env bash

VERBOSE="--tof-compressor-verbose --tof-compressor-decoder-verbose --tof-compressor-encoder-verbose --tof-compressor-checker-verbose"

MINTDC=4096
MAXTDC=36864

while true ; do

    RUN=$(date +%Y%m%d-%H%M%S)
    FILE=$RUN.noise_analysis.root

    atc-scl-proxy -b \
	| \
	o2-tof-compressor -b \
			  --tof-compressor-conet-mode \
	| \
	o2-tof-compressed-analysis -b \
				   --tof-compressed-analysis-conet-mode \
				   --tof-compressed-analysis-filename noise_analysis.C \
				   --tof-compressed-analysis-function "noise_analysis($MINTDC, $MAXTDC, \"$FILE\")" \
				   --run

done

