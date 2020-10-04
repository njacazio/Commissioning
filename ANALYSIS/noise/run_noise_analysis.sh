#! /usr/bin/env bash

DIR=$1

rm -rf $DIR/noise_analysis.*.root
rm -rf $DIR/*.log

for CRATE in {00..71} ; do
    FILENAME=$DIR/tofdata-$CRATE.0000.scl
    if [ -f "$FILENAME" ]; then
	echo " --- running noise_analysis: $FILENAME "
	./noise_analysis.sh $FILENAME $DIR/noise_analysis.$CRATE.root > $DIR/noise_analysis.$CRATE.log
    fi
done

hadd -f $DIR/noise_analysis.root $DIR/noise_analysis.*.root
