#!/usr/bin/env python3

import numpy as np
import argparse
from ROOT import TFile, TChain, EnableImplicitMT, RDataFrame, gPad, TH1, TColor, TObjArray
from ROOT.RDF import TH2DModel, TH1DModel, RSnapshotOptions
from numpy import sqrt
import sys
import os
sys.path.append(os.path.abspath("../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label


def addDFToChain(fileName, chain):
    f = TFile(fileName, "READ")
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
        tname = "{}?#{}/O2deltatof".format(fileName, dfname)
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


def main(fileName="${HOME}/cernbox/Share/Sofia/LHC22m_523308_apass3_relval_cpu2/16/AnalysisResults_trees_TOFCALIB.root",
         minP=0.6,
         maxP=0.7,
         maxfiles=20000):
    print("Using file:", fileName)
    chain = TChain()
    if type(fileName) is list:
        nfiles = 0
        for f in fileName:
            if nfiles > maxfiles:
                break
            nfiles += 1
            addDFToChain(f, chain)
        print("Using a total of", nfiles, "files")
    elif (fileName.endswith(".root")):
        addDFToChain(fileName, chain)
    elif (fileName.endswith(".txt")):
        with open("fileName", "r") as f:
            for line in f:
                addDFToChain(line, chain)
    df = RDataFrame(chain)
    df = df.Filter(f"fP>{minP}")
    df = df.Filter(f"fP<{maxP}")
    # df = df.Filter("fEta>0.3")
    # df = df.Filter("fEta<0.4")
    # df = df.Filter("fPhi>0.3")
    # df = df.Filter("fPhi<0.4")
    df = df.Filter("fTOFChi2<5")
    df = df.Filter("fTOFChi2>=0")
    df = df.Define("TOF", "fDeltaTPi-fEvTimeTOF")
    df = df.Define("T0AC", "fDeltaTPi-fEvTimeT0AC")
    evtimeaxis = [1000, -2000, 2000]
    multaxis = [40, 0, 40]

    def fitmultslices(h):
        obj = TObjArray()
        h.FitSlicesY(0, 0, -1, 0, "QNR", obj)
        obj.At(1).SetTitle(f"{h.GetTitle()} #mu")
        obj.At(2).SetTitle(f"{h.GetTitle()} #sigma")
        obj.At(1).SetLineColor(TColor.GetColor("#e41a1c"))
        obj.At(1).Draw("SAME")
        obj.At(2).Draw("SAME")
        return obj

    makehisto(df, "fEvTimeT0AC", draw=True, xr=evtimeaxis)
    hevtimevsmultT0AC = makehisto(df, "fEvTimeTOFMult", "fEvTimeT0AC", multaxis, evtimeaxis, draw=True)
    hevtimevsmultT0AC.SetTitle("T0AC ev. time")
    hslicesEvTimeT0AC = fitmultslices(hevtimevsmultT0AC)

    makehisto(df, "fEvTimeTOF", draw=True, xr=evtimeaxis)
    hevtimevsmult = makehisto(df, "fEvTimeTOFMult", "fEvTimeTOF", multaxis, evtimeaxis, draw=True)
    hevtimevsmult.SetTitle("TOF ev. time")
    hslicesEvTime = fitmultslices(hevtimevsmult)

    makehisto(df, "fEvTimeT0AC", "fEvTimeTOF", evtimeaxis, evtimeaxis, draw=True)

    deltaaxis = [1000, -2000, 2000]
    hDoulbleDelta = makehisto(df, "fEvTimeTOFMult", "fDoubleDelta", multaxis, deltaaxis, "TOF ev. mult.", "#Delta#Delta (ps)")
    hDoulbleDelta.SetTitle("#Delta#Delta")
    draw_nice_canvas("doubledelta")
    hDoulbleDelta.Draw("COLZ")
    hslicesDD = fitmultslices(hDoulbleDelta)
    hslicesDD.At(2).Scale(1./sqrt(2))

    hTOF = makehisto(df, "fEvTimeTOFMult", "TOF", multaxis, deltaaxis, "TOF ev. mult.", "t-texpPi-t0 (ps)")
    hTOF.SetTitle("T-Texp_{#pi}-t_{0}^{TOF}")
    draw_nice_canvas("tmentexp")
    hTOF.Draw("COLZ")
    hslicesTOF = fitmultslices(hTOF)

    hT0AC = makehisto(df, "fEvTimeTOFMult", "T0AC", multaxis, deltaaxis, "TOF ev. mult.", "t-texpPi-t0 (ps)")
    hT0AC.SetTitle("T-Texp_{#pi}-t_{0}^{T0AC}")
    draw_nice_canvas("tmentexp")
    hT0AC.Draw("COLZ")
    hslicesT0AC = fitmultslices(hT0AC)

    draw_nice_canvas("both")
    hpdd = hDoulbleDelta.ProjectionY("hDoulbleDelta_proj")
    hptof = hTOF.ProjectionY("hTOF_proj")
    hpdd.SetLineColor(TColor.GetColor("#e41a1c"))
    set_nice_frame(hpdd)
    hpdd.Draw()
    hptof.Draw("SAME")
    leg = draw_nice_legend()
    leg.AddEntry(hpdd)
    leg.AddEntry(hptof)

    draw_nice_frame(draw_nice_canvas("resolution"), [0, 40], [0, 200], "TOF ev. mult.", "#sigma (ps)")
    hslices = [hslicesEvTime.At(2).DrawCopy("SAME"),
               hslicesDD.At(2).DrawCopy("SAME"),
               hslicesTOF.At(2).DrawCopy("SAME"),
               hslicesT0AC.At(2).DrawCopy("SAME")]
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
    for i in enumerate(hslices):
        i[1].SetLineColor(TColor.GetColor(colors[i[0]]))
        i[1].SetMarkerColor(TColor.GetColor(colors[i[0]]))
        i[1].SetMarkerStyle(20)
    leg = draw_nice_legend([0.64, 0.92], [0.57, 0.92])
    for i in hslices:
        leg.AddEntry(i)
    draw_label(f"{minP:.2f} < #it{{p}} < {maxP:.2f} GeV/#it{{c}}", 0.2, 0.925, align=11)
    update_all_canvases()
    input("Press enter to exit")
    fout = TFile("/tmp/TOFRESO.root", "RECREATE")
    fout.cd()
    for i in [hevtimevsmult, hevtimevsmultT0AC, hDoulbleDelta, hTOF, hT0AC]:
        i.Write()





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Input file name", nargs="+")
    args = parser.parse_args()
    main(args.filename)
