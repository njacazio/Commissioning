#!/usr/bin/env python3

import numpy as np
import argparse
from ROOT import TFile, TChain, EnableImplicitMT, RDataFrame, gPad, TH1, TColor, TObjArray, gROOT, gStyle, TGraph, TF1, TGraphErrors
from ROOT.RDF import TH3DModel, TH2DModel, TH1DModel
from numpy import sqrt
import time
import sys
import os
import tqdm
sys.path.append(os.path.abspath("../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal


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
    gStyle.SetOptStat(0)
    gStyle.SetOptTitle(0)
    gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")


def addDFToChain(input_file_name, chain):
    f = TFile(input_file_name, "READ")
    lk = f.GetListOfKeys()
    for i in lk:
        dfname = i.GetName()
        if "DF_" not in dfname:
            continue
        tree = f.Get(f"{dfname}/O2deltatof").GetListOfBranches()
        hasit = False
        for i in tree:
            if i.GetName() == "fDeltaTMu":
                hasit = True
                break
        if not hasit:
            return
        tname = "{}?#{}/O2deltatof".format(input_file_name, dfname)
        chain.Add(tname)
    f.Close()

EnableImplicitMT(7)


histogram_names = []
histograms = {}
histomodels = {}


def makehisto(input_dataframe,
              x,
              y=None,
              #   z=None,
              xr=None,
              yr=None,
              xt=None,
              yt=None,
              extracut=None,
              logx=False,
              extracut_to_name=True,
              title=None,
              tag=None):
    n = f"{x}"
    if y is not None:
        n = f"{y}_vs_{x}"
    # if z is not None:
    #     if y is None:
    #         raise ValueError("Cannot have z without y")
    #     n = f"{z}_vs_{y}_vs_{x}"
    if extracut is not None and extracut_to_name:
        n = f"{n}_{extracut}"
    if tag is not None:
        n = f"{n}_{tag}"
    titles = {"fDoubleDelta": "#Delta#Deltat (ps)",
              "fEta": "#it{#eta}",
              "fP": "#it{p} (GeV/#it{c})",
              "fPt": "#it{p}_{T} (GeV/#it{c})",
              "fEvTimeTOFMult": "TOF ev. mult.",
              "fEvTimeTOF": "t_{0}^{TOF}",
              "fEvTimeT0AC": "t_{0}^{T0AC}"}
    if xt is None:
        if x in titles:
            xt = titles[x]
        else:
            xt = x
    if yt is None:
        if y in titles:
            yt = titles[y]
        else:
            yt = y

    add_mode = False
    if n in histograms:
        add_mode = True
    else:
        print("Booking histogram", n, "in", xr, "vs", yr, "with xt =", xt, "and yt =", yt, "logx", logx)

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
            if title is None:
                title = n
            title = f"{title};{xt};{yt}"
            model = TH2DModel(n, title, *xr, *yr)
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
                if title is None:
                    title = n
                if yt is None:
                    yt = "Counts"
                title = f"{title};{xt};{yt}"
                model = TH1DModel(x, title, *xr)
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

    if n not in histogram_names:
        histogram_names.append(n)


def main(input_file_name="${HOME}/cernbox/Share/Sofia/LHC22m_523308_apass3_relval_cpu2/16/AnalysisResults_trees_TOFCALIB.root",
         minPt=0.6,
         maxPt=0.7,
         reference_momentum=[0.6, 0.7],
         replay_mode=False,
         max_files=-1,
         out_file_name="/tmp/TOFRESO.root"):
    print("Using file:", input_file_name)

    out_file_name = out_file_name.replace(".root", f"_{minPt:.2f}_{maxPt:.2f}.root")
    if replay_mode is True:
        f = TFile(out_file_name, "READ")
        f.ls()
        for i in f.GetListOfKeys():
            print("Getting", i.GetName())
            histograms[i.GetName()] = f.Get(i.GetName())
            histograms[i.GetName()].SetDirectory(0)
            histogram_names.append(i.GetName())
        f.Close()
    else:
        print("Running pre-processing")
        start = time.time()
        chain = TChain()
        if type(input_file_name) is list:
            nfiles = 0
            for f in tqdm.tqdm(input_file_name, bar_format='Looping on input files {l_bar}{bar:10}{r_bar}{bar:-10b}'):
                if max_files >= 0 and nfiles >= max_files:
                    print("Reached max number of files", max_files)
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
        ptaxis = [10000, 0, 100]
        deltaaxis = [100, -2000, 2000]

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
        if reference_momentum[0] >= reference_momentum[1]:
            raise ValueError("Reference momentum range is not valid", reference_momentum)

        makehisto(df.Filter(f"fP > {reference_momentum[0]}").Filter(f"fP < {reference_momentum[1]}"),
                  "fEvTimeTOFMult", "fDoubleDelta", multaxis, deltaaxis,
                  tag="reference", title=f"#Delta#Deltat ref. {reference_momentum[0]:.1f} < #it{{p}} < {reference_momentum[1]:.1f} GeV/#it{{c}}")
        makehisto(df, "fEta", xr=[100, -1, 1])
        makehisto(df, "fDoubleDelta", "fP", deltaaxis, ptaxis, title="#Delta#Deltat vs p")
        makehisto(df, "fDoubleDelta", "fPt", deltaaxis, ptaxis, title="#Delta#Deltat vs pT")
        for i in ["El", "Mu", "Ka", "Pr"]:
            part = {"El": "e", "Mu": "#mu", "Ka": "K", "Pr": "p"}[i]
            makehisto(df, "DeltaPi"+i, "fPt", deltaaxis, ptaxis, xt="t_{exp}(#pi) - t_{exp}(%s)" % part, title="t_{exp}(#pi) - t_{exp}(%s)" % part)
            makehisto(df, "DeltaPi"+i, "fP", deltaaxis, ptaxis, xt="t_{exp}(#pi) - t_{exp}(%s)" % part, title="t_{exp}(#pi) - t_{exp}(%s)" % part)
        df = df.Filter(f"fPt>{minPt}")
        df = df.Filter(f"fPt<{maxPt}")

        makehisto(df, "fEvTimeTOFMult", "fEvTimeT0AC", multaxis, evtimeaxis, title="T0AC ev. time")
        makehisto(df, "fEvTimeTOFMult", "fEvTimeTOF", multaxis, evtimeaxis, title="TOF ev. time")
        makehisto(df, "fEvTimeTOFMult", "fDoubleDelta", multaxis, deltaaxis, title="#Delta#Deltat")
        makehisto(df, "fEvTimeTOFMult", "DeltaPiTOF", multaxis, deltaaxis, yt="t-t_{exp}(#pi)-t_{0}^{TOF} (ps)", title="t-t_{exp}(#pi)-t_{0}^{TOF}")
        makehisto(df, "fEvTimeTOFMult", "DeltaPiT0AC", multaxis, deltaaxis, yt="t-t_{exp}(#pi)-t_{0}^{T0AC} (ps)", title="t-t_{exp}(#pi)-t_{0}^{T0AC}")
        makehisto(df, "fEvTimeT0AC", xr=evtimeaxis)
        makehisto(df, "fEvTimeTOF", xr=evtimeaxis)
        makehisto(df, "fEvTimeT0AC", "fEvTimeTOF", evtimeaxis, evtimeaxis, extracut="fEvTimeTOFMult>0", title="T0AC ev. time vs TOF ev. time")
        makehisto(df, "fEvTimeT0AC", "fEvTimeTOF", evtimeaxis, evtimeaxis, extracut="fEvTimeTOFMult>15", title="T0AC ev. time vs TOF ev. time (TOF ev. mult > 15)")
        print("pre-processing done, it took", time.time()-start, "seconds")

    drawn_histos = []

    def drawhisto(hn, opt="COL"):
        draw_nice_canvas(hn, replace=False)
        if hn in drawn_histos:
            return histograms[hn]
        drawn_histos.append(hn)
        histograms[hn].SetBit(TH1.kNoStats)
        histograms[hn].SetBit(TH1.kNoTitle)
        set_nice_frame(histograms[hn])
        histograms[hn].Draw(opt)
        return histograms[hn]

    print("List of histograms:")
    for i in histogram_names:
        print("\t", i)

    for i in histogram_names:
        if i in ["fPt_vs_DeltaPiEl", "fPt_vs_DeltaPiMu", "fPt_vs_DeltaPiKa", "fPt_vs_DeltaPiPr"]:
            continue
        if i in ["fP_vs_DeltaPiEl", "fP_vs_DeltaPiMu", "fP_vs_DeltaPiKa", "fP_vs_DeltaPiPr"]:
            continue
        start = time.time()
        print("+ Drawing histogram", i)
        hd = drawhisto(i)
        if "fEvTimeTOF_vs_fEvTimeT0AC" in i:
            draw_diagonal(hd)
            draw_label(f"Correlation: {hd.GetCorrelationFactor():.2f}", 0.3, 0.85, 0.03)
            if ">" in i:
                draw_label("TOF ev. mult > "+i.split(">")[1], 0.3, 0.8, 0.03)

        print("+ took", time.time()-start, "seconds")

    # Drawing reference histogram
    draw_nice_canvas("reference_histo")
    reference_histo = histograms["fDoubleDelta_vs_fEvTimeTOFMult_reference"].ProjectionY("reference_histo")
    reference_histo.Draw()
    reference_gaus = TF1("reference_gaus", "gaus", -1000, 1000)
    reference_histo.Fit(reference_gaus, "QNRWW")
    reference_gaus.Draw("same")
    draw_label(reference_histo.GetTitle(), 0.35, 0.89, 0.03)
    draw_label(f"Gaussian fit:", 0.3, 0.84)
    draw_label(f"#mu = {reference_gaus.GetParameter(1):.3f} (ps)", 0.3, 0.79)
    draw_label(f"#sigma = {reference_gaus.GetParameter(2):.3f} (ps)", 0.3, 0.74)

    reso_vs_p = TGraphErrors()
    reso_vs_p.GetXaxis().SetTitle("#it{p} (GeV/#it{c})")
    reso_vs_pt = TGraphErrors()
    reso_vs_pt.GetXaxis().SetTitle("#it{p}_{T} (GeV/#it{c})")
    reso_graphs = {"fP": reso_vs_p, "fPt": reso_vs_pt}
    stopP = 20.3
    startP = 10.3
    stopP = 1.3
    startP = 0.3
    pwidth = 0.1
    for j in ["fP", "fPt"]:
        r = reso_graphs[j]
        r.GetYaxis().SetTitle("#sigma "+histograms[j+"_vs_fDoubleDelta"].GetXaxis().GetTitle())
        for i in range(int((stopP-startP)/pwidth)):
            xmin = startP + i*pwidth
            xmax = xmin + pwidth
            reso_histo = histograms[j+"_vs_fDoubleDelta"]
            reso_histo = reso_histo.ProjectionX(f"reso_histo_{j}_{xmin}_{xmax}", reso_histo.GetYaxis().FindBin(xmin+0.00001), reso_histo.GetYaxis().FindBin(xmax-0.0001))
            reso_gaus = TF1("reso_gaus_"+j, "gaus", -1000, 1000)
            reso_histo.Fit(reso_gaus, "QNRWW")
            r.SetPoint(r.GetN(), (xmin+xmax)/2, sqrt(reso_gaus.GetParameter(2)**2 - reference_gaus.GetParameter(2)**2/2))
            r.SetPointError(r.GetN()-1, (xmax-xmin)/2, reso_gaus.GetParError(2))
            if 0:
                draw_nice_canvas(f"reso_histo_vs_{j}_{i}")
                reso_histo.Draw()
                draw_label(f"#mu = {reso_gaus.GetParameter(1):.3f}", 0.3, 0.8)
                draw_label(f"#sigma = {reso_gaus.GetParameter(2):.3f}", 0.3, 0.75)

        draw_nice_canvas("reso_histo_vs_"+j)
        r.Draw("AP")

    if 1:
        # Drawing Double delta vs Pt and P
        for k in ["fPt", "fP"]:
            hd = drawhisto(k+"_vs_fDoubleDelta", opt="COL")
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
            leg = draw_nice_legend([0.74, 0.92], [0.74, 0.92])
            for i in ["El", "Mu", "Ka", "Pr"]:
                col = TColor.GetColor(colors.pop())
                particle_profile = histograms[k+"_vs_DeltaPi"+i].ProfileX()
                particle_profile.SetName("profile_"+particle_profile.GetName())
                if 1:
                    g = TGraph()
                    g.SetName("g"+particle_profile.GetName())
                    hd.GetListOfFunctions().Add(g)
                    g.SetTitle(particle_profile.GetTitle())
                    for j in range(1, particle_profile.GetNbinsX()+1):
                        if i == "El":
                            if particle_profile.GetXaxis().GetBinCenter(j) < -1000:
                                continue
                            if particle_profile.GetXaxis().GetBinCenter(j) > -5:
                                continue
                        elif i == "Mu":
                            if particle_profile.GetXaxis().GetBinCenter(j) < -500:
                                continue
                            if particle_profile.GetXaxis().GetBinCenter(j) > -5:
                                continue
                        elif i in ["Ka"]:
                            if particle_profile.GetXaxis().GetBinCenter(j) < 40:
                                continue
                        elif i in ["Pr"]:
                            if particle_profile.GetXaxis().GetBinCenter(j) < 130:
                                continue
                        g.SetPoint(g.GetN(), particle_profile.GetBinCenter(j), particle_profile.GetBinContent(j))
                    g.SetLineColor(col)
                    g.SetMarkerColor(col)
                    g.SetLineWidth(2)
                    g.Draw("lsame")
                    del particle_profile
                else:
                    particle_profile.SetLineColor(col)
                    particle_profile.SetMarkerColor(col)
                    particle_profile.SetLineWidth(2)
                    particle_profile.Draw("lsame")
                leg.AddEntry(g)

    # Fitting slices in multiplicity
    h_slices = {}

    def fitmultslices(hn):
        draw_nice_canvas(hn, replace=False)
        h = histograms[hn]
        obj = TObjArray()
        leg = draw_nice_legend([0.82, 0.92], [0.78, 0.92])
        h.FitSlicesY(0, 0, -1, 0, "QNRWW", obj)
        obj.At(1).SetTitle(f"#mu {h.GetTitle()}")
        obj.At(2).SetTitle(f"#sigma {h.GetTitle()}")
        leg.AddEntry(obj.At(1), "#mu", "l")
        leg.AddEntry(obj.At(2), "#sigma", "l")
        obj.At(1).SetLineColor(TColor.GetColor("#e41a1c"))
        obj.At(1).Draw("SAME")
        obj.At(2).Draw("SAME")
        g = TGraph()
        g.SetPoint(0, h.GetXaxis().GetBinLowEdge(1), 0)
        g.SetPoint(1, h.GetXaxis().GetBinUpEdge(h.GetXaxis().GetNbins()), 0)
        g.SetLineStyle(7)
        g.Draw("sameL")
        h.GetListOfFunctions().Add(g)
        h_slices[hn] = obj
        return obj

    for i in histograms:
        if "fEvTimeTOF_vs_fEvTimeT0AC" in i:
            continue
        if "fPt_" in i or "fP_" in i:
            continue
        if "vs" in i:
            fitmultslices(i)
    fitmultslices("fDoubleDelta_vs_fEvTimeTOFMult")

    if 1:
        draw_nice_canvas("DeltaEvTime")
        colors = ['#e41a1c', '#377eb8']
        b = histograms["DeltaPiTOF_vs_fEvTimeTOFMult"].GetXaxis().FindBin(12)
        p = histograms["DeltaPiTOF_vs_fEvTimeTOFMult"].ProjectionY("DeltaPiTOF_vs_fEvTimeTOFMult_proj", b).DrawCopy()
        p.SetBit(TH1.kNoStats)
        p.SetBit(TH1.kNoTitle)
        p.SetLineColor(TColor.GetColor(colors.pop()))
        leg = draw_nice_legend([0.64, 0.92], [0.57, 0.92])
        leg.AddEntry(p, f"{p.GetTitle()} {p.Integral()} #mu = {p.GetMean():.2f}")
        p = histograms["DeltaPiT0AC_vs_fEvTimeTOFMult"].ProjectionY("DeltaPiT0AC_vs_fEvTimeTOFMult_proj", b).DrawCopy("same")
        p.SetLineColor(TColor.GetColor(colors.pop()))
        leg.AddEntry(p, f"{p.GetTitle()} {p.Integral()} #mu = {p.GetMean():.2f}")

    multiplicity_range = [0, 45]
    max_multiplicity = 25
    if 1:
        # Drawing the event time resolution
        colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
        draw_nice_frame(draw_nice_canvas("resolutionEvTime"), multiplicity_range, [0, 200], "TOF ev. mult.", "#sigma (ps)")
        leg = draw_nice_legend([0.64, 0.92], [0.57, 0.92])
        for i in h_slices:
            print("Drawing slice for event time resolution", i)
            if "fEvTimeTOF_" not in i and "fEvTimeT0AC_" not in i:
                continue
            col = TColor.GetColor(colors.pop())
            s = h_slices[i].At(2).DrawCopy("SAME")
            for j in range(1, s.GetNbinsX()+1):
                if s.GetXaxis().GetBinCenter(j) > max_multiplicity:
                    s.SetBinContent(j, 0)
                    s.SetBinError(j, 0)
            s.SetLineColor(col)
            s.SetMarkerColor(col)
            s.SetMarkerStyle(20)
            leg.AddEntry(s)
    if 1:
        colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
        draw_nice_frame(draw_nice_canvas("resolutionDelta"), multiplicity_range, [0, 150], "TOF ev. mult.", "#sigma (ps)")
        # colors = ["#a65628", '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
        # leg = draw_nice_legend([0.64, 0.92], [0.57, 0.92])
        leg = draw_nice_legend([0.2, 0.48], [0.2, 0.45])
        drawn_slices = {}
        for i in h_slices:
            print("Drawing slice", i)
            if "fEvTimeTOF_" in i:
                continue
            if "fEvTimeT0AC_" in i:
                continue
            col = TColor.GetColor(colors.pop())
            s = h_slices[i].At(2).DrawCopy("SAME")
            for j in range(1, s.GetNbinsX()+1):
                if s.GetXaxis().GetBinCenter(j) > max_multiplicity:
                    s.SetBinContent(j, 0)
                    s.SetBinError(j, 0)
            drawn_slices[i] = s
            if "DoubleDelta" in i and "reference" not in i:
                for j in range(1, s.GetNbinsX()+1):
                    diff = s.GetBinContent(j)**2 - h_slices["fDoubleDelta_vs_fEvTimeTOFMult_reference"].At(2).GetBinContent(j)**2/2
                    if diff >= 0:
                        s.SetBinContent(j, sqrt(diff))
            s.SetLineColor(col)
            s.SetMarkerColor(col)
            s.SetMarkerStyle(20)
            leg.AddEntry(s)

        drawn_slices["fDoubleDelta_vs_fEvTimeTOFMult_reference"].Scale(1./sqrt(2))
        draw_label(f"{minPt:.2f} < #it{{p}}_{{T}} < {maxPt:.2f} GeV/#it{{c}}", 0.2, 0.97, align=11)

        if 1:
            # fasympt = TF1("fasympt", "[0]/x^[2]+[1]", 0, 40)
            fasympt = TF1("fasympt", "sqrt([0]*[0]/x + [1]*[1])", 0, 40)
            mult_value = 30
            for i in drawn_slices:
                hd = drawn_slices[i]
                fasympt.SetParameter(0, -5.81397e+01)
                hd.Fit(fasympt, "QNWW", "", 3, 20)
                fasympt.SetLineStyle(7)
                fasympt.SetLineColor(drawn_slices[i].GetLineColor())
                fasympt.DrawClone("same")
                draw_label(f"{hd.GetTitle()}|_{{{mult_value}}} = {fasympt.Eval(mult_value):.1f} ps", mult_value, fasympt.Eval(mult_value)+5, align=11, ndc=False, size=0.02)

    update_all_canvases()

    if not gROOT.IsBatch():
        input("Press enter to exit")
    if not replay_mode:
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
    parser.add_argument("--background", "-b", action="store_true", help="Background mode")
    parser.add_argument("--minpt", default=0.3, type=float, help="Minimum transverse momentum")
    parser.add_argument("--maxpt", default=0.4, type=float, help="Maximum transverse momentum")
    parser.add_argument("--maxfiles", default=-1, type=int, help="Maximum number of files")
    parser.add_argument("--replay_mode", "--replay", action="store_true", help="Replay previous output")
    args = parser.parse_args()
    if args.background:
        gROOT.SetBatch(True)
    main(args.filename, minPt=args.minpt, maxPt=args.maxpt, replay_mode=args.replay_mode, max_files=args.maxfiles)
