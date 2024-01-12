#!/bin/bash
size=$(du -H|awk '{print $1}')
#let soppression=size/500000000+1

ls calib*root|awk '{print "./filter.sh",$1,"1"}' >skimming
bash skimming

