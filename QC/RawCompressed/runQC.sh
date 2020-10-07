#!/usr/bin/env bash

reset

# Script to run QC on raw data
# Arguments (optionals):
# 1) configuration file for the raw reader e.g. o2-raw-file-reader-workflow.ini
# 2) json file for the configuration for the QC

CONFIGFILE="o2-raw-file-reader-workflow.ini"
if [[ -n $1 ]]; then
    CONFIGFILE="$1"
fi
if [[ -z $CONFIGFILE ]]; then
    echo "Cannot run with empty CONFIGFILE"
    exit 1
fi

QCJSON="${QUALITYCONTROL_ROOT}/etc/tofcompressed.json"
if [[ -n $2 ]]; then
    QCJSON="$2"
fi

if [[ -z $QCJSON ]]; then
    echo "Cannot run with empty QCJSON"
    exit 1
fi


echo "Using raw reader config '${CONFIGFILE}'"
echo "Using QC json config '${QCJSON}'"
sleep 10

### compressor
o2-raw-file-reader-workflow -b --input-conf "${CONFIGFILE}" \
| \
o2-tof-compressor -b \
| \
o2-qc -b --config json://"${QCJSON}"

rm localhost*

