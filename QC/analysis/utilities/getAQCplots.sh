#! /usr/bin/env bash

RUN=$1
PERIOD=$2
PASS=$3

echo "-------------------------------------"
echo "  Providing QC plots for Run $RUN   "
echo "-------------------------------------"

rm -rf Run$RUN/
mkdir Run$RUN
mkdir Run$RUN/rootfiles

# Declare an array of string with type
declare -a MatchingMONames=( "mEffPt_ITSTPC-ITSTPCTRD" "mEffPt_TPC" "mEffPt_TPCTRD" "mTOFChi2ITSTPC-ITSTPCTRD" "mTOFChi2TPC" "mTOFChi2TPCTRD" "mDeltaXEtaITSTPC-ITSTPCTRD" "mDeltaXEtaTPC" "mDeltaXEtaTPCTRD" "mDeltaZEtaITSTPC-ITSTPCTRD" "mDeltaZEtaTPC" "mDeltaZEtaTPCTRD" "DTimeTrk_sec00" "DTimeTrk_sec09" )
declare -a DigitsMONames=( "HitMap" "DecodingErrors" "OrbitVsCrate" )
declare -a PIDMONames=( "DeltaEvTimeTOFVsFT0ACSameBC" "DeltaEvTimeTOFVsFT0AC" "DeltaBCTOFFT0" "BetavsP_ITSTPC_t0FT0AC" "BetavsP_ITSTPC_t0TOF" "EvTimeTOF" "DeltatPiEvTimeMult_ITSTPC")

# Iterate the string array using for loop
for name in ${MatchingMONames[@]}; do
    python3 fetch_output.py qc_async/TOF/MO/MatchTrAll/$name -R $RUN --period $PERIOD --pass $PASS -o Run$RUN --downloadmode wget -v
    mv Run$RUN/qc_async/TOF/MO/MatchTrAll/$name/snapshot.root  Run$RUN/rootfiles/$name.root
done

for name in ${DigitsMONames[@]}; do
    declare -a newname=$(echo $name | tr / _)
    python3 fetch_output.py qc_async/TOF/MO/Digits/$name -R $RUN --period $PERIOD --pass $PASS -o Run$RUN --downloadmode wget -v
    mv Run$RUN/qc_async/TOF/MO/Digits/$name/snapshot.root  Run$RUN/rootfiles/$newname.root
done

for name in ${PIDMONames[@]}; do
    python3 fetch_output.py qc_async/TOF/MO/PID/$name -R $RUN --period $PERIOD --pass $PASS -o Run$RUN --downloadmode wget -v
    mv Run$RUN/qc_async/TOF/MO/PID/$name/snapshot.root  Run$RUN/rootfiles/$name.root
done

rm -rf Run$RUN/qc