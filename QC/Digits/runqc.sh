#!/bin/bash

reset

o2-tof-reco-workflow -b --output-type none --disable-mc |
    o2-qc -b --config json://${PWD}/tof.json
    #o2-qc -b --config json://${PWD}/tof.json --severity warning
