#!/usr/bin/env python3

"""
Script to compute the intrinsic TOF resolution from TOF skimmed data produced with the O2Physics
"""

import ROOT
from ROOT import TFile, TChain, TTree, TH1, o2, gInterpreter, TMath, EnableImplicitMT, gROOT, gPad, TColor, gStyle, TF1, TObjArray, gROOT, TH1F, TH2F
from ROOT.RDF import TH2DModel, TH1DModel, RSnapshotOptions
from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_label
from common import get_default_parser, set_verbose_mode, verbose_msg, is_verbose_mode
from debugtrack import *
import numpy as np
import os
from numpy import sqrt
import tqdm
import sys
import queue
import multiprocessing
import time
import pandas
import uproot
import awkward as ak


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


newhistograms = {"hDelta": TH2F("delta", "delta;Pt;#Delta", 1, 0.95, 1.05, 2000, -10000, 10000)}


def pre_pre_process_frame(filename_and_treename):
    start_time = time.process_time()
    filename = filename_and_treename[0]
    treename = filename_and_treename[1]
    structured_tree = uproot.open(filename)[treename]
    keys = list(structured_tree.keys())
    df = structured_tree.arrays(keys, library='pd')
    df = df[df["fLength"] > 0.1]  # Selecting tracks with TOF
    df = df[(df["fHasTRD"] == False) | (df["fLastTRDCluster"] >= 5)]  # Selecting tracks without TRD or with 5 TRD clusters
    grouped_df = df.groupby("fIndexCollisions")
    h = newhistograms["hDelta"]

    print("Tracks per collisions:", grouped_df.size().sum(), sep=" \n")
    for collision_index, df_in_collision in tqdm.tqdm(grouped_df, bar_format='         Collision index loop filtering {l_bar}{bar:10}{r_bar}{bar:-10b}'):
        df_reference = df_in_collision[(df_in_collision["fP"] > 0.95) & (df_in_collision["fP"] < 1.05)]
        reference_diff = []
        for trk_index, trk in df_in_collision.iterrows():
            reference_diff.append([])
            for trk_ref_index, trk_ref in df_reference.iterrows():
                if trk_index == trk_ref_index:
                    continue
                reference_diff[-1].append(trk["fTOFSignal"] - trk_ref["fTOFSignal"])
                # h.Fill(trk["fP"], trk["fTOFSignal"] - trk_ref["fTOFSignal"])
        df_in_collision["Diff"] = reference_diff
        print(df_in_collision)
        # dataframe = ROOT.RDF.FromNumpy(df_in_collision["Diff"])

    return {"ProcessingTime": time.process_time() - start_time, "hDelta": h}


