#!/usr/bin/env python3

"""
Script to compare different runs and extract the resolution to check its stability
"""

if 1:
    import sys
    import os
    this_file_path = os.path.dirname(__file__)
    sys.path.append(this_file_path)
    print(this_file_path)
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/AO2D/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/utilities/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/")))
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, definenicepalette, make_color_range, draw_label
    from common import get_default_parser, wait_for_input

from ROOT import TFile, TF1, TObjArray, TH1F, TH1
import argparse
from plotDeltaTSlices import get_from_file


def process(histograms):
            draw_nice_canvas(i)
            hd = drawhisto(i)
            fun = TF1("fun", "gaus", -1000, 1000)
            hd.Fit(fun, "QNRWW")
            fun.Draw("SAME")
            draw_label(f"#mu = {fun.GetParameter(1):.2f} (ps)", 0.35, 0.85, 0.03)
            draw_label(f"#sigma = {fun.GetParameter(2):.2f} (ps)", 0.35, 0.8, 0.03)
            if i == "FT0A_minus_FT0C":
                value_ft0AC_resolution = fun.GetParameter(2)