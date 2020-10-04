#! /usr/bin/env bash

rm -rf noise_analysis.*.root

for CRATE in {00..71} ; do
    FILENAME=tofdata-$CRATE.0000.scl
    if [ -f "$FILENAME" ]; then
	echo " --- running noise_analysis: $FILENAME "
	./noise_analysis.sh $FILENAME noise_analysis.$CRATE.root > noise_analysis.$CRATE.log
    fi
done

hadd -f noise_analysis.root noise_analysis.*.root
