#!/bin/bash

rm FEELIGHT
wget http://alice-ccdb.cern.ch/browse/TOF/Calib/FEELIGHT 1>/tmp/dummy 2>&1

export id=$(cat FEELIGHT |grep "runNumberFromTOF = $1" -B 15 |grep ID|awk '{print $2}')
echo $id

export output=$(cat FEELIGHT |grep $id -A 5|grep "Validity"|awk '{print "o2-dataformats-Feelight_"$2"_"$2"_"$2".root"}')
export input=$(alien.py find /alice/data/CCDB/TOF/Calib/FEELIGHT/ $id)
echo $input $output
alien.py cp alien://$input file:$output

rm lastfee.root
ln -s $output feelight.root
