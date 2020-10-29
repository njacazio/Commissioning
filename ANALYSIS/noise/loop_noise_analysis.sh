#! /usr/bin/env bash

if [ -z "$1" ]; then
    echo "usage: ./loop_noise_analysis [filename]"
    exit 1
fi

FILENAME=$1
if [ ! -f "$FILENAME" ]; then
    echo " --- file $FILENAME does not exist"
    exit 1
fi

COUNT=0
while true ; do
    RUN=$(printf "%03d" $COUNT)
    ./noise_analysis.sh $FILENAME noise_analysis.$RUN.root > noise_analysis.$RUN.log
    COUNT=$(($COUNT+1))
done

