#!/bin/bash
root -b -q -l ../adjust.C\(\"$1\",$2\) 2>&1 |grep -v Warning

ls updated_$1
if [ $? -gt 0 ]; then
touch updated_$1
echo $1 >>errors
fi

