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

o2-dpl-raw-proxy -b --session default \
    --dataspec "$PROXY_SPEC" \
    --channel-config "name=readout-proxy,type=pull,method=connect,address=ipc:///tmp/stf-builder-dpl-pipe-0,transport=shmem,rateLogging=1" \
    | o2-tof-compressor -b --session default \
    --tof-compressor-rdh-version 6 \
    --tof-compressor-config "$COMPR_CONF" \
    $VERBOSE \
    | o2-tof-reco-workflow -b --session default \
    --input-type raw \
    --output-type digits \
    | o2-tof-compressed-inspector -b --session default \
    --tof-compressed-inspector-rdh-version 6 \
    --tof-compressed-inspector-filename inspector.root
