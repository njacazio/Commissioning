#!/usr/bin/env python3

"""
Script to compute the TOF resolution used in analysis by using the TOF PID QA output
"""

import ROOT
from ROOT import TFile, TChain, TTree, TH1, o2, gInterpreter, TMath, EnableImplicitMT, gROOT, gPad, TColor, gStyle, TF1
from ROOT.RDF import TH2DModel, TH1DModel
from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_label
from common import get_default_parser, set_verbose_mode, verbose_msg, is_verbose_mode
from debugtrack import *
from intrinsic_resolution import get_trees_from_file, makehisto
import numpy as np
import os
import tqdm
import sys
import queue
import subprocess


def produce_qa_output(input_aods):
    executables = ["o2-analysis-track-propagation",
                   "o2-analysis-trackselection",
                   "o2-analysis-event-selection",
                   "o2-analysis-track-propagation",
                   "o2-analysis-pid-tof-base",
                #    "o2-analysis-pid-tof-beta",
                #    "o2-analysis-pid-tof-qa-beta",
                   "o2-analysis-pid-tof-full",
                   "o2-analysis-pid-tof-qa-evtime",
                   "o2-analysis-pid-tof-qa",
                   "o2-analysis-ft0-corrected-table",
                   "o2-analysis-timestamp"]
    cfg_json = os.path.abspath("config.json")
    options = f"\"-b --shm-segment-size 16000000000 --aod-memory-rate-limit 1000000000 --readers 1 --time-limit 300 --configuration json://{cfg_json}\""
    input_aods = input_aods.strip()
    if input_aods.endswith(".txt"):
        input_aods = f"@{input_aods}"
    with open("/tmp/o2runner.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("\n\n")
        f.write(f"ROPT={options}\n\n")
        for i in executables:
            cmd = f"{i} $ROPT"
            if i == executables[0]:
                cmd += f" --aod-file {input_aods}"
            if i != executables[-1]:
                cmd += " | \\"
            f.write(f"{cmd}\n")
        f.write("\n\n")

    subprocess.run("chmod +x /tmp/o2runner.sh".split(), capture_output=True)
    subprocess.run("/tmp/o2runner.sh".split())
    # run_result = subprocess.run("./o2runner.sh".split(), capture_output=True)
    # print(run_result)


def main(filename):
    if len(filename) == 1:
        filename = filename[0]
    produce_qa_output(filename)


if __name__ == "__main__":
    parser = get_default_parser(description=__doc__)
    parser.add_argument("filenames", nargs="+", help="Input files")
    args = parser.parse_args()
    set_verbose_mode(args)
    main(args.filenames)
