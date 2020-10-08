#!/bin/bash

# Script to create the config file for the raw file reader
# Argument:
# Files (with full path)

FILES=$*

# Creating config file
CONFIGFILE="o2-raw-reader-workflow.ini"
echo "Writing configuration for ${FILES} in ${CONFIGFILE}"
echo "[defaults]" > $CONFIGFILE
echo "dataOrigin = TOF" >> $CONFIGFILE
echo "dataDescription = RAWDATA" >> $CONFIGFILE

NFILES=0
for i in $FILES; do
    echo "$NFILES) File $i"
    echo "" >> $CONFIGFILE
    echo "[input-${NFILES}]" >> $CONFIGFILE
    echo "filePath = $i" >> $CONFIGFILE
    (( NFILES++ ))
done
