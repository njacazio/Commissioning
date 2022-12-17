#! /usr/bin/env bash

PERIOD=$1
PASS=$2

awk '{print ". getAQCplots.sh", $1, "'$PERIOD'", "'$PASS'"}' jiratext.txt > getfromccdb.sh

. getfromccdb.sh