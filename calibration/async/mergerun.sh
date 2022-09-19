#!/bin/bash
rm o2_ctf_*.root

alien.py find /alice/data/2022/$1/$2/apass1 o2calib_tof.root|awk '{print "alien://"$1}' |sort >listafile
cat listafile  |awk -F"/" '{print "./copy.sh",$8,$10,$7}'|bash
#cat listafile  |awk -F"/" '{print "./copy.sh",$8,$10,$7}'|bash
#cat listafile  |awk -F"/" '{print "./copy.sh",$8,$10,$7}'|bash

sleep 60

ls -l |grep " 228"|awk '{print "rm",$9}' |bash

ls |grep o2_ctf_run005|sort >listafile
root -b -q -l DoMerge.C
mv calib.root calib$2.root
cat listafile|awk '{print "rm",$1}' | bash
