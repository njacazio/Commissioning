#!/usr/bin/env python3

"""
Script to compute the intrinsic TOF resolution from TOF skimmed data produced with the O2Physics
"""

import ROOT
from ROOT import TFile, TChain, TTree, TH1, o2, gInterpreter, TMath, EnableImplicitMT, gROOT, gPad, TColor, gStyle, TF1, TObjArray, gROOT
from ROOT.RDF import TH2DModel, TH1DModel
from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_label
from common import get_default_parser, set_verbose_mode, verbose_msg, is_verbose_mode
from debugtrack import *
import numpy as np
import os
from numpy import sqrt
import tqdm
import sys
import queue


histograms = {}
histomodels = {}


def makehisto(input_dataframe,
              x,
              y=None,
              xr=None,
              yr=None,
              xt=None,
              yt=None,
              extracut=None,
              logx=False,
              draw=False,
              draw_logy=False,
              extracut_to_name=True,
              opt="COL"):
    n = f"{x}"
    if y is not None:
        n = f"{y}_vs_{x}"
    if extracut is not None and extracut_to_name:
        n = f"{n}_{extracut}"
    add_mode = False
    if n in histograms:
        add_mode = True
    else:
        verbose_msg("Making histogram", n, "in", xr, "vs", yr, "with xt =", xt, "and yt =", yt, "logx", logx)

    df = input_dataframe
    if extracut is not None:
        if type(extracut) is list:
            for i in extracut:
                df = df.Filter(i)
        else:
            df = df.Filter(extracut)
        # print("Tracks in sample after cut:", df.Count().GetValue())
    if xr is not None and add_mode is False:
        if logx:
            themin = xr[1]
            if themin <= 0.:
                themin = 0.01
            themax = xr[2]
            logmin = np.log10(themin)
            logmax = np.log10(themax)
            nbins = xr[0]
            logdelta = (logmax - logmin) / (float(nbins))
            binEdges = []
            for i in range(nbins):
                nextEdge = 10**(logmin + i * logdelta)
                binEdges.append(nextEdge)
            binEdges = np.array(binEdges)
            xr = [xr[0]-1, binEdges]
    if y is not None:
        if add_mode:
            model = histomodels[n]
        else:
            model = TH2DModel(n, n, *xr, *yr)
        h = df.Histo2D(model, x, y)
        if add_mode:
            histograms[n].Add(h.GetPtr())
            return
        else:
            histomodels[n] = model
            histograms[n] = h
    else:
        if xr is not None:
            if add_mode:
                model = histomodels[n]
            else:
                model = TH1DModel(x, x, *xr)
            h = df.Histo1D(model, x)
            if add_mode:
                histograms[n].Add(h.GetPtr())
                return
            histograms[n] = h
        else:
            h = df.Histo1D(x)
            if add_mode:
                histograms[n].Add(h.GetPtr())
                return
            histograms[n] = h
    h.SetBit(TH1.kNoTitle)
    h.SetBit(TH1.kNoStats)
    h.GetXaxis().SetTitle(x)
    if y is not None:
        h.GetYaxis().SetTitle(y)
    if xt is not None:
        h.GetXaxis().SetTitle(xt)
    if yt is not None:
        h.GetYaxis().SetTitle(yt)
    set_nice_frame(h)
    if draw:
        draw_nice_canvas(n, logy=draw_logy)
        h.Draw(opt)
        gPad.Modified()
        gPad.Update()
    return h


