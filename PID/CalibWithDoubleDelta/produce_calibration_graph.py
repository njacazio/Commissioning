#!/usr/bin/env python3


"""
Produce the calibration graph
"""

if 1:
    import sys
    import os
    this_file_path = os.path.dirname(__file__)
    sys.path.append(this_file_path)
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/AO2D/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/utilities/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../PerformanceStudy/plotMakers/")))
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, definenicepalette, make_color_range, draw_label
    from common import get_default_parser

from ROOT import TFile, TF1, TObjArray, TGraph
import argparse
from plotDeltaTVsEta import process_phiintegrated

definenicepalette()


def main(fnames=["/tmp/TOFCALIB_pos_pt1.30_1.45.root", "/tmp/TOFCALIB_neg_pt1.30_1.45.root"]):
    def do_one(fname):
        print(fname)
        h_phi_integrated = []
        fin = TFile(fname, "READ")
        for i in fin.GetListOfKeys():
            if "DeltaPiT0AC_vs_fEta" in i.GetName():
                h_phi_integrated.append(fin.Get(i.GetName()))
        mean, sigma = process_phiintegrated(h_phi_integrated)

        gmean = TGraph()
        gmean.SetName("gmean")
        for i in range(1, mean.GetNbinsX()+1):
            if i == 1:
                gmean.AddPoint(mean.GetXaxis().GetBinLowEdge(i), mean.GetBinContent(i))
            elif i == mean.GetNbinsX():
                gmean.AddPoint(mean.GetXaxis().GetBinUpEdge(i), mean.GetBinContent(i))
            else:
                gmean.AddPoint(mean.GetXaxis().GetBinCenter(i), mean.GetBinContent(i))
        gmean.Draw("LPsame")
        draw_nice_canvas("sigma", replace=False)
        sigma.Draw()
        outname = fname.replace(".root", "gmean.root")
        print("Writing to", outname)
        gmean.Clone("ccdb_object").SaveAs(outname)
        return mean, sigma, h_phi_integrated[0], gmean

    for i in fnames:
        do_one(i)

    input("Press enter to continue")


main()
