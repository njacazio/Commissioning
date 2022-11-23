#!/bin/bash

~/Alice/ali-o2/ninja.sh
retn_code=$?

[ $retn_code=="0" ] && echo "OK" || exit 1

#reset

CMP=""
CMP="--configuration json://dpl-pid-config.json"

o2-analysis-pid-tof-full --add-qa 1 --param-file /tmp/tofreso.root --param-sigma TOFResoParams $CMP | \
o2-analysis-pid-tof-base $CMP | \
o2-analysis-trackselection $CMP | \
o2-analysis-track-propagation $CMP | \
o2-analysis-event-selection $CMP | \
o2-analysis-timestamp $CMP -b --aod-file @i.txt 



