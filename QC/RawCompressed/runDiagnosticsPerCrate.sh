#!/usr/bin/env bash

reset

o2-qc-run-postprocessing --config json://${QUALITYCONTROL_ROOT}/etc/tofpostprocessdiagnosticpercrate.json --name PostProcessDiagnosticPerCrate

rm localhost*

