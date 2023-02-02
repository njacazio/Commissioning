#!/bin/bash
export startV=$(cat LHCphase |grep $1 -A 5|grep "Validity:"|awk '{print $2}'|tail --lines 1)
export stopV=$(cat LHCphase |grep $1 -A 5|grep "Validity:"|awk '{print $4}'|tail --lines 1)
export created=$(cat LHCphase |grep $1 -A 5|grep "Created:"|awk '{print $2}'|tail --lines 1)
export output=o2-dataformats-CalibLHCphaseTOF_${created}_${startV}_${stopV}.root

#export output=$(cat ../LHCphase |grep $1 -A 5|grep "Validity"|awk '{print "o2-dataformats-CalibLHCphaseTOF_"$2"_"$2"_"$2.root}')
export input=$(alien.py find /alice/data/CCDB/TOF/Calib/LHCphase/ $1)
alien.py cp alien://$input file:$output
