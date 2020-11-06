#!/bin/bash
if [ -z "$1" ]; then
    echo "usage: ./makedigit.sh [filein]"
    exit 1
fi

export FILEIN=$1
export VERBOSE=""

# digits written with a dedicated dpl. OUTPUTTYPE should contain only extra output wrt digits (i.e. clusters)
export OUTPUTTYPE="none"
# clusters require o2sim_geometry.root
#export OUTPUTTYPE="clusters"
# ctf not yet supported
#export OUTPUTTYPE="clusters,ctf"

export MASKNOISE="--row-filter"
#export MASKNOISE="--mask-noise --noise-counts 20 --row-filter"

# ntf (of bunch from compressor) written in each files (split parameters)
export DIGWRITEROPT="--ntf 50"
#export DIGWRITEROPT="--ntf 50 --write-decoding-errors"

atc-file-proxy -b --rate 100 \
	       --atc-file-proxy-conet-mode \
	       --atc-file-proxy-input-filename ${FILEIN} \
	       --atc-file-proxy-start-from 0 \
    | \
    o2-tof-compressor -b \
		      --tof-compressor-conet-mode $VERBOSE \
    |\
    o2-tof-reco-workflow -b --input-type raw --output-type $OUTPUTTYPE --conet-mode $MASKNOISE \
    |\
    |o2-tof-digit-writer-workflow -b $DIGWRITEROPT #\
# ctf not yet supported
#    |\
#    o2-ctf-writer-workflow -b --onlyDet TOF
