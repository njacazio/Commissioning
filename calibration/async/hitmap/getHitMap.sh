#!/bin/bash

export year=$1
export period=$2
export pass=$3
export run=$4

rm -rf QC.root
export input=$(alien.py find  /alice/data/$1/$2/$4/$3 QC_fullrun.root)
export isFull=$(alien.py find /alice/data/$1/$2/$4/$3 QC_fullrun.root|wc -l)

if [ $isFull == "0" ]; then
export input=$(alien.py find  /alice/data/$1/$2/$4/$3 QC.root|grep 001|tail --line 1)
fi

echo alien.py cp alien://$input file:QC.root
alien.py cp alien://$input file:QC.root

root -b -q -l extractMap.C
