#!/usr/bin/env python3

from debugtrack import *
import numpy as np
import argparse
from ROOT import TFile, TChain, EnableImplicitMT, RDataFrame, gPad, TH1, TColor, TObjArray, gROOT, gStyle, TGraph, TF1, TGraphErrors, TH2F, TH1F
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


def make_color_range(ncolors, simple=False):
    if simple:
        if ncolors <= 3:
            colors = ['#e41a1c', '#377eb8', '#4daf4a']
        elif ncolors <= 4:
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
        elif ncolors < 5:
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
        else:
            colors = ['#00000', '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628', '#f781bf']
        return [TColor.GetColor(i) for i in colors]
    NRGBs = 5
    NCont = 256
    NCont = ncolors
    stops = np.array([0.00, 0.30, 0.61, 0.84, 1.00])
    red = np.array([0.00, 0.00, 0.57, 0.90, 0.51])
    green = np.array([0.00, 0.65, 0.95, 0.20, 0.00])
    blue = np.array([0.51, 0.55, 0.15, 0.00, 0.10])
    FI = TColor.CreateGradientColorTable(NRGBs,
                                         stops, red, green, blue, NCont)
    colors = []
    for i in range(NCont):
        colors.append(FI + i)
    colors = np.array(colors, dtype=np.int32)
    gStyle.SetPalette(NCont, colors)
    return [int(i) for i in colors]


def addDFToChain(input_file_name, chain):
    f = TFile(input_file_name, "READ")
    lk = f.GetListOfKeys()
    for i in lk:
        dfname = i.GetName()
        if "DF_" not in dfname:
            continue
        treename = f"{dfname}/O2skimmedtof"
        tree = f.Get(treename)
        if not tree:
            print("Waring: no tree found for", treename, "in", input_file_name)
            f.Get(dfname).ls()
            continue
        tree = tree.GetListOfBranches()
        if chain.GetEntries() == 0:
            tree.ls()

        def testbranch(b):
            hasit = False
            for i in tree:
                if i.GetName() == b:
                    hasit = True
                    break
            if not hasit:
                raise ValueError("No fPtSigned in", treename, "in", input_file_name)
                return False
            return True
        if not testbranch("fPtSigned"):
            return

        tname = "{}?#{}/O2skimmedtof".format(input_file_name, dfname)
        chain.Add(tname)
    f.Close()


