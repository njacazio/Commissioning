#!/bin/bash
date


export file=$(printf 'tree_%04d.root\n' $1)
ls $file
export status=$?
if [ $status == 0 ]; then
echo already done
exit 0
fi

root -b -q -l checkGrid.C\(\"$2\",$1\)
