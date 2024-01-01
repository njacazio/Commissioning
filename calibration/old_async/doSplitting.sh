#!/bin/bash

cat $2  |awk -F"/" '{print "./copy.sh",$8,$11,$7,$10}'|bash
sleep 60

ls -l |grep " 228"|awk '{print "rm",$9}' |bash

ls |grep o2_ctf_run00523|sort >listafile
root -b -q -l DoMerge.C
mv calib.root calib$3-part$1.root
cat listafile|awk '{print "rm",$1}' | bash

