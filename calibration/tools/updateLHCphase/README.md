# download current status of production ccdb
wget http://alice-ccdb.cern.ch/browse/TOF/Calib/LHCphase

# crosscheck quality of LHCphase based on the trending (per period) of TOF_evtime and TOF_evtime vs FT0
# input (Franesca): FT0TOF_trending_#period_apass2.root with
# KEY: TH1F	trend_t0TOFFT0;1	trending FT0-TOF
# KEY: TH1F	trend_t0TOF;1	trending t0_{TOF}
root checkPhase.C\(\"FT0TOF_trending_#period]_apass2.root\"\)
# output: a file "#period" with the list of problematic runs for TOF with the shift to be applied

# a couple of script to prepare the upload to ccdb
# get.sh: download old ccdb (taken for the status of production ccdb previously downloaded) and apply the shift, it needs:
# downloadPhase.sh to download objects
# adjust.sh and adjust.C to apply the shift
# prepare.sh to create the script to upload object to ccdb

# e.g.
cat #period|awk '{print "./get.sh",$1,"#period"}'|bash
# to run on all problematic runs for a period (as flagged by checkPhase.C)
