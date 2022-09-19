#!/bin/bash

ls calib$1.root|sort >listacal

o2-tof-calib-reader -b --collection-infile listacal \
| o2-calibration-tof-calib-workflow -b --do-lhc-phase --tf-per-slot 26400 --max-delay 0 --condition-tf-per-query -1 --use-ccdb  --condition-backend $ccdburl --nbins 4000 \
--condition-remap "http://alice-ccdb.cern.ch=CTP/Calib/OrbitReset,GLO/Config/GRPECS" \
|o2-calibration-ccdb-populator-workflow -b --ccdb-path $ccdburl
