#!/bin/sh
alien.py cp alien:///alice/data/2023/$3/$1/$5/$4/$2/o2calib_tof.root file:$2.root &

export instances=$(ps aux|grep alien.py|wc -l)

if [ $instances -gt 40 ]; then
sleep 20
fi
