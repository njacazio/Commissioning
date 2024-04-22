#!/usr/bin/env python3

from plotMakers import plotDeltaTVsEta
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
from plotMakers import plot2DPIDPlots

if 1:
    from ROOT import gInterpreter
    gInterpreter.Declare("""
Double_t myfunction(Double_t* x, Double_t* par)
{
  Float_t xx = x[0];
  float norm = par[0];
  float mean = par[1];
  float sigma = par[2];
  float tail = par[3];
  if (xx <= (tail + mean))
    return norm * TMath::Gaus(xx, mean, sigma);
  else
    return norm * TMath::Gaus(tail + mean, mean, sigma) * TMath::Exp(-tail * (xx - tail - mean) / (sigma * sigma));
}

TF1* GaussianTail(TString name = "tailgaus", float min=-10, float max=10)
{
  TF1* f = new TF1(name, myfunction, min, max, 4);
  f->SetParameter(0, 1);
  f->SetParName(0, "Norm");
  
  f->SetParameter(1, 0);
  f->SetParName(1, "Mean");

  f->SetParameter(2, 100);
  f->SetParLimits(2, 0, 200);
  f->SetParName(2, "Sigma");

  f->SetParameter(3, 100);
  f->SetParLimits(3, 0, 200);
  f->SetParName(3, "Tail");
  return f;
}
""")
    from ROOT import GaussianTail