def pre_process_frame(filename,
                      treename,
                      outpath="/tmp/toftrees2",
                      overwrite=False,
                      make_histo=False):
    dataframe = ROOT.RDataFrame(treename, filename)
    treename = treename.split("/")[0]
    dataframe = dataframe.Define("ExpTimePi", "ComputeExpectedTimePi(fTOFExpMom, fLength)")
    dataframe = dataframe.Define("TMinusTExpPi", "fTOFSignal - ExpTimePi")
    dataframe = dataframe.Define("DeltaPi", "TMinusTExpPi - fEvTimeT0AC")
    dataframe = dataframe.Define("HasTOF", "fLength > 0")
    # dataframe = dataframe.Define("fNSigmaPi", "fPt")
    # dataframe = dataframe.Define("BetaEvTimeTOF", "fLength / (fTOFSignal - fEvTimeTOF) / kCSPEED")
    # dataframe = dataframe.Define("BetaEvTimeT0AC", "fLength / (fTOFSignal - fEvTimeT0AC) / kCSPEED")
    # dataframe = dataframe.Filter("fP < 10")
    dataframe = dataframe.Filter("fP > 0.5")
    # dataframe = dataframe.Filter("fPt < 1.1")
    # dataframe = dataframe.Filter("fPt > 1.0")
    dataframe = dataframe.Filter("fTOFSignal > 0")
    dataframe = dataframe.Filter("fTOFChi2 > 0")
    # dataframe = dataframe.Filter("fTOFChi2 < 3")
    # dataframe = dataframe.Filter("abs(fEta) < 0.1")
    dataframe = dataframe.Filter("HasTOF == true")
    ntracks = dataframe.Count().GetValue()
    verbose_msg("Tracks in sample:", ntracks)
    if ntracks <= 0:
        return

    collision_indices = dataframe.AsNumpy(["fIndexCollisions"])
    # print(collision_indices)
    collision_indices = np.unique(collision_indices["fIndexCollisions"])
    # print(collision_indices)
    if make_histo:
        ptbins = [100, 0, 5]
        deltapibins = [1000, -1000, 1000]
        makehisto(input_dataframe=dataframe, x="fP", y="DeltaPi", xr=ptbins, yr=deltapibins, xt="p (GeV/c)", yt="#Delta#pi (ps)")

    out_path = os.path.join(outpath, os.path.basename(filename).replace(".root", ""))
    if not overwrite and os.path.exists(out_path) and len(os.listdir(out_path)) == len(collision_indices):
        verbose_msg("All files exist, skipping:", filename)
        return
    for i in collision_indices:
        out_file = os.path.join(out_path, f"intermediate_{treename}_collid{i}.root")
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
        if os.path.exists(out_file) and not overwrite:
            verbose_msg("File exists, skipping:", out_file)
            continue
        df_same_collision = dataframe.Filter(f"fIndexCollisions == {i}")
        ref_index = 0
        reference_track = df_same_collision.Range(ref_index, ref_index).AsNumpy(["TMinusTExpPi", "rdfentry_"])
        reference_time = reference_track["TMinusTExpPi"][ref_index]
        reference_index = reference_track["rdfentry_"][ref_index]
        df_same_collision = df_same_collision.Filter(f"rdfentry_ != {reference_index}")
        df_same_collision = df_same_collision.Define("DeltaInEvent", f"TMinusTExpPi - {reference_time}")
        if df_same_collision.Count().GetValue() <= 0:
            continue
        df_same_collision.Snapshot("O2skimmedtof", out_file, ["fP", "DeltaInEvent"])
        if make_histo:
            makehisto(input_dataframe=df_same_collision, x="fP", y="DeltaInEvent", xr=ptbins, yr=deltapibins, xt="p (GeV/c)", yt="#DeltaRef (ps)")
        del df_same_collision
    del dataframe


