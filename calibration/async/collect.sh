#!/bin/bash
mkdir $2
cd $2
cp ../*.sh .
cp ../*.C .

./mergerunSub.sh $1 $2 $3

./filterall.sh

rm calib*root

cd ..
