# play with raw in simulation

# ENCODING RAW from digits (default: zero word suppression -> factor 2 gain in size)
o2-tof-reco-workflow -b --output-type raw
# for restore old behavior (no zero word suppression) add --use-old-format
o2-tof-reco-workflow -b --output-type raw --use-old-format

# Comparison of 2 encoding approach
./docomparison.sh


# DECODING FROM RAW (as for DATA)
o2-raw-file-reader-workflow -b --input-conf TOFraw.cfg |o2-tof-compressor -b | o2-tof-reco-workflow -b --input-type raw --output-type digits --outfile tofdigitsNew.root --ignore-dist-stf
#or
o2-raw-file-reader-workflow -b --input-conf TOFraw.cfg |o2-tof-compressor -b --use-old-format | o2-tof-reco-workflow -b --input-type raw --output-type digits --outfile tofdigitsNew.root --ignore-dist-stf

# NB
# --ignore-dist-stf needed since dist-stf(produced by raw-reader) is async with digits(produced by compressor)
