#!/bin/bash

rm -rf TOF
o2-ccdb-downloadccdbfile -t $1 -p TOF/Calib/FEELIGHT
mv TOF/Calib/FEELIGHT/snapshot.root o2-dataformats-Feelight_$1_$1_$1.root

rm feelight.root
ln -s o2-dataformats-Feelight_$1_$1_$1.root feelight.root
