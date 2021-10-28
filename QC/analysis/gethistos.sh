#! /usr/bin/env bash

RUN="505285"
SLOT="1635384636541"
HITS="1635384636658"
NOISE="1635384636639"
CHANNELS="1635384636589"
RATE="1635384637184"
HITMAP="1635384636261"
MULTI="1635384636222"
ORBITDDL="1635384636274"
RAWTIME="1635384636236"
TREND="1635384640563"

python3 fetch_output.py qc/TOF/MO/TaskRaw/hSlotPartMask -t $SLOT
mv Run$RUN/qc/TOF/MO/TaskRaw/hSlotPartMask/snapshot.root  Run$RUN/hSlotPartMask.root

python3 fetch_output.py qc/TOF/MO/TaskRaw/hHits -t $HITS
mv Run$RUN/qc/TOF/MO/TaskRaw/hHits/snapshot.root  Run$RUN/hHits.root

python3 fetch_output.py qc/TOF/MO/TaskRaw/hIndexEOIsNoise -t $NOISE
mv Run$RUN/qc/TOF/MO/TaskRaw/hIndexEOIsNoise/snapshot.root  Run$RUN/hIndexEOIsNoise.root

python3 fetch_output.py qc/TOF/MO/TaskRaw/hIndexEOInTimeWin -t $CHANNELS
mv Run$RUN/qc/TOF/MO/TaskRaw/hIndexEOInTimeWin/snapshot.root  Run$RUN/hIndexEOInTimeWin.root

python3 fetch_output.py qc/TOF/MO/TaskRaw/hIndexEOHitRate -t $RATE
mv Run$RUN/qc/TOF/MO/TaskRaw/hIndexEOHitRate/snapshot.root  Run$RUN/hIndexEOHitRate.root

python3 fetch_output.py qc/TOF/MO/TaskDigits/TOFRawHitMap -t $HITMAP
mv Run$RUN/qc/TOF/MO/TaskDigits/TOFRawHitMap/snapshot.root  Run$RUN/TOFRawHitMap.root

python3 fetch_output.py qc/TOF/MO/TaskDigits/TOFRawsMulti -t $MULTI
mv Run$RUN/qc/TOF/MO/TaskDigits/TOFRawsMulti/snapshot.root  Run$RUN/TOFRawsMulti.root

python3 fetch_output.py qc/TOF/MO/TaskDigits/OrbitDDL -t $ORBITDDL
mv Run$RUN/qc/TOF/MO/TaskDigits/OrbitDDL/snapshot.root  Run$RUN/OrbitDDL.root

python3 fetch_output.py qc/TOF/MO/TaskDigits/TOFRawsTime -t $ORBITDDL
mv Run$RUN/qc/TOF/MO/TaskDigits/TOFRawsTime/snapshot.root  Run$RUN/TOFRawsTime.root

python3 fetch_output.py qc/TOF/MO/TOFTrendingHits/mean_of_hits -t $TREND
mv Run$RUN/qc/TOF/MO/TOFTrendingHits/mean_of_hits/snapshot.root  Run$RUN/mean_of_hits.root

root -l draw.C\(\"$RUN\"\)

rm -rf Run$RUN/qc
	