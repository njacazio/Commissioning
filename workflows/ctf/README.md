# this is an example to run on ctf
# list.list file cointaining a list of local ctf
o2-ctf-reader-workflow --onlyDet TOF  --ctf-input list.list -b | o2-qc --config json://${PWD}/tofdigits.json --local-batch digitQC.root -b --run

