#! /usr/bin/env bash

### on FLP 179 we have the following sectors
SECTORS="05 06 07 08 09 10 11 12 13"

### Crate XX --> A:TOF/RAWDATA/1280+XX

PROXY_SPEC=""
COMPR_CONF=""
for iSector in $SECTORS; do
    for iCrate in 0 1 2 3; do
	crateId=$((10#$iSector * 4 + 10#$iCrate))
	feeId=$((1280 + 10#$crateId))
	desc="c$crateId:TOF/RAWDATA/$feeId"
	PROXY_SPEC+="$desc;"
	COMPR_CONF+="$desc;"
    done
    COMPR_CONF=${COMPR_CONF:0:-1}
    COMPR_CONF+=","
done
COMPR_CONF=${COMPR_CONF:0:-1}
PROXY_SPEC+="dd:FLP/DISTSUBTIMEFRAME/0"

echo "=== PROXY_SPEC"
echo $PROXY_SPEC

echo "=== COMPR_CONF"
echo $COMPR_CONF

#PROXY_SPEC="x:TOF/RAWDATA;dd:FLP/DISTSUBTIMEFRAME/0"
#COMPR_CONF="x:TOF/RAWDATA"

VERBOSE=""
#VERBOSE="--tof-compressor-verbose --tof-compressor-decoder-verbose"


o2-dpl-raw-proxy -b --session default \
    --dataspec "$PROXY_SPEC" \
    --readout-proxy '--channel-config "name=readout-proxy,type=pull,method=connect,address=ipc:///tmp/stf-builder-dpl-pipe-0,transport=shmem,rateLogging=1"' \
    | o2-tof-compressor -b --session default \
    --tof-compressor-rdh-version 6 \
    --tof-compressor-config "$COMPR_CONF" \
    $VERBOSE \
    | o2-dpl-output-proxy -b --session default \
    --dataspec "A:TOF/CRAWDATA;dd:FLP/DISTSUBTIMEFRAME/0" \
    --dpl-output-proxy '--channel-config "name=downstream,type=push,method=bind,address=ipc:///tmp/stf-pipe-0,rateLogging=1,transport=shmem"' \
    --run

