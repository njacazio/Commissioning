#!/bin/bash

o2-raw-file-reader-workflow --input-conf  /home/njacazio/aliceo2/TOFCommissioning/SIM/pp/TOFraw.cfg --loop -1 --rate 88 \
      | \
      o2-tof-compressor -b \
      | \
      o2-tof-reco-workflow --input-type raw --output-type digits -b \
      | \
      o2-qc -b --config json://${PWD}/tofdigits.json 


