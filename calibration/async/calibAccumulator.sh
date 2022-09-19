#!/bin/bash

#ls calib5*.root >listacal
ls calib523144-part$1.root >listacal

# check after 100 s if ccdb is updated (for LHCphase)

# example
#--condition-remap "http://alice-ccdb.cern.ch/user/username=TOF/Calib/LHCPhace,TOF/Calib/Diagnostics;\
#                      http://ccdb-test.cern.ch:8080=ITS/Calib/Align;\
#                      file:///home/shahoian/localSnaphot=GLO/Config/GRPECS" # to fetch from local snapshot.root


o2-tof-calib-reader -b --collection-infile listacal \
| o2-calibration-tof-collect-calib-workflow -b --update-interval 1000 --condition-tf-per-query 880 --use-ccdb --condition-backend $ccdburl \
--condition-remap "http://alice-ccdb.cern.ch=CTP/Calib/OrbitReset,GLO/Config/GRPECS;http://ccdb-test.cern.ch:8080=TOF/Calib/LHCphase,TOF/Calib/Diagnostic" \

ls collTOF_*|awk '{print "mv",$1,"'$1'_"$1}'|bash
