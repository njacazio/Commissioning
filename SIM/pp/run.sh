#! /usr/bin/env bash

### usage: ./run.sh [orbits] [rate]

[ -z "$1" ] && ORBITS=256 || ORBITS=$1
[ -z "$2" ] && RATE=1000000 || RATE=$2

echo " --- requested $ORBITS orbits at $RATE Hz "

### calculate number of events to be simulated
### to obtain the requested number of orbits
### at the given interaction rate

BUNCHCROSSINGS=3564
LHCFREQUENCY=40079000

NEVENTS=$(echo "scale=0;$BUNCHCROSSINGS*$ORBITS*$RATE/$LHCFREQUENCY" | bc -l)

echo " --- required $NEVENTS events to be simulated "

### simulate and digitise
shopt -s extglob
./simulation.sh $NEVENTS && ./digitization.sh $RATE && rm -v !("tofdigits.root"|"o2sim_grp.root")

