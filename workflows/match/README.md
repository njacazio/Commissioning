# matching

# download full outputs (apass#ID_debug dir in GRID)
# files needed (at least) o2match_itstpc.root tpctracks.root o2_tfidinfo.root trdmatches_*.root tofclusters.root

o2-global-track-cluster-reader --shm-segment-size 7000000000 --disable-mc --track-types "TPC,ITS-TPC,ITS-TPC-TRD,TPC-TRD" --cluster-types TOF --hbfutils-config o2_tfidinfo.root \
| o2-tof-matcher-workflow -b --hbfutils-config o2_tfidinfo.root --disable-mc --pipeline tof-matcher:3 --run

# for a single source (e.g. ITS-TPC)
o2-global-track-cluster-reader --shm-segment-size 7000000000 --disable-mc --track-types "ITS-TPC" --cluster-types TOF --hbfutils-config o2_tfidinfo.root --tpc-track-reader "tpctracks.root --reader-delay 15" \
| o2-tof-matcher-workflow -b --hbfutils-config o2_tfidinfo.root --disable-mc --track-sources ITS-TPC --pipeline tof-matcher:3 --run

# to produce a debug tree you can then run
o2-global-track-cluster-reader --shm-segment-size 7000000000 --disable-mc --track-types "TPC,ITS-TPC,ITS-TPC-TRD,TPC-TRD,TPC-TOF" --cluster-types TOF --hbfutils-config o2_tfidinfo.root \
| o2-tof-match-eventtime-workflow -b --hbfutils-config o2_tfidinfo.root --disable-mc

# or for a single source
o2-global-track-cluster-reader --shm-segment-size 7000000000 --disable-mc --track-types "ITS-TPC" --cluster-types TOF --hbfutils-config o2_tfidinfo.root \
| o2-tof-match-eventtime-workflow -b --hbfutils-config o2_tfidinfo.root --disable-mc --track-sources ITS-TPC,ITS-TPC-TOF

# macro for checking
root -b -q -l check.C

# note that if you want to analyze TPC only you need to add also TPC-TOF source in the reader



# to run Matching QC
# same reader configuration (including TPC-TOF for TPC only tracks)
# plus
| o2-qc ...


# to run PID QC
# extra requirement: o2reco_ft0.root to be added also in the reader
o2-global-track-cluster-reader --shm-segment-size 7000000000 --disable-mc --track-types "TPC,ITS-TPC,ITS-TPC-TRD,TPC-TRD,TPC-TOF" --cluster-types TOF,FT0 --hbfutils-config o2_tfidinfo.root \
| o2-qc ...
