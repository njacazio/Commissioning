#!/usr/bin/env python3

"""
Plot the delta T vs eta and its resolution
"""

if 1:
    import sys
    import os
    this_file_path = os.path.dirname(__file__)
    sys.path.append(this_file_path)
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/AO2D/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/utilities/")))
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, definenicepalette, make_color_range, draw_label
    from common import get_default_parser

from ROOT import TFile, TF1, TObjArray
import argparse
from plotDeltaTSlices import get_from_file

definenicepalette()


def process(histograms, wait_every_bin=False):
    if type(histograms) is dict:
        h = []
        for i in histograms:
            if "DeltaPiT0AC_vs_fPhi_EtaRange=" not in i:
                continue
            h.append(histograms[i])
        histograms = h
    fit_results = []
    colors = make_color_range(len(histograms))
    color_dict = {}
    can = draw_nice_canvas("DeltaPiT0AC_vs_fPhi_EtaRange_for_eta")
    for i in histograms:
        name = i.GetName()
        etarange = name.split("[")[1].strip("]")
        print(etarange)
        etarange = [float(x) for x in etarange.split(", ")]
        etarange_tit = f"{etarange[0]:.2f} < #eta < {etarange[1]:.2f}"
        i.SetTitle(etarange_tit)
        set_nice_frame(i)
        i.Draw("col")
        draw_label(etarange_tit)
        fitres = TObjArray()
        i.FitSlicesY(TF1("fgaus", "gaus", -300, 300), -1, -1, 10, "QNRWW", fitres)
        fitres[1].SetName("Mu"+name)
        fitres[2].SetName("Sigma"+name)
        color = colors.pop(0)
        color_dict[etarange_tit] = color
        fitres[1].SetLineColor(color)
        fitres[1].SetMarkerColor(color)
        fitres[1].SetMarkerStyle(20)
        fitres[1].GetYaxis().SetTitle(f"#mu ({i.GetYaxis().GetTitle()})")
        fitres[1].SetTitle(etarange_tit)
        fitres[2].SetLineColor(color)
        fitres[2].SetMarkerColor(color)
        fitres[2].SetMarkerStyle(20)
        fitres[2].GetYaxis().SetTitle(f"#sigma ({i.GetYaxis().GetTitle()})")
        fit_results.append(fitres)
        fitres[2].SetTitle(etarange_tit)
        can.Modified()
        can.Update()
        if wait_every_bin:
            input("Press enter to continue")

    cmean = draw_nice_canvas("mean")
    draw_nice_frame(cmean, histograms[0], [-100, 100], "#phi", "#mu (ps)")

    csigma = draw_nice_canvas("sigma")
    draw_nice_frame(csigma, histograms[0], [0, 140], "#phi", "#sigma (ps)")

    lsigma = draw_nice_legend([0.6, 0.92], [0.21, 0.45], columns=2)
    cmean.cd()
    lsigma.Draw()
    for i in fit_results:
        cmean.cd()
        i[1].Draw("same")
        csigma.cd()
        i[2].Draw("same")
        lsigma.AddEntry(i[2])

    update_all_canvases()


