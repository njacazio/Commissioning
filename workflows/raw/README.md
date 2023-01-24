# workflow to process starting from raw data

# general workflow to process raw data
o2-raw-file-reader-workflow -b --input-conf TOFraw.cfg |o2-tof-compressor -b | o2-tof-reco-workflow -b --input-type raw --output-type digits --outfile tofdigitsNew.root --ignore-dist-stf
# TOFraw.cfg example available here (as produced by simulation), one input expected per CRU


# ./MC dir for encoding/decoding in simulation