def pre_process_frame(filename,
                      treename,
                      outpath="/tmp/toftrees2",
                      overwrite=True,
                      make_histo=False):
    dataframe = ROOT.RDataFrame(treename, filename)
    df_name = treename.split("/")[0]
    dataframe = dataframe.Define("ExpTimePi", "ComputeExpectedTimePi(fTOFExpMom, fLength)")
    dataframe = dataframe.Define("TMinusTExpPi", "fTOFSignal - ExpTimePi")
    dataframe = dataframe.Define("DeltaPi", "TMinusTExpPi - fEvTimeT0AC")
    dataframe = dataframe.Define("HasTOF", "fLength > 0")
    # dataframe = dataframe.Define("fNSigmaPi", "fPt")
    # dataframe = dataframe.Define("BetaEvTimeTOF", "fLength / (fTOFSignal - fEvTimeTOF) / kCSPEED")
    # dataframe = dataframe.Define("BetaEvTimeT0AC", "fLength / (fTOFSignal - fEvTimeT0AC) / kCSPEED")
    # dataframe = dataframe.Filter("fP < 10")
    # dataframe = dataframe.Filter("fP > 0.5")
    # dataframe = dataframe.Filter("fPt < 1.1")
    # dataframe = dataframe.Filter("fPt > 1.0")
    # dataframe = dataframe.Filter("fTOFChi2 < 3")
    # dataframe = dataframe.Filter("abs(fEta) < 0.1")
    dataframe = dataframe.Filter("fTOFSignal > 0")
    dataframe = dataframe.Filter("fTOFChi2 > 0")
    dataframe = dataframe.Filter("HasTOF == true")
    dataframe = dataframe.Filter("fHasTRD == 0")
    ntracks = dataframe.Count().GetValue()
    verbose_msg("Tracks in sample", df_name, f": {ntracks}")
    if ntracks <= 0:
        del dataframe
        return

    # collision_indices = dataframe.AsNumpy(["fIndexCollisions"])
    # # print(collision_indices)
    # collision_indices = np.unique(collision_indices["fIndexCollisions"])
    # # print(collision_indices)
    if make_histo:
        ptbins = [100, 0, 5]
        deltapibins = [1000, -1000, 1000]
        makehisto(input_dataframe=dataframe, x="fP", y="DeltaPi", xr=ptbins, yr=deltapibins, xt="p (GeV/c)", yt="#Delta#pi (ps)")

    out_path = os.path.join(outpath, os.path.basename(filename).replace(".root", ""))
    reference_tracks = dataframe.Filter("fP > 0.95 && fP < 1.05").AsNumpy(["TMinusTExpPi", "fP", "fPt", "fEta", "fPhi", "rdfentry_", "fIndexCollisions"])
    for trk_index, rdfentry_ in enumerate(reference_tracks["rdfentry_"]):
        col_index = reference_tracks["fIndexCollisions"][trk_index]
        verbose_msg("Processing collision", col_index, "track", trk_index, "of", len(reference_tracks["rdfentry_"]), "in", df_name)
        out_file = os.path.join(out_path, f"intermediate_{df_name}_collid{col_index}_reftrk{rdfentry_}.root")
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
        if os.path.exists(out_file) and not overwrite:
            verbose_msg("File", out_file, "exists, skipping:", out_file)
            continue
        df_wrt_to_reference = dataframe.Filter(f"fIndexCollisions == {col_index:.0f} && rdfentry_ != {rdfentry_:.0f}")
        verbose_msg("Size of df_wrt_to_reference:", df_wrt_to_reference.Count().GetValue(), "wrt", dataframe.Count().GetValue())
        if dataframe.Count().GetValue() <= 0:
            continue
        df_wrt_to_reference = df_wrt_to_reference.Define("DeltaInEvent", "TMinusTExpPi - {}".format(reference_tracks["TMinusTExpPi"][trk_index]))
        df_wrt_to_reference = df_wrt_to_reference.Define("DeltaP", "fP - {}".format(reference_tracks["fP"][trk_index]))
        df_wrt_to_reference = df_wrt_to_reference.Define("DeltaPt", "fPt - {}".format(reference_tracks["fPt"][trk_index]))
        df_wrt_to_reference = df_wrt_to_reference.Define("DeltaEta", "fEta - {}".format(reference_tracks["fEta"][trk_index]))
        df_wrt_to_reference = df_wrt_to_reference.Define("DeltaPhi", "fPhi - {}".format(reference_tracks["fPhi"][trk_index]))
        df_wrt_to_reference.Snapshot("O2skimmedtof", out_file)
        # dataframe.Snapshot("O2skimmedtof", out_file, ["fP", "DeltaInEvent"])
        if make_histo:
            makehisto(input_dataframe=dataframe, x="fP", y="DeltaInEvent", xr=ptbins, yr=deltapibins, xt="p (GeV/c)", yt="#DeltaRef (ps)")
        del df_wrt_to_reference
    del reference_tracks
    del dataframe


