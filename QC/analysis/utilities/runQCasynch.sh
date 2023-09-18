#! /usr/bin/env bash

#Usage: . runQCasynch.sh <period> <pass>

PERIOD=$1
PASS=$2

awk '{print ". getAQCplots.sh", $1, "'$PERIOD'", "'$PASS'"}' jiratext.txt > getfromccdb.sh

. getfromccdb.sh