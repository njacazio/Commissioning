#Initializer script for the O2 in swan

export aTODAY=$(date -d "yesterday 13:00" "+%Y%m%d")
version=VO_ALICE@O2::nightly-${aTODAY}-1
eval `/cvmfs/alice.cern.ch/bin/alienv printenv $version`
export CPPYY_BACKEND_LIBRARY=/cvmfs/alice.cern.ch/el7-x86_64/Packages/ROOT/v6-24-06-62/lib/libcppyy_backend3_6
export PYTHONPATH=${HOME}.local:$PYTHONPATH