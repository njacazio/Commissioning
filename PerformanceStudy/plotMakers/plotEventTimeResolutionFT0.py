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

from ROOT import TGraph, TColor, TF1, TObjArray, TH1F, TH1
import argparse
from plotDeltaTSlices import get_from_file


# Fitting slices in multiplicity
h_slices = {}


def fitmultslices(h):
    hn = h.GetName()
    # draw_nice_canvas(hn+"slice", replace=False)
    obj = TObjArray()
    # leg = draw_nice_legend([0.82, 0.92], [0.78, 0.92])
    h.FitSlicesY(0, 0, -1, 0, "QNRWW", obj)
    obj.At(1).SetTitle(f"#mu {h.GetTitle()}")
    obj.At(2).SetTitle(f"#sigma {h.GetTitle()}")
    # leg.AddEntry(obj.At(1), "#mu", "l")
    # leg.AddEntry(obj.At(2), "#sigma", "l")
    obj.At(1).SetLineColor(TColor.GetColor("#e41a1c"))
    # obj.At(1).Draw("SAME")
    # obj.At(2).Draw("SAME")
    g = TGraph()
    g.SetPoint(0, h.GetXaxis().GetBinLowEdge(1), 0)
    g.SetPoint(1, h.GetXaxis().GetBinUpEdge(h.GetXaxis().GetNbins()), 0)
    g.SetLineStyle(7)
    # g.Draw("sameL")
    h.GetListOfFunctions().Add(g)
    h_slices[hn] = obj
    # draw_plot_label()
    return obj


def do_plot(histogram,
            do_draw=False,
            multiplicity_range=[0, 45],
            min_multiplicity=1,
            max_multiplicity=25):
    colors = ["#e41a1c", "#377eb8", "#4daf4a"]
    draw_nice_canvas(histogram.GetName()+"reso")
    tit = histogram.GetTitle().replace("vs TOF mult.", "")
    tit = histogram.GetTitle().replace("( ", "(")
    tit = f"#sigma({histogram.GetYaxis().GetTitle()})"
    histogram.SetTitle(tit)
    draw_nice_frame(None,
                    multiplicity_range,
                    [0, 200],
                    "TOF ev. mult.",
                    "#sigma (ps)")
    fitmultslices(histogram)
    # leg = draw_nice_legend([0.64, 0.92], [0.57, 0.92])
    for i in h_slices:
        col = TColor.GetColor(colors.pop())
        col = 1
        s = h_slices[i].At(2).DrawCopy("SAME")
        for j in range(1, s.GetNbinsX() + 1):
            if s.GetXaxis().GetBinCenter(j) < min_multiplicity:
                s.SetBinContent(j, 0)
                s.SetBinError(j, 0)
            if s.GetXaxis().GetBinCenter(j) > max_multiplicity:
                s.SetBinContent(j, 0)
                s.SetBinError(j, 0)
        s.SetLineColor(col)
        s.SetMarkerColor(col)
        s.SetMarkerStyle(20)
        s.SetTitle(s.GetTitle()
                    .replace("ev. time", "")
                    .strip()
                    .replace("#sigma", "#sigma(")
                   + ")")
        fasympt = TF1("fasympt", "sqrt([0]*[0]/(x) + [1]*[1])", 0, 40)
        fasympt.SetParameter(0, -5.81397e01)
        mult_value = 30
        s.Fit(fasympt, "QNWW", "", 4, 20)
        fasympt.SetLineStyle(7)
        fasympt.SetLineColor(s.GetLineColor())
        fasympt.DrawClone("same")
        draw_label(f"{histogram.GetTitle()}|_{{{mult_value}}} = {fasympt.Eval(mult_value):.1f} ps",
                   mult_value,
                   fasympt.Eval(mult_value) + 5,
                   align=11,
                   ndc=False,
                   size=0.02)
        # leg.AddEntry(s)


def main(input_filename="/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root",
         out_path="/home/njacazio/Overleaf/TOFPerformanceRun3/Common/img/"):
    definenicepalette()
    h = get_from_file(input_filename, "FT0AC_minus_TOF_vs_fEvTimeTOFMult")
    can = draw_nice_canvas(h.GetName())
    h.Draw("COL")
    do_plot(h, do_draw=True)
    update_all_canvases()
    wait_for_input()
    can.SaveAs(f"{out_path}/{can.GetName()}.pdf")
    can.SaveAs(f"{out_path}/{can.GetName()}.root")
    can.SaveAs(f"{out_path}/{can.GetName()}.png")


if __name__ == '__main__':
    parser = get_default_parser(__doc__)
    parser.add_argument("input_filename", default="/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root")
    args = parser.parse_args()
    main(args.input_filename)
