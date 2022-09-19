#!/bin/bash

ls calib$1*|awk -F".root" '{print $1}'|awk -F"part" '{print $2,$1"part"$2".root"}'|sort -n|awk '{print $2}' >listacal

# check after 100 s if ccdb is updated (for LHCphase)

# example
#--condition-remap "http://alice-ccdb.cern.ch/user/username=TOF/Calib/LHCPhace,TOF/Calib/Diagnostics;\
#                      http://ccdb-test.cern.ch:8080=ITS/Calib/Align;\
#                      file:///home/shahoian/localSnaphot=GLO/Config/GRPECS" # to fetch from local snapshot.root

o2-tof-calib-reader -b --collection-infile listacal \
| o2-calibration-tof-calib-workflow  --do-channel-offset --update-at-end-of-run-only --min-entries 8 -b --condition-tf-per-query 880 --use-ccdb --condition-backend $ccdburl --range 200000 --nbins 2000 \
--condition-remap "http://alice-ccdb.cern.ch=CTP/Calib/OrbitReset,GLO/Config/GRPECS;http://ccdb-test.cern.ch:8080=TOF/Calib/LHCphase" \
| o2-calibration-ccdb-populator-workflow -b --ccdb-path $ccdburl
