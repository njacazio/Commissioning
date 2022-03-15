#!/usr/bin/env python3

import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
import argparse
import fetch_output
import os
from ROOT import gROOT
import os

gROOT.LoadMacro("draw.C")
import ROOT

def main(timestamp, runnumber):
    to_download = [ "qc/TOF/MO/TaskRaw/hSlotPartMask", "qc/TOF/MO/TaskRaw/hSlotPartMask", "qc/TOF/MO/TaskRaw/hHits", "qc/TOF/MO/TaskRaw/hIndexEOIsNoise", "qc/TOF/MO/TaskRaw/hIndexEOInTimeWin", "qc/TOF/MO/TaskRaw/hIndexEOHitRate", "qc/TOF/MO/TaskDigits/TOFRawHitMap", "qc/TOF/MO/TaskDigits/TOFRawsMulti", "qc/TOF/MO/TaskDigits/OrbitDDL", "qc/TOF/MO/TaskDigits/TOFRawsTime", "qc/TOF/MO/TOFTrendingHits/mean_of_hits"]
    for i in to_download:
        fetch_output.main(ccdb_path=i,
                  timestamp=timestamp,
                  out_path=f"Run{runnumber}",
                  host="qcdb.cern.ch:8083",
                  show=False,
                  verbose=False)
        os.rename(f"Run{runnumber}/{i}/snapshot.root",
        f"Run{runnumber}/{os.path.basename(i)}.root")

    ROOT.draw(f"{runnumber}")
    input("Press Enter to continue...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot basic TOF-QC plots"
        "Basic example: `python3 plotQC.py -t 1635741378837 -r 505720`")
    parser.add_argument('--timestamp', "-t",
                        type=int,
                        default=-1,
                        help='Timestamp of the objects on qcdb, by default -1 (latest)')
    parser.add_argument('--runnumber', "-r",
                        type=int,
                        default=0,
                        help='Run number, by default 0')

    args = parser.parse_args()

    main(timestamp=args.timestamp,runnumber=args.runnumber)
  