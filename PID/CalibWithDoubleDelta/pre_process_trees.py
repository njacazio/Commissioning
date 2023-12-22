#!/usr/bin/env python3

# from plotMakers import plotDeltaTVsEta
import numpy as np
import argparse
from ROOT import TFile, TChain, EnableImplicitMT, RDataFrame, gPad, TH1, TColor, TObjArray, gROOT, gStyle, TGraph, TF1, TGraphErrors, TH2F
from ROOT.RDF import TH3DModel, TH2DModel, TH1DModel
from numpy import sqrt
import time
import sys
import os
import tqdm
import inspect


sys.path.append(os.path.abspath("../PerformanceStudy/"))
sys.path.append(os.path.abspath("../QC/analysis/AO2D/"))
sys.path.append(os.path.abspath("../QC/analysis/utilities/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal, definenicepalette
    from common import warning_msg, wait_for_input
    from make_reso_with_ev_time import addDFToChain, makehisto, get_histogram, define_extra_columns


def main(input_file_name="/tmp/AO2D.root",
         positives=True,
         eta_pt_range=[1.3, 1.45],
         reference_momentum=[0.6, 0.7],
         max_files=-1,
         label=None,
         out_file_name="/tmp/TOFCALIB.root"):

    chain = TChain()
    if type(input_file_name) is list:
        nfiles = 0
        for f in tqdm.tqdm(input_file_name, bar_format="Looping on input files {l_bar}{bar:10}{r_bar}{bar:-10b}"):
            if max_files >= 0 and nfiles >= max_files:
                print("Reached max number of files", max_files)
                break
            nfiles += 1
            addDFToChain(f, chain)
        print("Using a total of", nfiles, "files")
    elif input_file_name.endswith(".root"):
        addDFToChain(input_file_name, chain)
    elif input_file_name.endswith(".txt"):
        with open("input_file_name", "r") as f:
            for line in f:
                addDFToChain(line, chain)

    # Definition of the histogram axes
    evtimeaxis = [1000, -2000, 2000]
    evtimediffaxis = [100, -1000, 1000]
    multaxis = [40, 0, 40]
    ptaxis = [1000, 0, 5]
    etaaxis = [32, -0.8, 0.8]
    phiaxis = [18, 0, 2 * np.pi]
    deltaaxis = [1000, -2000, 2000]
    tminustexpaxis = [1000, -2000, 2000]

    df = RDataFrame(chain)
    df = define_extra_columns(df)
    # Apply filters
    df = df.Filter("fTOFChi2<5")
    df = df.Filter("fTOFChi2>=0")
    if positives:
        df = df.Filter("fPtSigned>=0")  # only positive tracks
    else:
        df = df.Filter("fPtSigned<=0")  # only negative tracks
    df = df.Filter(f"fPt>{eta_pt_range[0]}").Filter(f"fPt<{eta_pt_range[1]}")

    if reference_momentum[0] >= reference_momentum[1]:
        raise ValueError("Reference momentum range is not valid", reference_momentum)

    # makehisto(df.Filter(f"fP > {reference_momentum[0]}").Filter(f"fP < {reference_momentum[1]}"),
    #           x="fEvTimeTOFMult", y="fDoubleDelta", xr=multaxis, yr=deltaaxis,
    #           tag="reference", title=f"#Delta#Deltat ref. {reference_momentum[0]:.1f} < #it{{p}} < {reference_momentum[1]:.1f} GeV/#it{{c}}")
    # Double delta
    # makehisto(df, x="fP", y="fDoubleDelta", xr=ptaxis, yr=deltaaxis, title="#Delta#Deltat vs p")
    # makehisto(df, x="fPt", y="fDoubleDelta", xr=ptaxis, yr=deltaaxis, title="#Delta#Deltat vs pT")
    # T - texp - TEv
    makehisto(df, x="fPt", xr=ptaxis)
    makehisto(df, x="fEta", xr=etaaxis)
    for i in ["Pi", "Ka", "Pr"]:
        # makehisto(df, x="fPt", y=f"Delta{i}TOF", xr=ptaxis, yr=deltaaxis, title=f"Delta{i}TOF vs pT")
        # makehisto(df, x="fPt", y=f"Delta{i}T0AC", xr=ptaxis, yr=deltaaxis, title=f"Delta{i}T0AC vs pT")
        makehisto(df, x="fEta", y=f"Delta{i}T0AC", xr=etaaxis, yr=deltaaxis,
                  title=f"Delta{i}T0AC vs Eta for {eta_pt_range[0]:.2f} < pT < {eta_pt_range[1]:.2f}")
    # makehisto(df.Filter("fPtSigned>=0"), x="fPt", y="DeltaPrTOF", xr=ptaxis, yr=deltaaxis, title="DeltaPrTOF vs pT", tag="Pos")
    # makehisto(df.Filter("fPtSigned<=0"), x="fPt", y="DeltaPrTOF", xr=ptaxis, yr=deltaaxis, title="DeltaPrTOF vs pT", tag="Neg")
    # for i in ["El", "Mu", "Ka", "Pr"]:
    #     part = {"El": "e", "Mu": "#mu", "Ka": "K", "Pr": "p"}[i]
    #     makehisto(df, x="fP", y="DeltaPi" + i, xr=ptaxis, yr=tminustexpaxis, yt="t_{exp}(#pi) - t_{exp}(%s)" % part, title="t_{exp}(#pi) - t_{exp}(%s)" % part)
    #     makehisto(df, x="fPt", y="DeltaPi" + i, xr=ptaxis, yr=tminustexpaxis, yt="t_{exp}(#pi) - t_{exp}(%s)" % part, title="t_{exp}(#pi) - t_{exp}(%s)" % part)
    # if 0:
    #     df = df.Filter(f"fPt>{minPt}")
    #     df = df.Filter(f"fPt<{maxPt}")
    # else:
    #     df = df.Filter(f"fP>{minPt}")
    #     df = df.Filter(f"fP<{maxPt}")
    makehisto(df, x="fPhi", y="DeltaPiT0AC", z="fEta", xr=phiaxis, yr=deltaaxis, zr=etaaxis)

    histograms = get_histogram()
    for i in histograms:
        draw_nice_canvas(i, logz="TH3" not in histograms[i].ClassName())
        histograms[i].Draw("col")
    update_all_canvases()
    input("Press enter to continue")

    print("Writing output to", out_file_name)
    fout = TFile(out_file_name, "RECREATE")
    fout.cd()
    for i in histograms:
        print("Writing", i)
        if not histograms[i]:
            print("Warning! Histogram", i, "is empty!")
            continue
        if "transpose" in histograms[i].GetName():
            histograms[i].Write(histograms[i].GetName().replace("transpose", "").replace("_copy", ""))
        else:
            histograms[i].Write()
    fout.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Input file name", nargs="+")
    parser.add_argument("--jobs", "-j", default=4, type=int, help="Number of multithreading jobs")
    args = parser.parse_args()
    EnableImplicitMT(args.jobs)
    main(input_file_name=args.filename)
