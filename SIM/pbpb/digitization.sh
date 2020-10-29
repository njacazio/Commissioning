#! /usr/bin/env bash

### default interaction rate: 50 kHz

DIR=$(dirname "${BASH_SOURCE[0]}")
[ -z "$1" ] && RATE=50000 || RATE=$1

echo " --- running digitization: ${RATE} Hz "

o2-sim-digitizer-workflow --disable-mc -b --run --interactionRate ${RATE}
