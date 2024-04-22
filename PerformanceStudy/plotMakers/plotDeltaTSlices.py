#!/usr/bin/env python3

"""
Script to plot the t-texp-tev histograms in slices of pT
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

import subprocess
from ROOT import TFile, TH1, TF1, TGraphErrors
import sys
import os
sys.path.append(os.path.abspath("../../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal


downloaded_files = {}


def get_from_file(filename,
                  objname=None,
                  verbose=True,
                  error_if_not_found=True,
                  rename=None,
                  xrange=None,
                  linecolor=None):
    def msg(m):
        if not verbose:
            return
        print(m)
    if ":" in filename:
        if filename in downloaded_files:
            return get_from_file(downloaded_files[filename], objname=objname)
        cmd = f"env -i rsync --progress -u {filename} /tmp/"
        msg(f"Running {cmd}")
        subprocess.run(cmd.split(), capture_output=False)
        downloaded_file = os.path.join("/tmp/", os.path.basename(filename.split(":")[-1]))
        downloaded_files[filename] = downloaded_file
        print(downloaded_file)
        return get_from_file(downloaded_file, objname=objname)
    f = TFile(filename, "READ")
    if not f or not f.IsOpen():
        print("Did not get", filename)
        return

    if objname is None:
        f.ls()
        return
    if type(objname) is list:  # multiple option mode
        for i in objname:
            o = get_from_file(filename, i, verbose=verbose, error_if_not_found=False)
            if o:
                return o
    o = f.Get(objname)
    if not o and error_if_not_found:
        f.ls()
        # if objname.
        raise ValueError(f"Got no object {objname} from file {filename}")
    elif not o:
        return None
    if "TDirectory" in o.ClassName():
        o.ls()
    if "TH" in o.ClassName() and "THashList" not in o.ClassName():
        o.SetDirectory(0)
        if xrange is not None:
            o.GetXaxis().SetRangeUser(*xrange)
    if rename is not None:
        o.SetName(rename)
        o.SetTitle(rename)
    if linecolor is not None:
        o.SetLineColor(linecolor)
    return o


def main(input_filename="/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root",
         particle="Pi",
         normalize=True,
         do_fit=True,
         more_labels=["ALICE Performance", 
                      "pp #sqrt{#it{s}} = 13.6 TeV"],
         range_delta=[-1000, 1000]):
    h = get_from_file(input_filename, f"Delta{particle}TOF_vs_fPt")
    h = get_from_file(input_filename, f"Delta{particle}T0AC_vs_fPt")
    h = get_from_file(input_filename, f"Delta{particle}T0AC_vs_fP")
    draw_nice_canvas(h.GetName())
    h.Draw("COL")
    if range_delta is not None:
        h.GetYaxis().SetRangeUser(*range_delta)

    slices = {0: [0.59, 0.61],
              1: [0.99, 1.01],
              1: [1.49, 1.51]}
    slices = {}
    print("Slices")
    for i in range(12):
        slices[i] = [0.4+(1.6-0.4)/12 * i, 0.4+(1.6-0.4)/12 * (i+1)]
        print(slices[i])

    hslices = []
    g = TGraphErrors()
    g.GetXaxis().SetTitle(h.GetXaxis().GetTitle())
    g.GetXaxis().SetTitleOffset(h.GetXaxis().GetTitleOffset())
    yt = h.GetYaxis().GetTitle().replace("(ps)", "").strip()
    g.GetYaxis().SetTitle(f"#sigma({yt}) (ps)")
    g.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset())
    g.SetMarkerStyle(20)

    for i in slices:
        pt_bins = [h.GetXaxis().FindBin(slices[i][0]+0.0001), 
                   h.GetXaxis().FindBin(slices[i][1]-0.0001)]
        pt_actual = [h.GetXaxis().GetBinLowEdge(pt_bins[0]), h.GetXaxis().GetBinUpEdge(pt_bins[1])]
        pt_slice = h.GetXaxis().GetTitle().split(" ")
        pt_slice[1] = pt_slice[1].strip().strip("(").strip(")")
        if pt_actual[1] - pt_actual[0] > 0.1:
            pt_slice = f"{pt_actual[0]:.2f} < {pt_slice[0]} < {pt_actual[1]:.2f} {pt_slice[1]}"
        else:
            pt_center = sum(pt_actual)/2
            pt_slice = f"{pt_slice[0]} = {pt_center:.2f} {pt_slice[1]}"
        draw_nice_canvas(f"slice_{i}")
        hslices.append(h.ProjectionY(f"{h.GetName()}_{i}", *pt_bins))
        hslices[-1].SetMarkerStyle(20)
        hslices[-1].SetBit(TH1.kNoStats)
        hslices[-1].SetBit(TH1.kNoTitle)
        set_nice_frame(hslices[-1])
        if normalize:
            hslices[-1].GetYaxis().SetTitle("Normalized counts")
            hslices[-1] = hslices[-1].DrawNormalized("E1")
        else:
            hslices[-1].GetYaxis().SetTitle("Counts")
            hslices[-1].Draw()
        ystartleft = 0.88
        ystartleft = 0.66
        ystartleft = 0.7
        draw_label(pt_slice, 0.2, ystartleft, align=11, size=0.04)
        if more_labels is not None:
            ystart = 0.88
            for i in more_labels:
                draw_label(i, 0.75, ystart, size=0.04)
                ystart -= 0.05
        if do_fit:
            fun = TF1(f"{hslices[-1].GetName()}_fit", "gaus", -400, 400)
            hslices[-1].Fit(fun, "QNWW", "", -200, 200)
            fun.Draw("SAME")
            ystartleft -= 0.08
            xleft = 0.22
            draw_label("Gaussian model", xleft, ystartleft, align=11)
            ystartleft -= 0.05
            draw_label(f"#mu = {fun.GetParameter(1):.2f} #pm {fun.GetParError(1):.2f} ps", xleft, ystartleft, align=11)
            ystartleft -= 0.05
            draw_label(f"#sigma = {fun.GetParameter(2):.2f} #pm {fun.GetParError(2):.2f} ps", xleft, ystartleft, align=11)
            g.SetPoint(g.GetN(), sum(pt_actual)/2, fun.GetParameter(2))
            g.SetPointError(g.GetN()-1, (pt_actual[1]-pt_actual[0])/2, fun.GetParError(2))

    draw_nice_canvas("sigma_vs_pt")
    g.Draw("AP")

    cans = update_all_canvases()
    input("Press enter to continue")
    for i in cans:
        cans[i].SaveAs("/tmp/" + cans[i].GetName() + ".pdf")


if __name__ == '__main__':
    parser = get_default_parser(__doc__)
    parser.add_argument("--input", default="/tmp/TOFRESOLHC22m_pass3_1.40_1.50.root")
    args = parser.parse_args()
    main(args.input)