def post_process_frame(dataframe):
    gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
    ptbins = [100, 0, 5]
    deltapibins = [1000, -1000, 1000]
    before_cuts = dataframe.Count().GetValue()
    # dataframe = dataframe.Filter("TMath::Abs(DeltaEta) < 0.5")
    # dataframe = dataframe.Filter("TMath::Abs(DeltaEta) < 0.5")
    # dataframe = dataframe.Filter("TMath::Abs(DeltaPhi) < 0.5")
    # dataframe = dataframe.Filter("TMath::Abs(DeltaP) < 0.1")
    # dataframe = dataframe.Filter("fHasTRD == 0 || fLastTRDCluster >= 5")
    dataframe = dataframe.Filter("fHasTRD == 0")
    print("Post processing", dataframe.Count().GetValue(), "tracks after cuts, before:", before_cuts)
    h2 = makehisto(input_dataframe=dataframe, x="DeltaEta", y="DeltaInEvent", xr=[100, -1, 1], yr=deltapibins,
                   xt="#Delta_{#eta}", yt="#Delta(#pi) - #Delta(#pi)_{ref} (ps)", draw=True)
    h2 = makehisto(input_dataframe=dataframe, x="DeltaPhi", y="DeltaInEvent", xr=[100, -1, 1], yr=deltapibins,
                   xt="#Delta_{#varphi}", yt="#Delta(#pi) - #Delta(#pi)_{ref} (ps)", draw=True)
    h2 = makehisto(input_dataframe=dataframe, x="DeltaP", y="DeltaInEvent", xr=[100, -1, 1], yr=deltapibins,
                   xt="#Delta_{#it{p}} (GeV/c)", yt="#Delta(#pi) - #Delta(#pi)_{ref} (ps)", draw=True)
    h2 = makehisto(input_dataframe=dataframe, x="fP", y="DeltaInEvent", xr=ptbins, yr=[2000, -10000, 10000],
                   xt="#it{p} (GeV/c)", yt="#Delta(#pi) - #Delta(#pi)_{ref} (ps)", draw=True)
    fitres = TObjArray()
    proj_bin = [0.95, 1.049]
    b = [h2.GetXaxis().FindBin(proj_bin[0]),
         h2.GetXaxis().FindBin(proj_bin[1])]

    h2.FitSlicesY(TF1("fgaus", "gaus", -300, 300), -1, -1, 0, "QNR", fitres)
    fitres[1].Draw("same")
    fitres[2].Draw("same")
    for i in fitres:
        i.SetLineWidth(2)

    hp = h2.ProjectionY("hp", *b)
    hp.Rebin(4)
    hp.SetBit(TH1.kNoTitle)
    # hp.SetBit(TH1.kNoStats)
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
         process_in_parallel=True,
         jobs=1,
         overwrite=False,
         n_df_to_process=1):
    if len(filenames) > 1 and process_in_parallel and do_preprocessing:
        with open("/tmp/listofinput.txt", "w") as f:
            for i in filenames:
                f.write(f"{sys.argv[0]} {i} --jobs 1 --preprocess\n")
        print("Processing in parallel")
        # os.system(f"time parallel -j 4 python {sys.argv[0]} --preprocess --postprocess --filelist listofinput.txt --file {{}}")
        print(f"time parallel --progress -j {jobs} -a /tmp/listofinput.txt\n")
        return

    if do_preprocessing:

        EnableImplicitMT(5)
        # EnableImplicitMT(jobs)
        # First build the list of TTrees
        start_time = time.process_time()
        trees = {}
        for i in filenames:
            trees[i] = get_trees_from_file(file_name=i, print_branch_names=(i == filenames[0]))
        verbose_msg(f"Found {len(trees)} files with {sum([len(trees[i]) for i in trees])} trees in {time.process_time() - start_time:.2f} s")
        # Linearize it
        list_of_trees = []
        do_break = False
        for i in trees:
            for j in trees[i]:
                list_of_trees.append((i, j))
                if n_df_to_process > 0 and len(list_of_trees) >= n_df_to_process:
                    do_break = True
                    break
            if do_break:
                break

        if jobs > 1:
            try:
                with multiprocessing.Pool(processes=jobs) as pool:
                    tqdm.tqdm(pool.imap(pre_pre_process_frame, list_of_trees),
                              total=len(list_of_trees),
                              bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
            except KeyboardInterrupt:
                print("Keyboard interrupt")
        else:
            results = []
            for i in tqdm.tqdm(list_of_trees, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'):
                try:
                    results.append(pre_pre_process_frame(i))
                except KeyboardInterrupt:
                    print("Keyboard interrupt")
                    break
            # print(f"Total processing time: {total_processing_time:.2f} s")
            for i in newhistograms:
                can = draw_nice_canvas(f"can{i}", logz=True)
                newhistograms[i].Draw("COLZ")
                can.Update()
            input("Press enter to continue")
        for i in histograms:
            draw_nice_canvas(i, logz=True)
            histograms[i].Draw("COLZ")

    if do_postprocessing:
        EnableImplicitMT(jobs)
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
    parser.add_argument("--jobs", "-j", default=4, type=int, help="Number of jobs to run with")
    parser.add_argument("--n_df_to_process", "-n", default=-1, type=int, help="Number of DFs to process")
    parser.add_argument("--overwrite", "-o", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()
    set_verbose_mode(args)
    main(args.filenames,
         do_preprocessing=args.preprocess,
         do_postprocessing=args.postprocess,
         jobs=args.jobs,
         n_df_to_process=args.n_df_to_process,
         overwrite=args.overwrite)
