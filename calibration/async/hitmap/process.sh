#!/bin/bash
# 1 = run number
# 2 = SOR
# 3 = year
# 4 = period
# 5 = pass
# 6 = EOR

./getFEEfromTS.sh $2

# get hitmap from QC
rm -rf QC.root
./getHitMap.sh $3 $4 $5 $1

rm newfee.root

# compare
root -b -q -l  compare.C

mv newfee.root newobj/Feelight_$1_$2_$6.root