def process_phiintegrated(histograms):
    if type(histograms) is dict:
        h = []
        for i in histograms:
            if "DeltaPiT0AC_vs_fEta" not in i:
                continue
            h.append(histograms[i])
        histograms = h
    fit_results = []
    colors = make_color_range(len(histograms))
    color_dict = {}
    can = draw_nice_canvas("DeltaPiT0AC_vs_fEta")
    for i in histograms:
        name = i.GetName()
        etarange = [i.GetXaxis().GetBinLowEdge(1),
                    i.GetXaxis().GetBinUpEdge(i.GetXaxis().GetNbins())]
        etarange_tit = f"{etarange[0]:.2f} < #eta < {etarange[1]:.2f}"
        i.SetTitle(etarange_tit)
        set_nice_frame(i)
        i.Draw("col")
        draw_label(etarange_tit)
        fitres = TObjArray()
        i.FitSlicesY(TF1("fgaus", "gaus", -300, 300), -1, -1, 10, "QNRWW", fitres)
        fitres[1].SetName("Mu"+name)
        fitres[2].SetName("Sigma"+name)
        color = colors.pop(0)
        color_dict[etarange_tit] = color
        fitres[1].SetLineColor(color)
        fitres[1].SetMarkerColor(color)
        fitres[1].SetMarkerStyle(20)
        fitres[1].GetYaxis().SetTitle(f"#mu ({i.GetYaxis().GetTitle()})")
        fitres[1].SetTitle(etarange_tit)
        fitres[2].SetLineColor(color)
        fitres[2].SetMarkerColor(color)
        fitres[2].SetMarkerStyle(20)
        fitres[2].GetYaxis().SetTitle(f"#sigma ({i.GetYaxis().GetTitle()})")
        fit_results.append(fitres)
        fitres[2].SetTitle(etarange_tit)
        fitres[1].Draw("SAME")
        fitres[2].Draw("SAME")
        fitres[1].SetLineColor(1)
        fitres[2].SetLineColor(4)
        fitres[1].SetMarkerColor(1)
        fitres[2].SetMarkerColor(4)
        fitres[1].SetDirectory(0)
        fitres[2].SetDirectory(0)
        can.Modified()
        can.Update()

    cmean = draw_nice_canvas("mean")
    draw_nice_frame(cmean, histograms[0], [-100, 100], "#phi", "#mu (ps)")

    csigma = draw_nice_canvas("sigma")
    draw_nice_frame(csigma, histograms[0], [0, 140], "#phi", "#sigma (ps)")

    lsigma = draw_nice_legend([0.6, 0.92], [0.21, 0.45], columns=2)
    cmean.cd()
    lsigma.Draw()

    for i in fit_results:
        cmean.cd()
        i[1].Draw("same")
        csigma.cd()
        i[2].Draw("same")
        lsigma.AddEntry(i[2])
    update_all_canvases()
    return fitres[1], fitres[2]


def main(fnames=["/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root"],
         process_integrated=True):
    single_output = {}

    def process_one(fname):
        print(fname)
        h = []
        h_phi_integrated = []
        fin = TFile(fname, "READ")
        for i in fin.GetListOfKeys():
            if "DeltaPiT0AC_vs_fPhi_EtaRange=" in i.GetName():
                h.append(fin.Get(i.GetName()))
            elif "DeltaPiT0AC_vs_fEta" in i.GetName():
                h_phi_integrated.append(fin.Get(i.GetName()))
        if process_integrated:
            single_output[fname] = process_phiintegrated(h_phi_integrated)
        else:
            process(h)
    for i in fnames:
        process_one(i)

    meandrawn = {}
    sigmadrawn = {}
    if len(fnames) > 1:
        colors = make_color_range(len(fnames))

        draw_nice_frame(draw_nice_canvas("comparisonMean"), [-1, 1], [-100, 100], "#eta", "#mu (ps)")
        leg = draw_nice_legend(x=[0.55, 0.87],
                               y=[0.28, 0.5])
        for n, i in enumerate(single_output):
            hd = single_output[i][0].DrawCopy("same")
            hd.SetLineColor(colors[n])
            hd.SetMarkerColor(colors[n])
            hd.SetTitle(i.split("_")[1])
            hd.SetDirectory(0)
            meandrawn[i] = hd
            leg.AddEntry(hd)
            if leg.GetHeader() == "":
                leg.SetHeader("{} {}".format(i.split("_")[2].replace("pt", "#it{p}_{T} = ["), i.split("_")[3].replace(".root", "] GeV/#it{c}")))

        draw_nice_frame(draw_nice_canvas("comparisonSigma"), [-1, 1], [0, 150], "#eta", "#sigma (ps)")
        for n, i in enumerate(single_output):
            hd = single_output[i][1].DrawCopy("same")
            hd.SetLineColor(colors[n])
            hd.SetMarkerColor(colors[n])
            hd.SetTitle(i.split("_")[1])
            hd.SetDirectory(0)
            sigmadrawn[i] = hd
        leg.Draw()

    if 0:
        csofia = get_from_file("/tmp/SigmaEtaPhi.root", "c1")
        for i in csofia.GetListOfPrimitives():
            if "TGraph" not in i.ClassName():
                continue
            csigma.cd()
            for j in color_dict:
                if j == i.GetTitle():
                    i.SetLineColor(color_dict[j])
                    i.SetMarkerColor(color_dict[j])
                    break
            i.Draw("sameLP")

    update_all_canvases()
    input("Press enter to continue")


if __name__ == "__main__":
    parser = get_default_parser(__doc__)
    parser.add_argument("--input", "-i", default=["/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root"],
                        nargs="+", help="Input file name")
    args = parser.parse_args()
    main(fnames=args.input)
