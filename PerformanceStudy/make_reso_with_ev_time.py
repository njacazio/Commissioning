#!/usr/bin/env python3

import numpy as np
import argparse
from ROOT import TFile, TChain, EnableImplicitMT, RDataFrame, gPad, TH1, TColor, TObjArray, gROOT, gStyle, TGraph
from ROOT.RDF import TH2DModel, TH1DModel
from numpy import sqrt
import sys
import os
sys.path.append(os.path.abspath("../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label


if 1:
    NRGBs = 5
    NCont = 256
    stops = np.array([0.00, 0.30, 0.61, 0.84, 1.00])
    red = np.array([0.00, 0.00, 0.57, 0.90, 0.51])
    green = np.array([0.00, 0.65, 0.95, 0.20, 0.00])
    blue = np.array([0.51, 0.55, 0.15, 0.00, 0.10])
    TColor.CreateGradientColorTable(NRGBs,
                                    stops, red, green, blue, NCont)
    gStyle.SetNumberContours(NCont)
    gStyle.SetPalette(55)


def addDFToChain(input_file_name, chain):
    f = TFile(input_file_name, "READ")
    lk = f.GetListOfKeys()
    for i in lk:
        dfname = i.GetName()
        if "DF_" not in dfname:
            continue
        t = f.Get(f"{dfname}/O2deltatof").GetListOfBranches()
        hasit = False
        for i in t:
            if i.GetName() == "fEvTimeTOFMult":
                hasit = True
                break
        if not hasit:
            return
        tname = "{}?#{}/O2deltatof".format(input_file_name, dfname)
        chain.Add(tname)


EnableImplicitMT(2)


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
        print("Making histogram", n, "in", xr, "vs", yr, "with xt =", xt, "and yt =", yt, "logx", logx)

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


def pre_process(input_file_name,
                maxfiles=-1,
                minP=0.6,
                maxP=0.7):
    chain = TChain()
    if type(input_file_name) is list:
        nfiles = 0
        for f in input_file_name:
            if maxfiles >= 0 and nfiles > maxfiles:
                break
            nfiles += 1
            addDFToChain(f, chain)
        print("Using a total of", nfiles, "files")
    elif (input_file_name.endswith(".root")):
        addDFToChain(input_file_name, chain)
    elif (input_file_name.endswith(".txt")):
        with open("input_file_name", "r") as f:
            for line in f:
                addDFToChain(line, chain)
    evtimeaxis = [1000, -2000, 2000]
    multaxis = [40, 0, 40]
    ptaxis = [100, 0, 5]
    deltaaxis = [1000, -2000, 2000]

    df = RDataFrame(chain)
    # df = df.Filter("fEta>0.3")
    # df = df.Filter("fEta<0.4")
    # df = df.Filter("fPhi>0.3")
    # df = df.Filter("fPhi<0.4")
    df = df.Filter("fTOFChi2<5")
    df = df.Filter("fTOFChi2>=0")
    df = df.Define("DeltaPiTOF", "fDeltaTPi-fEvTimeTOF")
    df = df.Define("DeltaPiT0AC", "fDeltaTPi-fEvTimeT0AC")
    for i in ["El", "Mu", "Ka", "Pr"]:
        df = df.Define(f"DeltaPi{i}", f"fDeltaTPi-fDeltaT{i}")

    makehisto(df, "fDoubleDelta", "fPt", deltaaxis, ptaxis, xt="#Delta#Delta (ps)", yt="#it{p}_{T} (GeV/#it{c})").SetTitle("#Delta#Delta vs pT")
    for i in ["El", "Mu", "Ka", "Pr"]:
        part = {"El": "e", "Mu": "#mu", "Ka": "K", "Pr": "p"}[i]
        makehisto(df, "DeltaPi"+i, "fPt", deltaaxis, ptaxis).SetTitle("t_{exp}(#pi) - t_{exp}(%s)" % part)
    df = df.Filter(f"fP>{minP}")
    df = df.Filter(f"fP<{maxP}")

    makehisto(df, "fEvTimeTOFMult", "fEvTimeT0AC", multaxis, evtimeaxis).SetTitle("T0AC ev. time")
    makehisto(df, "fEvTimeTOFMult", "fEvTimeTOF", multaxis, evtimeaxis).SetTitle("TOF ev. time")
    makehisto(df, "fEvTimeTOFMult", "fDoubleDelta", multaxis, deltaaxis, "TOF ev. mult.", "#Delta#Delta (ps)").SetTitle("#Delta#Delta")
    makehisto(df, "fEvTimeTOFMult", "DeltaPiTOF", multaxis, deltaaxis, "TOF ev. mult.", "t-texpPi-t0 (ps)").SetTitle("T-Texp_{#pi}-t_{0}^{TOF}")
    makehisto(df, "fEvTimeTOFMult", "DeltaPiT0AC", multaxis, deltaaxis, "TOF ev. mult.", "t-texpPi-t0 (ps)").SetTitle("T-Texp_{#pi}-t_{0}^{T0AC}")
    makehisto(df, "fEvTimeT0AC", draw=True, xr=evtimeaxis)
    makehisto(df, "fEvTimeTOF", draw=True, xr=evtimeaxis)
    makehisto(df, "fEvTimeT0AC", "fEvTimeTOF", evtimeaxis, evtimeaxis, draw=True, extracut="fEvTimeTOFMult>0").SetTitle("T0AC ev. time vs TOF ev. time")


def main(input_file_name="${HOME}/cernbox/Share/Sofia/LHC22m_523308_apass3_relval_cpu2/16/AnalysisResults_trees_TOFCALIB.root",
         minP=0.6,
         maxP=0.7,
         out_file_name="/tmp/TOFRESO.root"):
    print("Using file:", input_file_name)
    if type(input_file_name) is list and len(input_file_name) == 1 and out_file_name == input_file_name[0]:
        f = TFile(out_file_name, "READ")
        f.ls()
        for i in f.GetListOfKeys():
            print("Getting", i.GetName())
            histograms[i.GetName()] = f.Get(i.GetName())
            histograms[i.GetName()].SetDirectory(0)
        f.Close()
    else:
        pre_process(input_file_name, minP=minP, maxP=maxP)

    def drawhisto(hn, opt="COL"):
        draw_nice_canvas(hn, replace=False)
        histograms[hn].Draw(opt)

    h_slices = {}

    def fitmultslices(hn):
        draw_nice_canvas(hn, replace=False)
        h = histograms[hn]
        obj = TObjArray()
        h.FitSlicesY(0, 0, -1, 0, "QNR", obj)
        obj.At(1).SetTitle(f"{h.GetTitle()} #mu")
        obj.At(2).SetTitle(f"{h.GetTitle()} #sigma")
        obj.At(1).SetLineColor(TColor.GetColor("#e41a1c"))
        obj.At(1).Draw("SAME")
        obj.At(2).Draw("SAME")
        h_slices[hn] = obj
        return obj

    for i in histograms:
        if "fPt" in i:
            continue
        drawhisto(i)
    drawhisto("fPt_vs_fDoubleDelta", opt="COL")
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
    # colors = ['#fbb4ae', '#b3cde3', '#ccebc5', '#decbe4']
    leg = draw_nice_legend([0.74, 0.92], [0.74, 0.92])
    exp_lines = []
    for i in ["El", "Mu", "Ka", "Pr"]:
        col = TColor.GetColor(colors.pop())
        p = histograms["fPt_vs_DeltaPi"+i].ProfileX()
        g = TGraph()
        exp_lines.append(g)
        g.SetTitle(p.GetTitle())
        for j in range(1, p.GetNbinsX()+1):
            if i == "El":
                if p.GetXaxis().GetBinCenter(j) < -1000:
                    continue
                if p.GetXaxis().GetBinCenter(j) > -5:
                    continue
            elif i in ["Ka"]:
                if p.GetXaxis().GetBinCenter(j) < 40:
                    continue
            elif i in ["Pr"]:
                if p.GetXaxis().GetBinCenter(j) < 130:
                    continue
            g.SetPoint(g.GetN(), p.GetBinCenter(j), p.GetBinContent(j))
        g.SetLineColor(col)
        g.SetMarkerColor(col)
        g.SetLineWidth(5)
        g.Draw("lsame")
        leg.AddEntry(g)

    for i in histograms:
        if "fEvTimeTOF_vs_fEvTimeT0AC" in i:
            continue
        if "fPt" in i:
            continue
        if "vs" in i:
            fitmultslices(i)
    fitmultslices("fDoubleDelta_vs_fEvTimeTOFMult")

    # draw_nice_canvas("both")
    # hpdd = hDoulbleDelta.ProjectionY("hDoulbleDelta_proj")
    # hptof = hTOF.ProjectionY("hTOF_proj")
    # hpdd.SetLineColor(TColor.GetColor("#e41a1c"))
    # set_nice_frame(hpdd)
    # hpdd.Draw()
    # hptof.Draw("SAME")
    # leg = draw_nice_legend()
    # leg.AddEntry(hpdd)
    # leg.AddEntry(hptof)

    draw_nice_frame(draw_nice_canvas("resolution"), [0, 40], [0, 200], "TOF ev. mult.", "#sigma (ps)")
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
    leg = draw_nice_legend([0.64, 0.92], [0.57, 0.92])
    for i in h_slices:
        print("Drawing", i)
        col = TColor.GetColor(colors.pop())
        s = h_slices[i].At(2).DrawCopy("SAME")
        s.Scale(1./sqrt(2))
        s.SetLineColor(col)
        s.SetMarkerColor(col)
        s.SetMarkerStyle(20)
        leg.AddEntry(s)
    draw_label(f"{minP:.2f} < #it{{p}}_{{ref}} < {maxP:.2f} GeV/#it{{c}}", 0.2, 0.96, align=11)
    update_all_canvases()

    if not gROOT.IsBatch():
        input("Press enter to exit")
    if input_file_name != out_file_name:
        print("Writing output to", out_file_name)
        fout = TFile(out_file_name, "RECREATE")
        fout.cd()
        for i in histograms:
            print("Writing", i)
            histograms[i].Write()
        fout.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Input file name", nargs="+")
    parser.add_argument("--background", action="store_true", help="Background mode")
    args = parser.parse_args()
    if args.background:
        gROOT.SetBatch(True)
    main(args.filename)