sys.path.append(os.path.abspath("../QC/analysis/AO2D/"))
sys.path.append(os.path.abspath("../QC/analysis/utilities/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal, definenicepalette
    from common import warning_msg, wait_for_input

# Post processing

definenicepalette()


def addDFToChain(input_file_name, chain):
    f = TFile(input_file_name, "READ")
    lk = f.GetListOfKeys()
    for i in lk:
        dfname = i.GetName()
        if "DF_" not in dfname:
            continue
        treename = f"{dfname}/O2deltatof"
        tree = f.Get(treename)
        if not tree:
            print("Waring: no tree found for", treename, "in", input_file_name)
            f.Get(dfname).ls()
            continue
        tree = tree.GetListOfBranches()
        # tree.ls()

        def testbranch(b):
            hasit = False
            for i in tree:
                if i.GetName() == b:
                    hasit = True
                    break
            if not hasit:
                return False
            return True

        if not testbranch("fDeltaTMu"):
            return
        if not testbranch("fPtSigned"):
            return

        tname = "{}?#{}/O2deltatof".format(input_file_name, dfname)
        chain.Add(tname)
    f.Close()


histogram_names = []
histograms = {}
histomodels = {}


def get_histogram(hn=None):
    if hn is None:
        return histograms
    return histograms[hn]


def makehisto(input_dataframe,
              x,
              y=None,
              z=None,
              xr=None,
              yr=None,
              zr=None,
              xt=None,
              yt=None,
              zt=None,
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
              "fEvTimeTOF": "t_{ev}^{TOF}",
              "DeltaPiTOF": "t-t_{exp}(#pi)-t_{ev}^{TOF} (ps)",
              "DeltaKaTOF": "t-t_{exp}(K)-t_{ev}^{TOF} (ps)",
              "DeltaPrTOF": "t-t_{exp}(p)-t_{ev}^{TOF} (ps)",
              "DeltaPiT0AC": "t-t_{exp}(#pi)-t_{ev}^{FT0} (ps)",
              "DeltaKaT0AC": "t-t_{exp}(K)-t_{ev}^{FT0} (ps)",
              "DeltaPrT0AC": "t-t_{exp}(p)-t_{ev}^{FT0} (ps)",
              "FT0AC_minus_TOF": "t_{ev}^{FT0} - t_{ev}^{TOF}",
              "FT0AC_minus_FT0A": "t_{ev}^{FT0AC} - t_{ev}^{FT0A}",
              "FT0AC_minus_FT0C": "t_{ev}^{FT0AC} - t_{ev}^{FT0C}",
              "FT0A_minus_FT0C": "t_{ev}^{FT0A} - t_{ev}^{FT0C}",
              "FT0A_minus_TOF": "t_{ev}^{FT0A} - t_{ev}^{TOF}",
              "FT0C_minus_TOF": "t_{ev}^{FT0C} - t_{ev}^{TOF}",
              "fPhi": "#phi",
              "fEvTimeT0AC": "t_{ev}^{FT0}"}
    if xt is None:
        if x in titles:
            xt = titles[x]
        else:
            xt = x
            warning_msg("Not defined title for X", x)
    if y is None:
        yt = "Counts"
    elif yt is None:
        if y in titles:
            yt = titles[y]
        else:
            yt = y
            warning_msg("Not defined title for Y", y)
    if z is not None and zt is None:
        zt = titles[z]

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
            if themin <= 0.0:
                themin = 0.01
            themax = xr[2]
            logmin = np.log10(themin)
            logmax = np.log10(themax)
            nbins = xr[0]
            logdelta = (logmax - logmin) / (float(nbins))
            binEdges = []
            for i in range(nbins):
                nextEdge = 10 ** (logmin + i * logdelta)
                binEdges.append(nextEdge)
            binEdges = np.array(binEdges)
            xr = [xr[0] - 1, binEdges]
    if z is not None:
        if add_mode:
            model = histomodels[n]
        else:
            if title is None:
                title = n
            title = f"{title};{xt};{yt};{zt}"
            model = TH3DModel(n, title, *xr, *yr, *zr)
        h = df.Histo3D(model, x, y, z)
        if add_mode:
            histograms[n].Add(h.GetPtr())
            return
        else:
            histomodels[n] = model
            histograms[n] = h
    elif y is not None:
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
    else:
        raise ValueError("Histogram", n, "already exists")


def define_extra_columns(df):
    df = df.Define("fPt", "TMath::Abs(fPtSigned)")
    df = df.Define("FT0AC_minus_TOF", "fEvTimeT0AC - fEvTimeTOF")
    df = df.Define("FT0AC_minus_FT0A", "fEvTimeT0AC - fT0ACorrected")
    df = df.Define("FT0AC_minus_FT0C", "fEvTimeT0AC - fT0CCorrected")
    df = df.Define("FT0A_minus_FT0C", "fT0ACorrected - fT0CCorrected")
    df = df.Define("FT0A_minus_TOF", "fT0ACorrected - fEvTimeTOF")
    df = df.Define("FT0C_minus_TOF", "fT0CCorrected - fEvTimeTOF")
    for i in ["Pi", "Ka", "Pr"]:
        df = df.Define(f"Delta{i}TOF", f"fDeltaT{i}-fEvTimeTOF")
        df = df.Define(f"Delta{i}T0AC", f"fDeltaT{i}-fEvTimeT0AC")
    for i in ["El", "Mu", "Ka", "Pr"]:
        df = df.Define(f"DeltaPi{i}", f"fDeltaTPi-fDeltaT{i}")
    return df


def main(input_file_name="${HOME}/cernbox/Share/Sofia/LHC22m_523308_apass3_relval_cpu2/16/AnalysisResults_trees_TOFCALIB.root",
         minPt=0.6,
         maxPt=0.7,
         reference_momentum=[0.6, 0.7],
         replay_mode=False,
         max_files=-1,
         label=None,
         out_file_name="/tmp/TOFRESO.root",
         do_draw_correlation_evtime_ft0_tof=False,
         do_draw_comparison_pos_neg=False,
         do_draw_resolution_with_FT0=True,
         do_draw_resolution_vs_mult=False):
    print("Using file:", input_file_name)
    if label.strip() == "":
        label = None

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
        # Apply filters
        # df = df.Filter("fEta>0.3")
        # df = df.Filter("fEta<0.4")
        # df = df.Filter("fPhi>0.3")
        # df = df.Filter("fPhi<0.4")
        df = df.Filter("fTOFChi2<5")
        df = df.Filter("fTOFChi2>=0")
        # df = df.Filter("fPtSigned>=0")  # only positive tracks
        # df = df.Filter("fRefSign>=0")  # only positive tracks

        df = define_extra_columns(df)
        if reference_momentum[0] >= reference_momentum[1]:
            raise ValueError("Reference momentum range is not valid", reference_momentum)

        # Reference double delta
        makehisto(df.Filter(f"fP > {reference_momentum[0]}").Filter(f"fP < {reference_momentum[1]}"),
                  x="fEvTimeTOFMult", y="fDoubleDelta", xr=multaxis, yr=deltaaxis,
                  tag="reference", title=f"#Delta#Deltat ref. {reference_momentum[0]:.1f} < #it{{p}} < {reference_momentum[1]:.1f} GeV/#it{{c}}")
        # Double delta
        makehisto(df, x="fP", y="fDoubleDelta", xr=ptaxis, yr=deltaaxis, title="#Delta#Deltat vs p")
        makehisto(df, x="fPt", y="fDoubleDelta", xr=ptaxis, yr=deltaaxis, title="#Delta#Deltat vs pT")
        # T - texp - TEv
        for i in ["Pi", "Ka", "Pr"]:
            makehisto(df, x="fPt", y=f"Delta{i}TOF", xr=ptaxis, yr=deltaaxis, title=f"Delta{i}TOF vs pT")
            makehisto(df, x="fPt", y=f"Delta{i}T0AC", xr=ptaxis, yr=deltaaxis, title=f"Delta{i}T0AC vs pT")
            eta_pt_range = [1.3, 1.35]
            makehisto(df.Filter(f"fPt>{eta_pt_range[0]}").Filter(f"fPt<{eta_pt_range[1]}"), x="fEta", y=f"Delta{i}T0AC", xr=etaaxis, yr=deltaaxis,
                      title=f"Delta{i}T0AC vs Eta for {eta_pt_range[0]:.2f} < pT < {eta_pt_range[1]:.2f}")
        makehisto(df.Filter("fPtSigned>=0"), x="fPt", y="DeltaPrTOF", xr=ptaxis, yr=deltaaxis, title="DeltaPrTOF vs pT", tag="Pos")
        makehisto(df.Filter("fPtSigned<=0"), x="fPt", y="DeltaPrTOF", xr=ptaxis, yr=deltaaxis, title="DeltaPrTOF vs pT", tag="Neg")
        for i in ["El", "Mu", "Ka", "Pr"]:
            part = {"El": "e", "Mu": "#mu", "Ka": "K", "Pr": "p"}[i]
            makehisto(df, x="fP", y="DeltaPi" + i, xr=ptaxis, yr=tminustexpaxis, yt="t_{exp}(#pi) - t_{exp}(%s)" % part, title="t_{exp}(#pi) - t_{exp}(%s)" % part)
            makehisto(df, x="fPt", y="DeltaPi" + i, xr=ptaxis, yr=tminustexpaxis, yt="t_{exp}(#pi) - t_{exp}(%s)" % part, title="t_{exp}(#pi) - t_{exp}(%s)" % part)
        if 0:
            df = df.Filter(f"fPt>{minPt}")
            df = df.Filter(f"fPt<{maxPt}")
        else:
            df = df.Filter(f"fP>{minPt}")
            df = df.Filter(f"fP<{maxPt}")
        makehisto(df, x="fEta", xr=etaaxis)

        # Event times
        if do_draw_resolution_vs_mult:
            makehisto(df, x="fEvTimeTOFMult", y="fEvTimeT0AC", xr=multaxis, yr=evtimeaxis, title="T0AC ev. time")
            makehisto(df, x="fEvTimeTOFMult", y="fEvTimeTOF", xr=multaxis, yr=evtimeaxis, title="TOF ev. time")
            makehisto(df, x="fEvTimeTOFMult", y="fDoubleDelta", xr=multaxis, yr=deltaaxis, title="#Delta#Deltat")
            makehisto(df, x="fEvTimeTOFMult", y="DeltaPiTOF", xr=multaxis, yr=deltaaxis, title="t-t_{exp}(#pi)-t_{ev}^{TOF}")
            makehisto(df, x="fEvTimeTOFMult", y="DeltaPiT0AC", xr=multaxis, yr=deltaaxis, title="t-t_{exp}(#pi)-t_{ev}^{FT0}")
        makehisto(df, x="fEvTimeT0AC", xr=evtimeaxis)
        makehisto(df, x="fEvTimeTOF", xr=evtimeaxis)
        makehisto(df, x="fEvTimeT0AC", y="fEvTimeTOF", xr=evtimeaxis, yr=evtimeaxis, extracut="fEvTimeTOFMult>0", title="T0AC ev. time vs TOF ev. time")
        makehisto(df, x="fEvTimeT0AC", y="fEvTimeTOF", xr=evtimeaxis, yr=evtimeaxis, extracut="fEvTimeTOFMult>5", title="T0AC ev. time vs TOF ev. time (TOF ev. mult > 5)")
        makehisto(df, x="fEvTimeT0AC", y="fEvTimeTOF", xr=evtimeaxis, yr=evtimeaxis, extracut="fEvTimeTOFMult>15", title="T0AC ev. time vs TOF ev. time (TOF ev. mult > 15)")
        makehisto(df, x="fEvTimeTOFMult", y="FT0AC_minus_TOF", xr=multaxis, yr=evtimediffaxis, title="T0AC ev. time - TOF ev. time vs TOF mult.")
        makehisto(df, x="fEvTimeTOFMult", y="FT0A_minus_FT0C", xr=multaxis, yr=evtimediffaxis, title="T0A ev. time - T0C ev. time vs TOF mult.")
        makehisto(df, x="FT0AC_minus_FT0A", xr=evtimediffaxis)
        makehisto(df, x="FT0AC_minus_FT0C", xr=evtimediffaxis)
        makehisto(df, x="FT0AC_minus_TOF", xr=evtimediffaxis)
        makehisto(df, x="FT0A_minus_FT0C", xr=evtimediffaxis)
        # makehisto(df, x="FT0A_minus_FT0C")
        makehisto(df, x="FT0A_minus_TOF", xr=evtimediffaxis)
        makehisto(df, x="FT0C_minus_TOF", xr=evtimediffaxis)
        if 0:
            for i in range(0, etaaxis[0]):
                bwidth = (etaaxis[2] - etaaxis[1]) / etaaxis[0]
                etarange = [etaaxis[1] + bwidth * i, etaaxis[1] + bwidth * (i + 1)]
                makehisto(df.Filter(f"fEta>{etarange[0]}").Filter(f"fEta<{etarange[1]}"), x="fPhi", y="DeltaPiT0AC", xr=phiaxis, yr=deltaaxis, tag=f"EtaRange={etarange}")
        else:
            makehisto(df, x="fPhi", y="DeltaPiT0AC", z="fEta", xr=phiaxis, yr=deltaaxis, zr=etaaxis)

        print("pre-processing done, it took", time.time() - start, "seconds")

    drawn_graphs = []

    def graph(name, title=None):
        g = TGraph()
        drawn_graphs.append(g)
        g.SetName(name)
        if title is not None:
            g.SetTitle(title)
        return g

    def draw_plot_label():
        if label is not None and label != "":
            draw_label(label, 0.95, 0.96, 0.03, align=31)

    drawn_histos = []

    def drawhisto(hn, opt="COL", xrange=None, yrange=None, transpose=False):
        print("+ Drawing histogram", f"`{hn}`", "at line", inspect.stack()[1][2])
        start = time.time()
        draw_nice_canvas(hn, replace=False)
        if hn not in histograms:
            warning_msg("Histogram", hn, "not found")
            for i in histograms:
                print("\t", i)
            return
        if hn in drawn_histos:
            return histograms[hn]
        drawn_histos.append(hn)
        histograms[hn].SetBit(TH1.kNoStats)
        histograms[hn].SetBit(TH1.kNoTitle)
        set_nice_frame(histograms[hn])
        if transpose:
            if "TH2" not in histograms[hn].ClassName():
                raise ValueError("Cannot transpose something that is not a TH2")
            xaxis = histograms[hn].GetXaxis()
            yaxis = histograms[hn].GetYaxis()
            htmp = TH2F(f"transpose{histograms[hn].GetName()}",
                        histograms[hn].GetTitle(),
                        yaxis.GetNbins(), yaxis.GetBinLowEdge(1), yaxis.GetBinUpEdge(yaxis.GetNbins()),
                        xaxis.GetNbins(), xaxis.GetBinLowEdge(1), xaxis.GetBinUpEdge(xaxis.GetNbins()))
            htmp.GetXaxis().SetTitle(yaxis.GetTitle())
            htmp.GetYaxis().SetTitle(xaxis.GetTitle())
            for ix in range(1, xaxis.GetNbins() + 1):
                # xb = htmp.GetYaxis().FindBin(xaxis.GetBinCenter(ix))
                for iy in range(1, yaxis.GetNbins() + 1):
                    # yb = htmp.GetXaxis().FindBin(yaxis.GetBinCenter(iy))
                    # print(ix, iy, "goes to", xb, yb)
                    htmp.SetBinContent(iy, ix, histograms[hn].GetBinContent(ix, iy))
                    # htmp.SetBinContent(xb, yb,
                    #                    histograms[hn].GetBinContent(ix, iy) + htmp.GetBinContent(xb, yb))
            histograms[hn] = htmp.DrawCopy(opt)
            histograms[hn].SetDirectory(0)
        else:
            histograms[hn].Draw(opt)
        if xrange is not None:
            if transpose:
                histograms[hn].GetYaxis().SetRangeUser(*xrange)
            else:
                histograms[hn].GetXaxis().SetRangeUser(*xrange)
        if yrange is not None:
            if transpose:
                histograms[hn].GetXaxis().SetRangeUser(*yrange)
            else:
                histograms[hn].GetYaxis().SetRangeUser(*yrange)

        draw_plot_label()
        print("+ took", time.time() - start, "seconds")
        return histograms[hn]

    print("List of histograms:")
    for i in histogram_names:
        print("\t", i)

    # Drawing all the histograms
    if 0:
        for i in histogram_names:
            if 1:
                if i in ["DeltaPiEl_vs_fPt",
                         "DeltaPiMu_vs_fPt",
                         "DeltaPiKa_vs_fPt",
                         "DeltaPiPr_vs_fPt"]:
                    continue
            if 1:
                if i in ["DeltaPiEl_vs_fP",
                         "DeltaPiMu_vs_fP",
                         "DeltaPiKa_vs_fP",
                         "DeltaPiPr_vs_fP"]:
                    continue
            if 1:
                if i in ["fDoubleDelta_vs_fP", "fDoubleDelta_vs_fPt"]:
                    continue
            if 1:
                if "DeltaPiT0AC_vs_fPhi_EtaRange=" in i:
                    continue
            if 1:
                if i in ["DeltaKaT0AC_vs_fPt",
                         "DeltaPrT0AC_vs_fPt",
                         "DeltaKaTOF_vs_fPt",
                         "DeltaPrTOF_vs_fPt"]:
                    continue
            if "fEvTimeTOF_vs_fEvTimeT0AC" in i:
                continue
            hd = drawhisto(i)

    # Drawing the difference between FT0C and FT0A and TOF
    value_ft0AC_resolution = None
    if 0:
        for i in ["FT0AC_minus_FT0A",
                  "FT0AC_minus_FT0C",
                  "FT0AC_minus_TOF",
                  "FT0A_minus_FT0C",
                  "FT0A_minus_TOF",
                  "FT0C_minus_TOF"]:
            draw_nice_canvas(i)
            hd = drawhisto(i)
            fun = TF1("fun", "gaus", -1000, 1000)
            hd.Fit(fun, "QNRWW")
            fun.Draw("SAME")
            draw_label(f"#mu = {fun.GetParameter(1):.2f} (ps)", 0.35, 0.85, 0.03)
            draw_label(f"#sigma = {fun.GetParameter(2):.2f} (ps)", 0.35, 0.8, 0.03)
            if i == "FT0A_minus_FT0C":
                value_ft0AC_resolution = fun.GetParameter(2)

    # Draw correlation between TOF and FT0 event times
    if do_draw_correlation_evtime_ft0_tof:
        for i in histogram_names:
            if "fEvTimeTOF_vs_fEvTimeT0AC" not in i:
                continue
            hd = drawhisto(i)
            draw_diagonal(hd)
            draw_label(f"Correlation: {hd.GetCorrelationFactor():.2f}", 0.3, 0.85, 0.03)
            if ">" in i:
                draw_label("TOF ev. mult > " + i.split(">")[1], 0.3, 0.8, 0.03)

    # PID 2D plots
    if 1:
        for i in ["Pi", "Ka", "Pr"]:
            hd = drawhisto(f"Delta{i}T0AC_vs_fPt")
            plot2DPIDPlots.do_plot(hd)

    # Drawing the resolution of the T-TExpPi-Tev with the FT0
    if do_draw_resolution_with_FT0:
        hd = drawhisto("DeltaPiT0AC_vs_fPt")
        draw_nice_canvas("TOF_resolution_with_FT0")
        reso_pt_range = [1.3, 1.35]
        reso_pt_range_b = [hd.GetXaxis().FindBin(i) for i in reso_pt_range]
        htof_reso_with_ft0 = hd.ProjectionY("TOF_resolution_with_FT0", *reso_pt_range_b)
        draw_nice_frame(None, htof_reso_with_ft0, [0, htof_reso_with_ft0.GetMaximum()], htof_reso_with_ft0, yt="Counts")
        htof_reso_with_ft0.Draw("same")
        if 0:  # Gaussian model
            fgaus_reso_with_ft0 = TF1("fgaus_reso_with_ft0", "gaus", -1000, 1000)
        else:  # Gaussian + tail model
            fgaus_reso_with_ft0 = GaussianTail("tailgaus", -1000, 1000)
        htof_reso_with_ft0.Fit(fgaus_reso_with_ft0, "N", "", -200, 200)
        fgaus_reso_with_ft0.Draw("same")
        draw_label(f"{reso_pt_range[0]:.2f} < #it{{p}}_{{T}} < {reso_pt_range[1]:.2f} GeV/#it{{c}}", 0.35, 0.85, 0.03)
        draw_label(f"#mu = {fgaus_reso_with_ft0.GetParameter(1):.2f} (ps)", 0.35, 0.8, 0.03)
        reso = fgaus_reso_with_ft0.GetParameter(2)
        draw_label(f"#sigma = {reso:.2f} (ps)", 0.35, 0.75, 0.03)
        if value_ft0AC_resolution is not None:
            reso = sqrt(reso**2 - value_ft0AC_resolution**2/2)
            draw_label(f"#sigma_{{FT0AC ev. time}} = {value_ft0AC_resolution:.2f} (ps)", 0.35, 0.7, 0.03)
            draw_label(f"#sigma (ev. time sub.) = {reso:.2f} (ps)", 0.35, 0.65, 0.03)
        draw_plot_label()

    # Drawing the delta for pos and neg
    if do_draw_comparison_pos_neg:
        for i in ["DeltaPrTOF_vs_fPt_Pos", "DeltaPrTOF_vs_fPt_Neg"]:
            hd = drawhisto(i)
            fitres = TObjArray()
            hd.FitSlicesY(TF1("fgaus", "gaus", -300, 300), -1, -1, 10, "QNRG5", fitres)
            draw_label(hd.GetName())
            fitres[1].Draw("same")
            fitres[1].SetLineColor(TColor.GetColor("#377eb8"))
            fitres[2].SetLineColor(TColor.GetColor("#4daf4a"))
            for ff in fitres:
                # ff.SetLineWidth(2)
                ff.SetMarkerColor(ff.GetLineColor())
            leg = draw_nice_legend([0.83, 0.92], [0.83, 0.92], columns=2)
            leg.AddEntry(fitres[1], "#mu", "l")

    # test
    # plotDeltaTVsEta.process(histograms=histograms)
    # Time alignment vs eta
    if 1:
        hd = drawhisto("DeltaPiT0AC_vs_fEta", transpose=False)
        fgaus_eta_model = GaussianTail("fgaus_eta_model", -1000, 1000)
        fgaus_eta_model.SetParameter(1, 0)
        fgaus_eta_model.SetParLimits(1, -300, 300)
        result_arr = TObjArray()
        hd.FitSlicesY(fgaus_eta_model, 1, -1, 10, "QNR", result_arr)
        result_arr.At(1).SetLineWidth(2)
        result_arr.At(1).SetLineColor(4)
        result_arr.At(1).Draw("same")
        result_arr.At(2).SetLineWidth(2)
        result_arr.At(2).SetLineColor(1)
        result_arr.At(2).Draw("same")
        leg = draw_nice_legend([0.63, 0.91], [0.25, 0.35])
        leg.AddEntry(result_arr.At(1), "#mu", "l")
        leg.AddEntry(result_arr.At(2), "#sigma", "l")
        tit = hd.GetTitle().split(" ")
        tit = f"{tit[-5]} < #it{{p}}_{{T}} < {tit[-1]} GeV/#it{{c}}"
        ptlabel = draw_label(tit, x=0.14, y=0.97, align=11)
        can = draw_nice_canvas("singlebin")
        for i in range(1, hd.GetNbinsX()+1):
            hproj = hd.ProjectionY(f"singlebin_{i}", i, i)
            hproj.Draw()
            for j in range(fgaus_eta_model.GetNpar()):
                fgaus_eta_model.SetParameter(j, result_arr.At(j).GetBinContent(i))
            if 1:  # Refit
                hproj.Fit(fgaus_eta_model, "QNRWW", "", -200 + fgaus_eta_model.GetParameter(1), 200 + fgaus_eta_model.GetParameter(1))
                for j in range(fgaus_eta_model.GetNpar()):
                    result_arr.At(j).SetBinContent(i, fgaus_eta_model.GetParameter(j))
                    result_arr.At(j).SetBinError(i, fgaus_eta_model.GetParError(j))
            fgaus_eta_model.Draw("same")
            can.Modified()
            can.Update()
            # input("Press enter to continue")
        ptlabel.Draw()
        ptlabel.Draw()
        draw_nice_canvas("etaAlignment")
        draw_nice_frame(None, result_arr.At(1), [-100, 100], result_arr.At(1), "ps")
        result_arr.At(1).Draw("SAME")
        result_arr.At(2).Draw("same")
        leg.Draw()
        ptlabel.Draw()
        ptlabel.Draw()

    # Time alignment and resolution vs phi for eta slices
    if 1:
        for i in histograms:
            if "DeltaPiT0AC_vs_fPhi_EtaRange" in i:
                continue
            print(i)

    # Drawing reference histogram
    if 0:
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
        draw_plot_label()

    # Drawing the resolution of the double delta with the reference subtracted
    if 0:
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
        for j in reso_graphs:
            r_graph = reso_graphs[j]
            hn = "fDoubleDelta_vs_" + j
            r_graph.GetYaxis().SetTitle("#sigma " + histograms[hn].GetYaxis().GetTitle())
            for i in range(int((stopP - startP) / pwidth)):
                xmin = startP + i * pwidth
                xmax = xmin + pwidth
                reso_histo = histograms[hn]
                reso_histo = reso_histo.ProjectionY(f"reso_histo_{j}_{xmin}_{xmax}",
                                                    reso_histo.GetXaxis().FindBin(xmin + 0.00001),
                                                    reso_histo.GetXaxis().FindBin(xmax - 0.0001))
                reso_gaus = TF1("reso_gaus_" + j, "gaus", -1000, 1000)
                reso_histo.Fit(reso_gaus, "QNRWW")
                r_graph.SetPoint(r_graph.GetN(), (xmin + xmax) / 2, sqrt(reso_gaus.GetParameter(2) ** 2 - reference_gaus.GetParameter(2) ** 2 / 2))
                r_graph.SetPointError(r_graph.GetN() - 1, (xmax - xmin) / 2, reso_gaus.GetParError(2))
                if 0:
                    draw_nice_canvas(f"reso_histo_vs_{j}_{i}")
                    reso_histo.Draw()
                    draw_label(f"#mu = {reso_gaus.GetParameter(1):.3f}", 0.3, 0.8)
                    draw_label(f"#sigma = {reso_gaus.GetParameter(2):.3f}", 0.3, 0.75)

            draw_nice_canvas("reso_histo_vs_" + j)
            r_graph.Draw("AP")
            draw_plot_label()

    # Drawing Double delta vs Pt and P
    if 0:
        for k in ["fPt", "fP"]:
            hd = drawhisto("fDoubleDelta_vs_" + k, opt="COL", xrange=[0, 5], transpose=True)
            colors = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3"]
            leg = draw_nice_legend([0.74, 0.92], [0.74, 0.92])
            if 1:  # Show prediction
                for i in ["El", "Mu", "Ka", "Pr"]:
                    col = TColor.GetColor(colors.pop())
                    particle_profile = histograms["DeltaPi" + i + "_vs_" + k].ProfileX()
                    particle_profile.SetName("profile_" + particle_profile.GetName())
                    if 1:
                        g = graph("g" + particle_profile.GetName(), particle_profile.GetTitle())
                        for j in range(1, particle_profile.GetNbinsX() + 1):
                            if 1:
                                starting_pt = {"El": 0.4,
                                               "Mu": 0.4,
                                               "Ka": 0.9,
                                               "Pr": 1.8}
                                if i in starting_pt:
                                    if (particle_profile.GetBinCenter(j) < starting_pt[i]):
                                        continue
                            if 0:
                                timepred = particle_profile.GetXaxis().GetBinCenter(j)
                                if "transpose" in hd.GetName():
                                    timepred = particle_profile.GetBinContent(j)
                                if i == "El":
                                    if timepred < -1000:
                                        continue
                                    if timepred > -5:
                                        continue
                                elif i == "Mu":
                                    if timepred < -500:
                                        continue
                                    if timepred > -5:
                                        continue
                                elif i in ["Ka"]:
                                    if timepred < 40:
                                        continue
                                elif i in ["Pr"]:
                                    if timepred < 130:
                                        continue
                            if "transpose" in hd.GetName():
                                g.SetPoint(g.GetN(), particle_profile.GetBinContent(j), particle_profile.GetBinCenter(j))
                            else:
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
        draw_plot_label()
        return obj

    # Fit slices
    do_draw_slices = False
    if do_draw_slices:
        for i in histograms:
            if "fEvTimeTOF_vs_fEvTimeT0AC" in i:
                continue
            if "fPt_" in i or "fP_" in i:
                continue
            if "_fPt" in i or "_fP" in i:
                continue
            if "_fEta" in i:
                continue
            if "_fPhi" in i:
                continue
            if "vs" in i:
                fitmultslices(i)
        fitmultslices("fDoubleDelta_vs_fEvTimeTOFMult")

    # Resolution vs TOF Multiplicity
    if do_draw_resolution_vs_mult:
        draw_nice_canvas("DeltaEvTime")
        colors = ["#e41a1c", "#377eb8", "#4daf4a"]
        projections = []
        for i in ["DeltaPiTOF_vs_fEvTimeTOFMult",
                  "DeltaPiT0AC_vs_fEvTimeTOFMult",
                  "fDoubleDelta_vs_fEvTimeTOFMult"]:
            b = histograms[i].GetXaxis().FindBin(12)
            p = histograms[i].ProjectionY(i + "_proj", b)
            if i == "DeltaPiTOF_vs_fEvTimeTOFMult":
                p.Draw()
            else:
                p.Draw("same")
            p.Draw()
            p.SetDirectory(0)
            p.SetBit(TH1.kNoStats)
            p.SetBit(TH1.kNoTitle)
            p.SetLineColor(TColor.GetColor(colors.pop()))
            projections.append(p)
        leg = draw_nice_legend([0.64, 0.92], [0.57, 0.92])
        for i in projections:
            print(i)
            leg.AddEntry(i, "", f"{p.GetTitle()} {p.Integral()} #mu = {p.GetMean():.2f}")
        draw_plot_label()

    multiplicity_range = [0, 45]
    max_multiplicity = 25
    # Drawing the event time resolution
    if 1:
        colors = ["#e41a1c", "#377eb8", "#4daf4a"]
        draw_nice_canvas("resolutionEvTimevsTOFMult")
        draw_nice_frame(None,
                        multiplicity_range,
                        [0, 200],
                        "TOF ev. mult.",
                        "#sigma (ps)")
        leg = draw_nice_legend([0.64, 0.92], [0.57, 0.92])
        for i in h_slices:
            print("Drawing slice for event time resolution", i)
            if "fEvTimeTOF_" not in i and "fEvTimeT0AC_" not in i and "EvTimeReso_" not in i:
                continue
            col = TColor.GetColor(colors.pop())
            s = h_slices[i].At(2).DrawCopy("SAME")
            for j in range(1, s.GetNbinsX() + 1):
                if s.GetXaxis().GetBinCenter(j) > max_multiplicity:
                    s.SetBinContent(j, 0)
                    s.SetBinError(j, 0)
            s.SetLineColor(col)
            s.SetMarkerColor(col)
            s.SetMarkerStyle(20)
            if "EvTimeReso_" in i:
                s.SetTitle(s.GetTitle()
                            .replace("ev. time", "")
                            .strip()
                           .replace("#sigma", "#sigma(")
                           + ")")
                fasympt = TF1("fasympt", "sqrt([0]*[0]/x + [1]*[1])", 0, 40)
                mult_value = 30
                fasympt.SetParameter(0, -5.81397e01)
                s.Fit(fasympt, "QNWW", "", 4, 20)
                fasympt.SetLineStyle(7)
                fasympt.SetLineColor(s.GetLineColor())
                fasympt.DrawClone("same")
                draw_label(f"{hd.GetTitle()}|_{{{mult_value}}} = {fasympt.Eval(mult_value):.1f} ps",
                           mult_value,
                           fasympt.Eval(mult_value) + 5,
                           align=11,
                           ndc=False,
                           size=0.02)
            leg.AddEntry(s)
        draw_plot_label()

        # Drawing the event time resolution alone
        colors = ["#e41a1c"]
        draw_nice_frame(draw_nice_canvas("resolutionEvTimeOnly"),
                        multiplicity_range,
                        [0, 200],
                        "TOF ev. mult.",
                        "#sigma(t_{ev}^{FT0} - t_{ev}^{TOF}) (ps)")
        for i in h_slices:
            print("Drawing slice for event time resolution", i)
            if "EvTimeReso_" not in i:
                continue
            col = TColor.GetColor(colors.pop())
            s = h_slices[i].At(2).DrawCopy("SAME")
            # Resetting the first bin
            s.SetBinContent(1, 0)
            s.SetBinError(1, 0)
            for j in range(1, s.GetNbinsX() + 1):
                if s.GetXaxis().GetBinCenter(j) > max_multiplicity:
                    s.SetBinContent(j, 0)
                    s.SetBinError(j, 0)
            s.SetLineColor(col)
            s.SetMarkerColor(col)
            s.SetMarkerStyle(20)
            if "EvTimeReso_" in i:
                s.SetTitle(s.GetTitle()
                            .replace("ev. time", "")
                            .strip()
                           .replace("#sigma", "#sigma(")
                           + ")")
                fasympt = TF1("fasympt", "sqrt([0]*[0]/x + [1]*[1])", 0, 40)
                mult_value = 30
                fasympt.SetParameter(0, -5.81397e01)
                s.Fit(fasympt, "QNWW", "", 4, 20)
                fasympt.SetLineStyle(7)
                fasympt.SetLineColor(s.GetLineColor())
                fasympt.DrawClone("same")
                draw_label(f"{s.GetTitle()}|_{{{mult_value}}} = {fasympt.Eval(mult_value):.1f} ps",
                           mult_value,
                           fasympt.Eval(mult_value) + 5,
                           align=11,
                           ndc=False,
                           size=0.02)
        draw_plot_label()

    # Drawing the event time resolution
    if do_draw_slices:
        colors = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]
        # ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33']
        draw_nice_frame(draw_nice_canvas("resolutionDelta"),
                        multiplicity_range,
                        [0, 150],
                        "TOF ev. mult.",
                        "#sigma (ps)")
        leg = draw_nice_legend([0.2, 0.48], [0.2, 0.45])
        drawn_slices = {}
        for i in h_slices:
            print("Drawing slice", i)
            if "fEvTimeTOF_" in i:
                continue
            if "fEvTimeT0AC_" in i:
                continue
            if "EvTimeReso_vs_fEvTimeTOFMult" in i:
                continue
            col = TColor.GetColor(colors.pop())
            s = h_slices[i].At(2).DrawCopy("SAME")
            for j in range(1, s.GetNbinsX() + 1):
                if s.GetXaxis().GetBinCenter(j) > max_multiplicity:
                    s.SetBinContent(j, 0)
                    s.SetBinError(j, 0)
            drawn_slices[i] = s
            if "DoubleDelta" in i and "reference" not in i:
                for j in range(1, s.GetNbinsX() + 1):
                    diff = (s.GetBinContent(j) ** 2 - h_slices["fDoubleDelta_vs_fEvTimeTOFMult_reference"].At(2).GetBinContent(j) ** 2 / 2)
                    if diff >= 0:
                        s.SetBinContent(j, sqrt(diff))
            s.SetLineColor(col)
            s.SetMarkerColor(col)
            s.SetMarkerStyle(20)
            leg.AddEntry(s)

        drawn_slices["fDoubleDelta_vs_fEvTimeTOFMult_reference"].Scale(1.0 / sqrt(2))
        # draw_label(f"{minPt:.2f} < #it{{p}}_{{T}} < {maxPt:.2f} GeV/#it{{c}}", 0.2, 0.97, align=11)
        draw_label(f"{minPt:.2f} < #it{{p}} < {maxPt:.2f} GeV/#it{{c}}", 0.2, 0.97, align=11)
        draw_plot_label()

        if 1:
            # fasympt = TF1("fasympt", "[0]/x^[2]+[1]", 0, 40)
            fasympt = TF1("fasympt", "sqrt([0]*[0]/x + [1]*[1])", 0, 40)
            mult_value = 30
            for i in drawn_slices:
                hd = drawn_slices[i]
                fasympt.SetParameter(0, -5.81397e01)
                hd.Fit(fasympt, "QNWW", "", 3, 20)
                fasympt.SetLineStyle(7)
                fasympt.SetLineColor(drawn_slices[i].GetLineColor())
                fasympt.DrawClone("same")
                draw_label(f"{hd.GetTitle()}|_{{{mult_value}}} = {fasympt.Eval(mult_value):.1f} ps",
                           mult_value,
                           fasympt.Eval(mult_value) + 5,
                           align=11,
                           ndc=False,
                           size=0.02)

    all_canvases = update_all_canvases()

    wait_for_input()

    # Saving images
    if 1:
        imgdir = "/tmp/tofreso/"
        imgdir = os.path.join("/tmp/", "tofreso")
        if not os.path.isdir(imgdir):
            os.makedirs(imgdir)
        for i in all_canvases:
            all_canvases[i].SaveAs(os.path.join(imgdir, i + ".png"))
            all_canvases[i].SaveAs(os.path.join(imgdir, i + ".pdf"))

    if replay_mode:
        return

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
    parser.add_argument("--background", "-b", action="store_true", help="Background mode")
    parser.add_argument("--minpt", default=0.3, type=float, help="Minimum transverse momentum")
    parser.add_argument("--maxpt", default=0.4, type=float, help="Maximum transverse momentum")
    parser.add_argument("--maxfiles", default=-1, type=int, help="Maximum number of files")
    parser.add_argument("--jobs", "-j", default=4, type=int, help="Number of multithreading jobs")
    parser.add_argument("--tag", "-t", default="", help="Tag to use for the output file name")
    parser.add_argument("--replay_mode", "--replay", action="store_true", help="Replay previous output")
    parser.add_argument("--label", "-l", help="Label to put on plots", nargs="+", default=[""])
    parser.add_argument("--draw_correlation_evtime_ft0_tof", action="store_true", help="do_draw_correlation_evtime_ft0_tof")
    args = parser.parse_args()
    EnableImplicitMT(args.jobs)
    if args.background:
        gROOT.SetBatch(True)
    main(args.filename,
         minPt=args.minpt,
         maxPt=args.maxpt,
         replay_mode=args.replay_mode,
         max_files=args.maxfiles,
         out_file_name=f"/tmp/TOFRESO{args.tag}.root",
         label=" ".join(args.label).strip(),
         do_draw_correlation_evtime_ft0_tof=args.draw_correlation_evtime_ft0_tof)
