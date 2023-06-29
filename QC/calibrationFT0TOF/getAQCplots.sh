#! /usr/bin/env bash

RUN=$1
PERIOD=$2
PASS=$3

echo "-------------------------------------"
echo "  Providing QC plots for Run $RUN   "
echo "-------------------------------------"

rm -rf Run$RUN/
mkdir Run$RUN
mkdir Run$RUN/rootfiles

# Declare an array of string with type
declare -a PIDMONames=( "DeltaEvTimeTOFVsFT0CSameBC" "EvTimeTOF" )

for name in ${PIDMONames[@]}; do
    python3 fetch_output.py qc_async/TOF/MO/PID/$name -R $RUN --period $PERIOD --pass $PASS -o Run$RUN --downloadmode wget -v
    mv Run$RUN/qc_async/TOF/MO/PID/$name/snapshot.root  Run$RUN/rootfiles/$name.root
done

rm -rf Run$RUN/qc