#!/usr/bin/env python3

"""
Script to plot the TOF event time vs T0AC event time
"""

if 1:
    import sys
    import os
    this_file_path = os.path.dirname(__file__)
    sys.path.append(this_file_path)
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/AO2D/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/utilities/")))
    sys.path.append(os.path.abspath(os.path.join(this_file_path, "../../QC/analysis/")))
    from common import get_default_parser, wait_for_input


from plotDeltaTSlices import get_from_file
import subprocess
from ROOT import TFile, TH1, TF1
import sys
import os
sys.path.append(os.path.abspath("../../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal, definenicepalette


def main(input_filename="/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root",
         more_labels=["ALICE Performance", "pp #sqrt{#it{s}} = 13.6 TeV"],
         range_delta=[-1000, 1000]):
    definenicepalette()

    def make_correlation_plot(name):
        h = get_from_file(input_filename, name)
        if "ps" not in h.GetXaxis().GetTitle():
            h.GetXaxis().SetTitle(h.GetXaxis().GetTitle() + " (ps)")
        if "ps" not in h.GetYaxis().GetTitle():
            h.GetYaxis().SetTitle(h.GetYaxis().GetTitle() + " (ps)")
        if range_delta is not None:
            h.GetXaxis().SetRangeUser(*range_delta)
            h.GetYaxis().SetRangeUser(*range_delta)
        set_nice_frame(h)
        h.GetXaxis().SetLabelOffset(0.015)
        can = draw_nice_canvas(h.GetName())
        h.Draw("COL")
        draw_diagonal(h)
        xstart = 0.35
        ystart = 0.88
        if more_labels is not None:
            for i in more_labels:
                draw_label(i, xstart, ystart, size=0.04)
                ystart -= 0.05
        draw_label(f"Correlation: {h.GetCorrelationFactor():.2f}", xstart, ystart, 0.03)
        if ">" in h.GetName():
            draw_label("TOF ev. mult > "+h.GetName().split(">")[1], xstart, ystart-0.05, 0.03)
        can.SaveAs("/tmp/" + can.GetName() + ".png")
        can.SaveAs("/tmp/" + can.GetName() + ".pdf")

    for i in [0, 5, 15]:
        make_correlation_plot(f"fEvTimeTOF_vs_fEvTimeT0AC_fEvTimeTOFMult>{i}")

    hdiff = get_from_file(input_filename, "FT0AC_minus_TOF_vs_fEvTimeTOFMult")
    # hdiff = get_from_file(input_filename, "EvTimeResoFT0_vs_fEvTimeTOFMult")
    draw_nice_canvas(hdiff.GetName())
    hdiff.Draw("COL")

    draw_nice_canvas("evtimeslices")
    minmult = 15
    hp = hdiff.ProjectionY("hprojection", hdiff.GetXaxis().FindBin(minmult), -1)
    set_nice_frame(hp)
    if "ps" not in hp.GetXaxis().GetTitle():
        hp.GetXaxis().SetTitle(hp.GetXaxis().GetTitle() + " (ps)")
    hp.SetBit(TH1.kNoTitle)
    hp.SetBit(TH1.kNoStats)
    hp.SetMarkerStyle(20)
    hp.SetMarkerColor(1)
    hp.GetXaxis().SetRangeUser(-600, 600)
    hp.GetYaxis().SetTitle("Normalized counts")
    hp = hp.DrawNormalized("E1")
    xstart = 0.33
    ystart = 0.88
    if more_labels is not None:
        for i in more_labels:
            draw_label(i, xstart, ystart, size=0.04)
            ystart -= 0.05
    draw_label(f"TOF track multiplicity > {minmult}", xstart, ystart, size=0.03)
    ystart -= 0.05
    if 1:
        ystartleft = 0.7
        fun = TF1(f"{hp.GetName()}_fit", "gaus", -400, 400)
        hp.Fit(fun, "QNWW", "", -200, 200)
        fun.Draw("SAME")
        ystartleft -= 0.08
        xleft = 0.22
        draw_label("Gaussian model", xleft, ystartleft, align=11)
        ystartleft -= 0.05
        draw_label(f"#mu = {fun.GetParameter(1):.2f} ps", xleft, ystartleft, align=11)
        ystartleft -= 0.05
        draw_label(f"#sigma = {fun.GetParameter(2):.2f} ps", xleft, ystartleft, align=11)

    cans = update_all_canvases()
    input("Press enter to continue")
    for i in cans:
        cans[i].SaveAs("/tmp/" + cans[i].GetName() + ".png")


if __name__ == '__main__':
    parser = get_default_parser(__doc__)
    parser.add_argument("input_filename", default="/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root")
    args = parser.parse_args()
    main(args.input_filename)
