#! /usr/bin/env bash

if [ -z "$1" ]; then
    echo "usage: ./run_noise_analysis [datadir]"
    exit 1
fi

DIR=$1

rm -rf $DIR/noise_analysis.*.root
rm -rf $DIR/*.log

for CRATE in {00..71} ; do

    # skip
#    if [ $CRATE == "12" ]; then
#	continue;
 #   fi
  #  if [ $CRATE == "56" ]; then
#	continue;
 #   fi
    
    FILENAME=$DIR/run-01.tofdata-$CRATE.0000.scl
    if [ -f "$FILENAME" ]; then
	echo " --- running noise_analysis: $FILENAME "
	./noise_analysis.sh $FILENAME $DIR/noise_analysis.$CRATE.root > $DIR/noise_analysis.$CRATE.log
    fi
done

hadd -f $DIR/noise_analysis.root $DIR/noise_analysis.*.root