def post_process_frame(dataframe):
    gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")
    ptbins = [100, 0, 5]
    deltapibins = [1000, -1000, 1000]
    print("Post processing", dataframe.Count().GetValue(), "tracks")
    h2 = makehisto(input_dataframe=dataframe, x="fP", y="DeltaInEvent", xr=ptbins, yr=deltapibins,
                   xt="p (GeV/c)", yt="#Delta(#pi) - #Delta(#pi)_{ref} (ps)", draw=True)
    fitres = TObjArray()
    proj_bin = [0.5, 2.2]
    b = [h2.GetXaxis().FindBin(proj_bin[0]), h2.GetXaxis().FindBin(proj_bin[1])]

    h2.FitSlicesY (TF1("fgaus", "gaus", -300, 300), *b, 0, "QNR", fitres)
    fitres[1].Draw("same")
    fitres[2].Draw("same")

    hp = h2.ProjectionY("hp", *b)
    hp.Rebin(4)
    hp.SetBit(TH1.kNoTitle)
    hp.SetBit(TH1.kNoStats)
    fgaus = TF1("fgaus", "gaus", -600, 600)
    fgaus.SetParameter(0, hp.GetMaximum())
    fgaus.SetParameter(1, hp.GetXaxis().GetBinCenter(hp.GetMaximumBin()))
    draw_nice_canvas("reso")
    hp.Draw()
    hp.Fit(fgaus, "QN", "", -200, 200)
    fgaus.Draw("same")
    draw_label(f"{h2.GetXaxis().GetTitle()} [{h2.GetXaxis().GetBinLowEdge(b[0]):.2f}, {h2.GetXaxis().GetBinUpEdge(b[1]):.2f}]",
               x=0.95, y=0.96, align=31)
    draw_label(f"#sigma = {fgaus.GetParameter(2):.2f} ps", x=0.91, y=0.9, align=31)
    draw_label(f"#sigma/#sqrt{{2}} = {fgaus.GetParameter(2)/sqrt(2):.2f} ps", x=0.91, y=0.85, align=31)


def get_trees_from_file(file_name="/tmp/toftrees/AnalysisResults_trees_V0S_0.root",
                        tree_name="O2skimmedtof",
                        print_branch_names=False):
    verbose_msg("Getting trees from", file_name)
    f = TFile(file_name, "READ")
    subdirs = []
    for i in f.GetListOfKeys():
        if i.GetName().startswith("DF_"):
            subdirs.append(f"{i.GetName()}/{tree_name}")
    if print_branch_names and is_verbose_mode():
        f.Get(subdirs[0]).Print()
        for i in f.Get(subdirs[0]).GetListOfBranches():
            print(i.GetName())
    f.Close()
    # print(subdirs)
    return subdirs


def main(filenames,
         do_preprocessing=True,
         do_postprocessing=False,
         process_in_parallel=True):
    if len(filenames) > 1 and process_in_parallel and do_preprocessing:
        with open("/tmp/listofinput.txt", "w") as f:
            for i in filenames:
                f.write(f"{sys.argv[0]} {i} --preprocess\n")
        print("Processing in parallel")
        # os.system(f"time parallel -j 4 python {sys.argv[0]} --preprocess --postprocess --filelist listofinput.txt --file {{}}")
        print(f"time parallel --progress -j 4 -a /tmp/listofinput.txt\n")
        return

    if do_preprocessing:
        # First build the list of TTrees
        trees = {}
        for i in filenames:
            trees[i] = get_trees_from_file(file_name=i, print_branch_names=(i == filenames[0]))
        # Linearize it
        list_of_trees = []
        for i in trees:
            for j in trees[i]:
                list_of_trees.append((i, j))
        for i in tqdm.tqdm(list_of_trees, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'):
            try:
                pre_process_frame(filename=i[0], treename=i[1])
            except KeyboardInterrupt:
                print("Keyboard interrupt")
                break
        for i in histograms:
            draw_nice_canvas(i, logz=True)
            histograms[i].Draw("COLZ")

    if do_postprocessing:
        EnableImplicitMT(5)
        post_process_frame(ROOT.RDataFrame("O2skimmedtof", filenames))

    update_all_canvases()
    if not gROOT.IsBatch() and len(histograms) > 0:
        input("Press enter to continue")
    else:
        print("Batch mode, exiting")


if __name__ == "__main__":
    parser = get_default_parser(description=__doc__)
    parser.add_argument("filenames", nargs="+", help="Input files")
    parser.add_argument("--preprocess", action="store_true", help="Run the preprocessing")
    parser.add_argument("--postprocess", action="store_true", help="Run the postprocessing")
    args = parser.parse_args()
    set_verbose_mode(args)
    main(args.filenames, do_preprocessing=args.preprocess, do_postprocessing=args.postprocess)
