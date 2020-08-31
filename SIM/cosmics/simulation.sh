#! /usr/bin/env bash

### default number of events is 22765 to
### generate 256 orbits at 2.667 kHz rate

### 2 seconds/event (on R+Docker), 0.04 Mbytes/event
### 12 hours total time, 960 Mbytes

DIR=$(dirname "${BASH_SOURCE[0]}")
[ -z "$1" ] && NEVENTS=22765 || NEVENTS=$1

echo " --- running simulation: ${NEVENTS} events "

o2-sim-serial -n ${NEVENTS} -g extgen -m TOF --field 0 --extGenFile ${DIR}/cosmicGenerator.C
