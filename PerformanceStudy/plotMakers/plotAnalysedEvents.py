#!/usr/bin/env python3

"""
Plot the number of processed events
"""


from ROOT import TH1
from plotDeltaTSlices import get_from_file
import sys
import os
sys.path.append(os.path.abspath("../../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal


def main(fname="~/cernbox/Share/Sofia/LHC22m_pass3/AnalysisResults_TOFCALIB.root"):
    h = get_from_file(fname, "tof-offline-calib/events")
    h.SetBit(TH1.kNoStats)
    h.GetXaxis().SetRange(1, h.FindLastBinAbove(0)+1)
    print("Number of events", h.GetBinContent(h.FindLastBinAbove(0))/1e6, "M")
    h.GetYaxis().SetRangeUser(0, h.GetMaximum()*1.3)
    h.SetBit(TH1.kNoTitle)
    set_nice_frame(h)
    draw_nice_canvas("events", logy=False)
    h.Draw()
    h.Draw("sameTEXT")
    draw_label("LHC22m apass3", 0.9, 0.88, align=31)
    draw_label("run 523308", 0.9, 0.83, align=31)

    if 0:
        h = get_from_file(fname, "tof-pid-beta-qa/event/evsel")
        h.SetBit(TH1.kNoStats)
        h.GetXaxis().SetRange(1, h.FindLastBinAbove(0)+1)
        h.GetYaxis().SetRangeUser(0, h.GetMaximum()*1.3)
        h.SetBit(TH1.kNoTitle)
        set_nice_frame(h)
        draw_nice_canvas("evsel", logy=False)
        h.Draw()
        h.Draw("sameTEXT")
        draw_label("LHC22m apass3", 0.9, 0.88, align=31)
        draw_label("run 523308", 0.9, 0.83, align=31)

    if 1:
        h = get_from_file(fname, "tof-pid-qa/event/vertexz")
        h.SetBit(TH1.kNoStats)
        h.GetXaxis().SetTitle("Collision position along z (cm)")
        h.GetYaxis().SetTitle("Counts")
        h.GetXaxis().SetRangeUser(-12, 12)
        h.GetYaxis().SetRangeUser(0, h.GetMaximum()*1.3)
        h.SetBit(TH1.kNoTitle)
        set_nice_frame(h)
        draw_nice_canvas("vertexz", logy=False)
        h.Draw()
        draw_label("LHC22m apass3", 0.9, 0.88, align=31)
        draw_label("run 523308", 0.9, 0.83, align=31)

    canvases = update_all_canvases()
    input("Press enter to continue")
    for i in ["png", "pdf"]:
        for j in canvases:
            canvases[j].SaveAs(f"/tmp/{j}."+i)


if __name__ == "__main__":
    main()
