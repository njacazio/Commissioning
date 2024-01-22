#!/bin/bash
cat FEELIGHT|grep "runNumberFromTOF = $1" -B 10|grep "Validity"|awk '{print "'$1'",$2,$4}'
cat FEELIGHT|grep "runNumberFromTOF = $1" -B 10|grep "Validity"|awk '{print "'$1'",$2,$4}' >> runinfo
