#! /usr/bin/env bash

### Crate  6 --> A:TOF/RAWDATA/768
### Crate  7 --> B:TOF/RAWDATA/1024
### Crate 10 --> C:TOF/RAWDATA/1280
### Crate 11 --> D:TOF/RAWDATA/1536

#PROXY_SPEC="A:TOF/RAWDATA/768;B:TOF/RAWDATA/1024;C:TOF/RAWDATA/1280;D:TOF/RAWDATA/1536"
#COMPR_CONF="A:TOF/RAWDATA/768,B:TOF/RAWDATA/1024,C:TOF/RAWDATA/1280,D:TOF/RAWDATA/1536"
PROXY_SPEC="x:TOF/RAWDATA"
COMPR_CONF="x:TOF/RAWDATA"

VERBOSE=""
#VERBOSE="--tof-compressor-verbose --tof-compressor-decoder-verbose"

QCJSONRAW="${QUALITYCONTROL_ROOT}/etc/tofcompressed.json"
QCJSONDIG="${QUALITYCONTROL_ROOT}/etc/tof.json"
#QCJSONFUL="${QUALITYCONTROL_ROOT}/etc/toffull.json"
QCJSONFUL="/home/flp/o2/QualityControl/Modules/TOF/toffull.json"
QCJSON=${QCJSONFUL}

#RECOWFLOWOPT="--input-type raw --output-type none --row-filter --mask-noise --noise-counts 10"
RECOWFLOWOPT="--input-type raw --output-type none"

#DIGIWRITEOPT="--ntf 2 --write-decoding-errors"
DIGIWRITEOPT="--ntf 4096"

o2-dpl-raw-proxy -b --session default \
    --dataspec "$PROXY_SPEC" \
    --channel-config "name=readout-proxy,type=pull,method=connect,address=ipc:///tmp/stf-builder-dpl-pipe-0,transport=shmem,rateLogging=1" \
    | o2-tof-compressor -b --session default \
    --tof-compressor-rdh-version 6 \
    --tof-compressor-config "$COMPR_CONF" \
    $VERBOSE \
    | o2-tof-reco-workflow -b --session default ${RECOWFLOWOPT} \
    | o2-tof-digit-writer-workflow -b --session default ${DIGIWRITEOPT} \
    | o2-qc -b --session default \
    --config json://${QCJSON} \
    | o2-tof-compressed-inspector -b --session default \
    --tof-compressed-inspector-rdh-version 6 \
    --tof-compressed-inspector-filename inspector.root
