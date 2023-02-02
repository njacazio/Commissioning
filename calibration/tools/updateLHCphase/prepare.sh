#!/bin/bash
export run=$1
ls updated_*.root |awk -F".root" '{print $1}' |awk -F"_" '{print "o2-ccdb-upload --host \"$ccdbhost\" -p TOF/Calib/LHCphase -f",$1"_"$2"_"$3"_"$4"_"$5".root","-k ccdb_object --starttimestamp",$5,"--endtimestamp",$5,"-m \"adjustableEOV=true;runNumber='$run';JIRA=[O2-3531];\""}' >uplaod_tmp
