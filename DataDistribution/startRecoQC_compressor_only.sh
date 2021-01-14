#! /usr/bin/env bash

### Crate  6 --> A:TOF/RAWDATA/768
### Crate  7 --> B:TOF/RAWDATA/1024
### Crate 10 --> C:TOF/RAWDATA/1280
### Crate 11 --> D:TOF/RAWDATA/1536

#PROXY_SPEC="A:TOF/RAWDATA/768;B:TOF/RAWDATA/1024;C:TOF/RAWDATA/1280;D:TOF/RAWDATA/1536"
#COMPR_CONF="A:TOF/RAWDATA/768,B:TOF/RAWDATA/1024,C:TOF/RAWDATA/1280,D:TOF/RAWDATA/1536"
PROXY_SPEC="x:TOF/RAWDATA;dd:FLP/DISTSUBTIMEFRAME/0"
COMPR_CONF="x:TOF/RAWDATA"

VERBOSE=""
#VERBOSE="--tof-compressor-verbose --tof-compressor-decoder-verbose"

COMMONOPT="-b --session default"

QCJSONRAW="${QUALITYCONTROL_ROOT}/etc/tofcompressed.json"
QCJSONDIG="${QUALITYCONTROL_ROOT}/etc/tof.json"
QCJSONFUL="${QUALITYCONTROL_ROOT}/etc/toffull.json"
QCJSON="${PWD}/toffull_100.json"

#RECOWFLOWOPT="--input-type raw --output-type none --row-filter --mask-noise --noise-counts 10"
RECOWFLOWOPT="--input-type raw --output-type none"

#DIGIWRITEOPT="--ntf 2 --write-decoding-errors"
DIGIWRITEOPT="--ntf 4096"

o2-dpl-raw-proxy ${COMMONOPT} \
    --dataspec "$PROXY_SPEC" \
    --raw-proxy '--channel-config "name=readout-proxy,type=pull,method=connect,address=ipc:///tmp/stf-builder-dpl-pipe-0,transport=shmem,rateLogging=1"' \
    | o2-tof-compressor ${COMMONOPT} --tof-compressor-rdh-version 6 --tof-compressor-config "$COMPR_CONF" $VERBOSE \
    | o2-tof-reco-workflow ${COMMONOPT} ${RECOWFLOWOPT} \
    | o2-tof-digit-writer-workflow ${COMMONOPT} ${DIGIWRITEOPT}
