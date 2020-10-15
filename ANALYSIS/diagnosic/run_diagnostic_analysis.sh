#! /usr/bin/env bash

if [ -z "$1" ]; then
    echo "usage: ./run_diagnostic_analysis [datadir]"
    exit 1
fi

DIR=$1

rm -rf $DIR/diagnostic_analysis.*.root
rm -rf $DIR/*.log

for CRATE in {00..71} ; do
    FILENAME=$DIR/run-00.tofdata-$CRATE.0000.scl
    if [ -f "$FILENAME" ]; then
	echo " --- running diagnostic_analysis: $FILENAME "
	./diagnostic_analysis.sh $FILENAME $DIR/diagnostic_analysis.$CRATE.root > $DIR/diagnostic_analysis.$CRATE.log
    fi
done

hadd -f $DIR/diagnostic_analysis.root $DIR/diagnostic_analysis.*.root
rm -rf $DIR/diagnostic_analysis.*.root
rm -rf $DIR/*.log
