#Initializer script for the O2 in swan

if [[ -n "${1}" ]]; then
    echo "Downloading SWAN resources"
    wget https://raw.githubusercontent.com/alicetof/Commissioning/master/QC/analysis/notebooks/draw.ipynb
    wget https://raw.githubusercontent.com/alicetof/Commissioning/master/QC/analysis/common.py
    wget https://raw.githubusercontent.com/alicetof/Commissioning/master/QC/analysis/plotting.py
    wget https://raw.githubusercontent.com/alicetof/Commissioning/master/QC/analysis/utilities/fetch_output.py
    return
fi

export aTODAY=$(date -d "yesterday 13:00" "+%Y%m%d")
version=VO_ALICE@O2::nightly-${aTODAY}-1
echo "Entering $version"
eval $(/cvmfs/alice.cern.ch/bin/alienv printenv $version)
export CPPYY_BACKEND_LIBRARY=${ROOTSYS}/lib/libcppyy_backend3_6
export PYTHONPATH=${HOME}.local:$PYTHONPATH
