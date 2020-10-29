#!/bin/bash

o2-raw-file-reader-workflow -b --input-conf o2-raw-reader-workflow.ini \
	| o2-tof-compressor -b \
	| o2-tof-compressed-inspector -b
