#!/bin/bash
ls calib$1.root >listacal

o2-tof-calib-reader -b --collection-infile listacal \
| o2-calibration-tof-diagnostic-workflow -b --tf-per-slot 26400 --max-delay 0 --condition-tf-per-query -1 \
|o2-calibration-ccdb-populator-workflow -b --ccdb-path $ccdburl
