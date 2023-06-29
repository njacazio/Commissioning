#! /usr/bin/env bash

PERIOD=$1
PASS=$2

awk '{print ". getAQCplots.sh", $1, "'LHC$PERIOD'", "'$PASS'"}' jiratext$PERIOD.txt > getfromccdb.sh

. getfromccdb.sh