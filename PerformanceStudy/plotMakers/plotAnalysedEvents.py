#!/usr/bin/env python3

"""
Plot the number of processed events
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
from ROOT import TH1, TH1F
from plotDeltaTSlices import get_from_file
import sys
import os
sys.path.append(os.path.abspath("../../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal


def main(fname="~/cernbox/Share/Sofia/LHC22m_pass3/AnalysisResults_TOFCALIB.root",
         labels=["LHC22m apass3", "run 523308"]):
    def draw_labels():
        for i, j in enumerate(labels):
            draw_label(j, 0.9, 0.88-0.05*i, align=31)
    hColCounterAll = get_from_file(fname, "event-selection-task/hColCounterAll")
    hColCounterAcc = get_from_file(fname, "event-selection-task/hColCounterAcc")
    
    h = get_from_file(fname, "tof-offline-calib/events")
    hevents = TH1F("hevents", "hevents", 2+h.FindLastBinAbove(0)+1, 0, 2+h.FindLastBinAbove(0)+1)
    hevents.GetYaxis().SetTitle("Collisions")
    set_nice_frame(hevents)
    hevents.SetBit(TH1.kNoStats)
    hevents.SetBit(TH1.kNoTitle)
    hevents.GetXaxis().SetBinLabel(1, "Events read")
    hevents.GetXaxis().SetBinLabel(2, "Passed event selection")
    hevents.SetBinContent(1, hColCounterAll.GetEntries())
    hevents.SetBinContent(2, hColCounterAcc.GetEntries())
    for i in range(1, h.FindLastBinAbove(0)+1):
        hevents.GetXaxis().SetBinLabel(2+i, h.GetXaxis().GetBinLabel(i))
        hevents.SetBinContent(2+i, h.GetBinContent(i))
    print("Number of events", h.GetBinContent(h.FindLastBinAbove(0))/1e6, "M")

    draw_nice_canvas("events", logy=False)
    hevents.GetYaxis().SetRangeUser(0, h.GetMaximum()*1.4)
    hevents.Draw()
    hevents.Draw("sameTEXT")
    draw_labels()

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
        draw_labels()

    if 0:
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
        draw_labels()

    canvases = update_all_canvases()
    input("Press enter to continue")
    for i in ["png", "pdf"]:
        for j in canvases:
            canvases[j].SaveAs(f"/tmp/{j}."+i)


if __name__ == "__main__":
    parser = get_default_parser(__doc__)
    parser.add_argument("input", help="Input file name", nargs="?", default="~/cernbox/Share/Sofia/LHC22m_pass3/AnalysisResults_TOFCALIB.root")
    args = parser.parse_args()
    main(args.input)
