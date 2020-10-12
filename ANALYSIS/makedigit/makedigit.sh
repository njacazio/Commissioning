#!/bin/bash
if [ -z "$1" ]; then
    echo "usage: ./makedigit.sh [filein]"
    exit 1
fi

export FILEIN=$1
export VERBOSE=""

export OUTPUTTYPE="digits"

# clusters require o2sim_geometry.root
#export OUTPUTTYPE="digits,clusters"

# ctf not yet supported
#export OUTPUTTYPE="digits,clusters,ctf"

export MASKNOISE=""
# export MASKNOISE="--mask-noise --noise-counts 5"

atc-file-proxy -b --rate 100 \
	       --atc-file-proxy-conet-mode \
	       --atc-file-proxy-input-filename ${FILEIN} \
	       --atc-file-proxy-start-from 0 \
    | \
    o2-tof-compressor -b \
		      --tof-compressor-conet-mode $VERBOSE \
    |\
    o2-tof-reco-workflow -b --input-type raw --output-type $OUTPUTTYPE --conet-mode $MASKNOISE #\
# ctf not yet supported
#    |\
#    o2-ctf-writer-workflow -b --onlyDet TOF
