#! /usr/bin/env bash

RUN=$1
TIMESTAMP=$2
echo "-------------------------------------"
echo "  Providing QC plots for Run $RUN   "
echo "-------------------------------------"

rm -rf Run$RUN/
mkdir Run$RUN
mkdir Run$RUN/rootfiles

# Declare an array of string with type
declare -a RawMONames=( "hOrbitID" "hSlotPartMask" "hHits" "hEffRDHTriggers" "RDHCounter" "DRMCounter" "TRMCounterSlot03" "TRMCounterSlot04" "TRMCounterSlot05" "TRMCounterSlot06" "TRMCounterSlot07" "TRMCounterSlot08" "TRMCounterSlot09" "hIndexEOIsNoise" "hIndexEOIsNoise" "hIndexEOHitRate" )
declare -a DigitsMONames=( "HitMap" "ToT/Integrated" "ToT/SectorIA" "ToT/SectorIC" "ToT/SectorOA" "ToT/SectorOC" "Multiplicity/Integrated" "Multiplicity/SectorIA" "Multiplicity/SectorIC" "Multiplicity/SectorOA" "Multiplicity/SectorOC" "Time/Integrated" "Time/SectorIA" "Time/SectorIC" "Time/SectorOC" "Time/SectorOC" "Time/Orphans" "ReadoutWindowSize" "OrbitVsCrate" )

# Iterate the string array using for loop
for name in ${RawMONames[@]}; do
    python3 fetch_output.py qc/TOF/MO/TaskRaw/$name -t $TIMESTAMP -o Run$RUN
    mv Run$RUN/qc/TOF/MO/TaskRaw/$name/snapshot.root  Run$RUN/rootfiles/$name.root
done

for name in ${DigitsMONames[@]}; do
    declare -a newname=$(echo $name | tr / _)
    python3 fetch_output.py qc/TOF/MO/TaskDigits/$name -t $TIMESTAMP -o Run$RUN
    mv Run$RUN/qc/TOF/MO/TaskDigits/$name/snapshot.root  Run$RUN/rootfiles/$newname.root
done

python3 fetch_output.py qc/TOF/MO/TOFTrendingHits/mean_of_hits -t $TIMESTAMP -o Run$RUN
mv Run$RUN/qc/TOF/MO/TOFTrendingHits/mean_of_hits/snapshot.root  Run$RUN/rootfiles/mean_of_hits.root

rm -rf Run$RUN/qc

root -l -b -q drawqcplots.C\(\"$RUN\"\)

