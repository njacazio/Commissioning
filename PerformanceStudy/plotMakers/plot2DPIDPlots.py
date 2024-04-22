#!/usr/bin/env python3

"""
The usual 2D separation plots vs pT
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
from ROOT import TFile, TH1, TF1
import sys
import os
sys.path.append(os.path.abspath("../../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal, definenicepalette


def do_plot(histogram, do_draw=False, plot_particles=True):
    if do_draw:
        histogram.Draw("COL")
    if not plot_particles:
        return
    particle = None
    for i in ["Pi", "Ka", "Pr"]:
        if i in histogram.GetName():
            particle = i
            break
    if particle == "Pi":
        draw_label("#pi", 0.24, 0.58, size=0.04)
        draw_label("K", 0.33, 0.74, size=0.04)
        draw_label("p", 0.45, 0.83, size=0.04)
    elif particle == "Ka":
        draw_label("#pi", 0.4, 0.43, size=0.04)
        draw_label("K", 0.24, 0.6, size=0.04)
        draw_label("p", 0.41, 0.81, size=0.04)


def main(input_filename="/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root",
         particle="Ka",
         evtime="T0AC",
         out_path="/home/njacazio/Overleaf/TOFPerformanceRun3/Common/img/"):
    definenicepalette()
    h = get_from_file(input_filename, f"Delta{particle}{evtime}_vs_fPt")
    can = draw_nice_canvas(h.GetName())
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
