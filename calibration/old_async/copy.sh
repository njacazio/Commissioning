#!/bin/sh
alien.py cp alien:///alice/data/2022/$3/$1/apass1/$4/$2/o2calib_tof.root file:$2.root &

export instances=$(ps aux|grep convert|wc -l)

if [ $instances -gt 10 ]; then
sleep 2
fi
