#!/bin/bash
rm o2_ctf_*.root

alien.py find /alice/data/2022/$1/$2/apass1_trigger o2calib_tof.root|awk '{print "alien://"$1}' |sort >listafile


export nfiles=$(cat listafile|wc -l)
echo nfiles=$nfiles

export run=$2

if [ $nfiles -gt 10000 ] ; then
  echo to be splitted
  cat listafile|awk -F"o2_ctf" '{print $2,$1"o2_ctf"$2}'|sort|awk '{print $2}' >sorted
  split sorted --lines=10000 splitted
  export nsplitted=$(ls splitted*|wc -l)
  ls splitted* >subprocesses
  cat -b subprocesses|awk '{print "./doSplitting.sh",$1,$2,"'$run'"}' >comSplitting
  bash comSplitting
  rm splitted*
else
  cat listafile  |awk -F"/" '{print "./copy.sh",$8,$11,$7,$10}'|bash
  sleep 60

  ls -l |grep " 228"|awk '{print "rm",$9}' |bash

  ls |grep o2_ctf_run00523|sort >listafile
  root -b -q -l DoMerge.C
  mv calib.root calib$2.root
  cat listafile|awk '{print "rm",$1}' | bash
fi
