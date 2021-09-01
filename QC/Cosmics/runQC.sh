#!/bin/bash

QCJSON=${QUALITYCONTROL_ROOT}/etc/tofcosmics.json
o2-tof-cluscal-reader-workflow -b --cosmics | o2-qc -b --config json://"${QCJSON}"

