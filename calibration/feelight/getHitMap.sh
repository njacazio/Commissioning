#!/bin/bash

export year=$1
export period=$2
export pass=$3
export run=$4

rm QC.root
export input=$(alien.py find  /alice/data/$1/$2/$4/$3 QC_fullrun.root)
alien.py cp alien://$input file:QC.root

root -b -q -l extractMap.C
