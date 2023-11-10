#!/bin/bash

for i in ${@}; do
    echo ${i}
    t=${i##*/}
    ./make_reso_with_ev_time.py $i/*/Analysis*trees*.root -t ${t} -l ${t} --minpt 1.3 --maxpt 1.4 --maxfiles -20 -j 4 -b
done
