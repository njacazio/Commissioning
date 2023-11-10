#!/usr/bin/env python3

"""
Script to compare different runs and extract the resolution to check its stability
"""

if 1:
    import sys
    import os
    this_file_path = os.path.dirname(__file__)
    sys.path.append(this_file_path)
    print(this_file_path)
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/AO2D/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/utilities/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/")))
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, definenicepalette, make_color_range, draw_label
    from common import get_default_parser, wait_for_input

from ROOT import TFile, TF1, TObjArray, TH1F, TH1
import argparse
from plotDeltaTSlices import get_from_file


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
  f->SetParLimits(1, -100, 100);
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
    from ROOT import GaussianTail, gMinuit

import ROOT
from numpy import sqrt


def run_fit(h, fun, fit_range, strategy):
    print(f"Fitting with strategy {strategy}")
    ROOT.Math.MinimizerOptions().SetStrategy(strategy)
    r = h.Fit(fun, "QINS", "", *fit_range)
    st = gMinuit.fCstatu
    if "CONVERGED" not in st:
        print("Fit did not converge -> ", st)
        return None
    return r


def process(histogram, event_time_resolution=0):
    # histogram = drawhisto("DeltaPiT0AC_vs_fPt")
    reso_pt_range = [1.3, 1.35]
    if "TH2" in histogram.ClassName():
        draw_nice_canvas("TOF_resolution_with_FT0")
        reso_pt_range_b = [histogram.GetXaxis().FindBin(i) for i in reso_pt_range]
        htof_reso_with_ft0 = histogram.ProjectionY("TOF_resolution_with_FT0", *reso_pt_range_b)
    else:
        draw_nice_canvas("Resolution" + histogram.GetName(), replace=False)
        htof_reso_with_ft0 = histogram
    # htof_reso_with_ft0.Rebin(2)
    draw_nice_frame(None, htof_reso_with_ft0, [0, htof_reso_with_ft0.GetMaximum()], htof_reso_with_ft0, yt="Counts")
    htof_reso_with_ft0.DrawCopy("same")
    fgaus_reso_with_ft0 = TF1("fgaus_reso_with_ft0", "gaus", -1000, 1000)
    for i in [0, 1, 2]:
        run_fit(htof_reso_with_ft0, fgaus_reso_with_ft0, [-150, 150], i)
    prefit = [fgaus_reso_with_ft0.GetParameter(1), fgaus_reso_with_ft0.GetParameter(2)]
    # Gaussian + tail model
    if 1:
        fgaus_reso_with_ft0 = GaussianTail("tailgaus", -1000, 1000)
        fgaus_reso_with_ft0.SetParameter(1, prefit[0])
        fgaus_reso_with_ft0.SetParameter(2, prefit[1])
        for i in [0, 1, 2]:
            run_fit(htof_reso_with_ft0, fgaus_reso_with_ft0, [-200, 200], i)
    fgaus_reso_with_ft0.Draw("same")
    draw_label(f"{reso_pt_range[0]:.2f} < #it{{p}}_{{T}} < {reso_pt_range[1]:.2f} GeV/#it{{c}}", 0.35, 0.85, 0.03)
    mean = fgaus_reso_with_ft0.GetParameter(1)
    draw_label(f"#mu = {mean:.2f} (ps)", 0.35, 0.8, 0.03)
    reso = fgaus_reso_with_ft0.GetParameter(2)
    draw_label(f"#sigma = {reso:.2f} (ps)", 0.35, 0.75, 0.03)
    if event_time_resolution is not None:
        reso = sqrt(reso**2 - event_time_resolution**2/4)
        draw_label(f"#sigma_{{FT0AC ev. time}} = {event_time_resolution:.2f} (ps)", 0.35, 0.7, 0.03)
        draw_label(f"#sigma (ev. time sub.) = {reso:.2f} (ps)", 0.35, 0.65, 0.03)
    update_all_canvases()
    return {"mean": mean, "sigma": reso,
            "sigma_err": fgaus_reso_with_ft0.GetParError(2),
            "chi2": fgaus_reso_with_ft0.GetChisquare() / fgaus_reso_with_ft0.GetNDF()}


def process_event_time_resolution(histogram):
    i = histogram.GetName()
    draw_nice_canvas(i, replace=False)
    fun = TF1("fun", "gaus", -1000, 1000)
    histogram.Fit(fun, "QNRWW")
    histogram.Draw()
    fun.Draw("SAME")
    draw_label(f"#mu = {fun.GetParameter(1):.2f} (ps)", 0.35, 0.85, 0.03)
    draw_label(f"#sigma = {fun.GetParameter(2):.2f} (ps)", 0.35, 0.8, 0.03)
    return fun.GetParameter(2)


