#! /usr/bin/env bash

### default number of events is 1138 to
### generate 256 orbits at 50 kHz rate

### 140 seconds/event (on R+Docker), 3 Mbytes/event
### 44 hours total time, 3.4 Gbytes

DIR=$(dirname "${BASH_SOURCE[0]}")
[ -z "$1" ] && NEVENTS=1138 || NEVENTS=$1

echo " --- running simulation: ${NEVENTS} events "

o2-sim -n ${NEVENTS} -g pythia8hi -m TOF