histogram_names = []
histograms = {}
histomodels = {}


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
    if z is not None:
        if y is None:
            raise ValueError("Cannot have z without y")
        n = f"{z}_vs_{y}_vs_{x}"
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
              "fEvTimeT0AC": "t_{ev}^{FT0}"}
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
    if zt is None:
        if z in titles:
            zt = titles[z]
        else:
            zt = z

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
        if z is None:
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
         minPt=0.99,
         maxPt=1.01,
         replay_mode=False,
         max_files=-1,
         label=None,
         out_file_name="/tmp/TOFALIGN.root"):
    print("Using file:", input_file_name)

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
        ptaxis = [100, 0, 5]
        etaaxis = [32, -0.8, 0.8]
        phiaxis = [70, 0, 7]
        deltaaxis = [200, -2000, 2000]

        df = RDataFrame(chain)
        # df = df.Filter("fEta>0.3")
        # df = df.Filter("fEta<0.4")
        # df = df.Filter("fPhi>0.3")
        # df = df.Filter("fPhi<0.4")
        # df = df.Filter("fTOFChi2<5")
        # df = df.Filter("fTOFChi2>=0")
        # df = df.Filter("fPtSigned>=0")  # only positive tracks
        # df = df.Filter("fPtSigned<=0")  # only negative tracks

        df = df.Define("Charge", "fPtSigned>=0")
        df = df.Define("fPt", "TMath::Abs(fPtSigned)")
        df = df.Define("ExpTimePi", "ComputeExpectedTimePi(fTOFExpMom, fLength)")
        df = df.Define("DeltaPiTOF", "fTOFSignal - fEvTimeTOF - ExpTimePi")
        df = df.Define("isEvTimeTOF", "(fTOFFlags & PIDFlags::EvTimeTOF) == PIDFlags::EvTimeTOF")

        df = df.Filter("isEvTimeTOF == 1")
        df = df.Filter(f"fPt >= {minPt}")
        df = df.Filter(f"fPt <= {maxPt}")

        makehisto(df, x="DeltaPiTOF", y="fEta", z="Charge", xr=deltaaxis, yr=etaaxis, zr=[2, -0.5, 1.5], title="Delta vs Eta vs Charge")
        makehisto(df, x="DeltaPiTOF", y="fEta", z="fPhi", xr=deltaaxis, yr=etaaxis, zr=phiaxis, title="Delta vs Eta vs Phi")

        print("pre-processing done, it took", time.time()-start, "seconds")

    drawn_histos = []

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

    def drawhisto(hn, opt="COL", xrange=None, yrange=None, transpose=False):
        draw_nice_canvas(hn, replace=False, logz=False)
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
            for ix in range(1, xaxis.GetNbins()+1):
                # xb = htmp.GetYaxis().FindBin(xaxis.GetBinCenter(ix))
                for iy in range(1, yaxis.GetNbins()+1):
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
        return histograms[hn]

    print("List of histograms:")
    for i in histogram_names:
        print("\t", i)

    for i in histogram_names:
        start = time.time()
        print("+ Drawing histogram", i)
        hd = drawhisto(i)
        if "fEvTimeTOF_vs_fEvTimeT0AC" in i:
            draw_diagonal(hd)
            draw_label(f"Correlation: {hd.GetCorrelationFactor():.2f}", 0.3, 0.85, 0.03)
            if ">" in i:
                draw_label("TOF ev. mult > "+i.split(">")[1], 0.3, 0.8, 0.03)

        print("+ took", time.time()-start, "seconds")

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

    # fitmultslices("fEta_vs_DeltaPiTOF")
    if 1:
        h = histograms["Charge_vs_fEta_vs_DeltaPiTOF"]
        print(h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ())
        h.Print()
        h.GetZaxis().SetRange(1, 1)
        hneg = h.Project3D("yx")
        hneg.SetName("Negative charge")
        h.GetZaxis().SetRange(2, 2)
        hpos = h.Project3D("yx")
        hpos.SetName("Positive charge")

        def fitcharge(histo, name):
            h_vs_eta = []
            colors = make_color_range(histo.GetYaxis().GetNbins())
            mean = TH1F("mean"+name, f"mean{name};#eta;#mu (ps)", histo.GetYaxis().GetNbins(),
                        histo.GetYaxis().GetBinLowEdge(1), histo.GetYaxis().GetBinUpEdge(histo.GetYaxis().GetNbins()))
            sigma = TH1F("sigma"+name, f"sigma{name};#eta;#sigma (ps)", histo.GetYaxis().GetNbins(),
                         histo.GetYaxis().GetBinLowEdge(1), histo.GetYaxis().GetBinUpEdge(histo.GetYaxis().GetNbins()))
            for i in range(1, histo.GetYaxis().GetNbins()+1):
                etabin = [histo.GetYaxis().GetBinLowEdge(i), histo.GetYaxis().GetBinUpEdge(i)]
                p = histo.ProjectionX(f"slice{i}", i, i)
                fun = TF1(f"gaus{i}", "gaus", -500, 500)
                p.Fit(fun, "QNWW", "", -300, 300)
                if 0:
                    fit = draw_nice_canvas("fit", replace=True)
                    p.Draw()
                    fun.Draw("same")
                    draw_label(f"eta = {etabin}")
                    fit.Modified()
                    fit.Update()
                    input("Press enter to continue")
                mean.SetBinContent(i, fun.GetParameter(1))
                sigma.SetBinContent(i, fun.GetParameter(2))
                col = colors.pop(0)
                p.SetLineColor(col)
                p.SetMarkerColor(col)
                h_vs_eta.append(p)
            draw_nice_canvas("fEta_vs_DeltaPiTOF_vs_eta"+name, replace=False)
            h_vs_eta[0].DrawNormalized()
            draw_label(f"{minPt} < #it{{p}}_{{T}} < {maxPt} GeV/#it{{c}}", 0.76, 0.88)
            if name == "Pos":
                draw_label("Positive tracks", 0.835526, 0.962572)
            if name == "Neg":
                draw_label("Negative tracks", 0.835526, 0.962572)
            for i in h_vs_eta[1:]:
                i.DrawNormalized("SAME")
            draw_nice_canvas("mean"+name, replace=False)
            mean.Draw()
            gmean = TGraph()
            gmean.SetName("gmean"+name)
            for i in range(1, mean.GetNbinsX()+1):
                gmean.SetPoint(gmean.GetN(), mean.GetXaxis().GetBinCenter(i), mean.GetBinContent(i))
            gmean.Draw("LPsame")
            draw_nice_canvas("sigma"+name, replace=False)
            sigma.Draw()
            gmean.SaveAs(f"/tmp/gmean_{name}.root")
            return mean, sigma, h_vs_eta, gmean

        neg = fitcharge(hneg, "Neg")
        pos = fitcharge(hpos, "Pos")

    all_canvases = update_all_canvases()

    if not gROOT.IsBatch():
        input("Press enter to exit")
    # Saving images
    if 1:
        imgdir = os.path.join("/tmp/", "tofalign")
        if not os.path.isdir(imgdir):
            os.makedirs(imgdir)
        for i in all_canvases:
            all_canvases[i].SaveAs(os.path.join(imgdir, i + ".png"))
            all_canvases[i].SaveAs(os.path.join(imgdir, i + ".pdf"))
    if not replay_mode:
        print("Writing output to", out_file_name)
        fout = TFile(out_file_name, "RECREATE")
        fout.cd()
        for i in histograms:
            print("Writing", i)
            if "transpose" in histograms[i].GetName():
                histograms[i].Write(histograms[i].GetName().replace("transpose", "").replace("_copy", ""))
            else:
                histograms[i].Write()
        fout.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Input file name", nargs="+")
    parser.add_argument("--background", "-b", action="store_true", help="Background mode")
    parser.add_argument("--minpt", default=0.99, type=float, help="Minimum transverse momentum")
    parser.add_argument("--maxpt", default=1.01, type=float, help="Maximum transverse momentum")
    parser.add_argument("--maxfiles", default=-1, type=int, help="Maximum number of files")
    parser.add_argument("--jobs", "-j", default=4, type=int, help="Number of multithreading jobs")
    parser.add_argument("--tag", "-t", default="", help="Tag to use for the output file name")
    parser.add_argument("--replay_mode", "--replay", action="store_true", help="Replay previous output")
    parser.add_argument("--label", "-l", help="Label to put on plots")
    args = parser.parse_args()
    EnableImplicitMT(args.jobs)
    if args.background:
        gROOT.SetBatch(True)
    main(args.filename, minPt=args.minpt, maxPt=args.maxpt, replay_mode=args.replay_mode, max_files=args.maxfiles, out_file_name=f"/tmp/TOFALIGN{args.tag}.root", label=args.label)