def process_event_resolution_vs_eta(histogram, draw=False):
    # hd = drawhisto("DeltaPiT0AC_vs_fEta", transpose=False)
    fgaus_eta_model = GaussianTail("fgaus_eta_model", -1000, 1000)
    result_arr = TObjArray()
    histogram.FitSlicesY(fgaus_eta_model, 1, -1, 10, "QNR", result_arr)
    result_arr.At(1).SetLineWidth(2)
    result_arr.At(1).SetLineColor(4)
    result_arr.At(2).SetLineWidth(2)
    result_arr.At(2).SetLineColor(1)
    if draw:
        draw_nice_canvas(histogram.GetName())
        result_arr.At(1).Draw("same")
        result_arr.At(2).Draw("same")
        leg = draw_nice_legend([0.63, 0.91], [0.25, 0.35])
        leg.AddEntry(result_arr.At(1), "#mu", "l")
        leg.AddEntry(result_arr.At(2), "#sigma", "l")
        can = draw_nice_canvas("singlebin")
    for i in range(1, histogram.GetNbinsX()+1):
        hproj = histogram.ProjectionY(f"singlebin_{i}", i, i)
        if draw:
            hproj.Draw()
        for j in range(fgaus_eta_model.GetNpar()):
            fgaus_eta_model.SetParameter(j, result_arr.At(j).GetBinContent(i))
        if 1:  # Refit
            hproj.Fit(fgaus_eta_model, "QNRWW", "", -200 + fgaus_eta_model.GetParameter(1), 200 + fgaus_eta_model.GetParameter(1))
            for j in range(fgaus_eta_model.GetNpar()):
                result_arr.At(j).SetBinContent(i, fgaus_eta_model.GetParameter(j))
                result_arr.At(j).SetBinError(i, fgaus_eta_model.GetParError(j))
        if draw:
            fgaus_eta_model.Draw("same")
            can.Modified()
            can.Update()
        # input("Press enter to continue")
    if draw:
        draw_nice_canvas("etaAlignment")
        draw_nice_frame(None, result_arr.At(1), [-100, 100], result_arr.At(1), "ps")
        result_arr.At(1).Draw("SAME")
        result_arr.At(2).Draw("same")
        leg.Draw()
    h_not_realigned = histogram.ProjectionY("h_not_realigned"+histogram.GetName(), 1, -1)
    h_not_realigned.SetLineColor(1)
    h_not_realigned.SetDirectory(0)

    h_realigned = h_not_realigned.Clone("h_realigned")
    h_realigned.SetLineColor(4)
    h_realigned.SetDirectory(0)
    h_realigned.Reset()
    for i in range(1, histogram.GetNbinsX()+1):
        s = result_arr.At(1).GetBinContent(i)
        for j in range(1, histogram.GetNbinsY()+1):
            x = histogram.GetYaxis().GetBinCenter(j) - s
            b = h_realigned.FindBin(x)
            h_realigned.SetBinContent(b, h_realigned.GetBinContent(b) + histogram.GetBinContent(i, j))
    draw_nice_canvas("hrealigned", replace=False)
    h_not_realigned.DrawCopy()
    h_realigned.DrawCopy("SAME")
    return h_realigned, h_not_realigned


def main(input_filenames):
    print(len(input_filenames), "files")
    h_run_by_run = TH1F("h_run_by_run", "h_run_by_run", len(input_filenames), 0, len(input_filenames))
    h_run_by_run.SetBit(TH1.kNoTitle)
    h_run_by_run.SetBit(TH1.kNoStats)
    h_run_by_run.GetXaxis().SetTitle("Run number")
    h_run_by_run.GetYaxis().SetTitle("#sigma(t-t_{exp}(#pi)-t_{ev}^{FT0AC}) (ps)")
    h_run_by_run_chi2 = h_run_by_run.Clone("h_run_by_run_chi2")
    h_run_by_run_chi2.GetYaxis().SetTitle("#chi^{2}/NDF")

    for b, i in enumerate(input_filenames):
        print("Filename", i)
        h = get_from_file(i, "DeltaPiT0AC_vs_fPt")
        h_vs_eta = get_from_file(i, "DeltaPiT0AC_vs_fEta")
        h_ev_time = get_from_file(i, "FT0A_minus_FT0C")
        h_realigned, h_not_realigned = process_event_resolution_vs_eta(h_vs_eta)
        ev_time_reso = process_event_time_resolution(h_ev_time)
        # r = process(h, ev_time_reso)
        # wait_for_input()
        r = process(h_realigned, ev_time_reso)
        # wait_for_input()
        # r = process(h_not_realigned, ev_time_reso)
        # wait_for_input()
        h_run_by_run.SetBinContent(b+1, r["sigma"])
        h_run_by_run.SetBinError(b+1, r["sigma_err"])
        h_run_by_run_chi2.SetBinContent(b+1, r["chi2"])
        t = i.split("/")[-1]
        t = t.replace(".root", "")
        t = t.replace("TOFRESO", "")
        t = t.split("apass1_")[1].split("_")[0]
        h_run_by_run.GetXaxis().SetBinLabel(b+1, t)
        h_run_by_run_chi2.GetXaxis().SetBinLabel(b+1, t)
        update_all_canvases()
        # wait_for_input()
    draw_nice_canvas("Run by run resolution")
    h_run_by_run.Draw()
    h_run_by_run.GetYaxis().SetRangeUser(60, 110)
    draw_nice_canvas("Run by run chi2")
    h_run_by_run_chi2.Draw("HIST")
    update_all_canvases()
    return h_run_by_run, h_run_by_run_chi2


if __name__ == "__main__":
    parser = get_default_parser(__doc__)
    parser.add_argument("input_filenames", nargs="+")
    args = parser.parse_args()
    r = main(args.input_filenames)
    wait_for_input()
