#! /usr/bin/env bash

### default interaction rate: 2.667 kHz

DIR=$(dirname "${BASH_SOURCE[0]}")
[ -z "$1" ] && RATE=2667 || RATE=$1

echo " --- running digitization: ${RATE} Hz "

o2-sim-digitizer-workflow --disable-mc -b --run --interactionRate ${RATE}
