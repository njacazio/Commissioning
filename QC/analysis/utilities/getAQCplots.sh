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
declare -a MatchingMONames=( "mEffPt_ITSTPC-ITSTPCTRD" "mEffPt_TPC" "mDeltaXEtaITSTPC-ITSTPCTRD" "mDeltaXEtaTPC" "mDeltaZEtaITSTPC-ITSTPCTRD" "mDeltaZEtaTPC" )
declare -a DigitsMONames=( "HitMap" )
declare -a PIDMONames=( "BetavsP_ITSTPC_t0FT0AC" "BetavsP_ITSTPC_t0TOF" "BetavsP_TPC_t0FT0AC" "BetavsP_TPC_t0TOF" "DeltaBCTOFFT0" "DeltaEvTimeTOFVsFT0AC" "DeltaEvTimeTOFVsFT0ACSameBC" "DeltatPi_ITSTPC_t0FT0AC" "DeltatPi_ITSTPC_t0TOF" "EvTimeTOF" "EvTimeTOFVsFT0AC" "EvTimeTOFVsFT0ACSameBC" "HadronMasses_ITSTPC_t0TOF" "HadronMassesvsP_ITSTPC_t0TOF" "HadronMasses_ITSTPC_t0FT0AC" "HadronMassesvsP_ITSTPC_t0FT0AC" )

# Iterate the string array using for loop
for name in ${MatchingMONames[@]}; do
    python3 fetch_output.py qc_async/TOF/MO/MatchingTOF/$name -R $RUN --period $PERIOD --pass $PASS -o Run$RUN --downloadmode wget -v
    mv Run$RUN/qc_async/TOF/MO/MatchingTOF/$name/snapshot.root  Run$RUN/rootfiles/$name.root
done

for name in ${DigitsMONames[@]}; do
    declare -a newname=$(echo $name | tr / _)
    python3 fetch_output.py qc_async/TOF/MO/TaskDigits/$name -R $RUN --period $PERIOD --pass $PASS -o Run$RUN --downloadmode wget -v
    mv Run$RUN/qc_async/TOF/MO/TaskDigits/$name/snapshot.root  Run$RUN/rootfiles/$newname.root
done

for name in ${PIDMONames[@]}; do
    python3 fetch_output.py qc_async/TOF/MO/TaskFT0TOF/$name -R $RUN --period $PERIOD --pass $PASS -o Run$RUN --downloadmode wget -v
    mv Run$RUN/qc_async/TOF/MO/TaskFT0TOF/$name/snapshot.root  Run$RUN/rootfiles/$name.root
done

rm -rf Run$RUN/qc