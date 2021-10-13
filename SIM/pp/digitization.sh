#! /usr/bin/env bash

### default interaction rate: 1 MHz

DIR=$(dirname "${BASH_SOURCE[0]}")
[ -z "$1" ] && RATE=1000000 || RATE=$1

echo " --- running digitization: ${RATE} Hz "

o2-sim-digitizer-workflow --disable-mc -b --run --interactionRate ${RATE}

o2-tof-reco-workflow -b --output-type raw
