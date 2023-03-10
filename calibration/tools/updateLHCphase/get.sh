#!/bin/bash
export adjusting=$(cat $2|grep $1|awk '{print $2}')
rm *o2-data*
cat LHCphase |grep "runNumber = $1" -B 15|grep ID|awk '{print "./downloadPhase.sh",$2}' |bash
mkdir $1
mv *o2-data* $1/.

cd $1
ls o2-data* |awk '{print "../adjust.sh",$1,"'$adjusting'"}'|bash
../prepare.sh $1
cd ..

