#!/bin/bash

#commands

#o2-sim -m TOF --CCDBUrl file://.ccdb -n 8000
#o2-sim-digitizer-workflow -b --onlyDet TOF --condition-backend file://.ccdb --interactionRate 650000


mkdir compareFormats
cd compareFormats
o2-sim -m TOF -n 7500
o2-sim-digitizer-workflow -b --onlyDet TOF --interactionRate 650000
o2-tof-reco-workflow -b --output-type raw --use-old-format
mkdir oldFormat
cp TOF* oldFormat/.
o2-raw-file-reader-workflow -b --input-conf TOFraw.cfg |o2-tof-compressor -b | o2-tof-reco-workflow -b --input-type raw --output-type digits --outfile tofdigitsFromRawOld.root  --ignore-dist-stf
o2-tof-reco-workflow -b --output-type raw
mkdir newFormat
cp TOF* newFormat/.
o2-raw-file-reader-workflow -b --input-conf TOFraw.cfg |o2-tof-compressor -b | o2-tof-reco-workflow -b --input-type raw --output-type digits --outfile tofdigitsFromRawNew.root  --ignore-dist-stf
du -hs TOF_ali* >oldsize
cd ..
