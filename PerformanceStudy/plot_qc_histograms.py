#!/usr/bin/env python3


from ROOT import TFile, TF1, TObjArray, TColor, gROOT
import argparse
import sys
import os
sys.path.append(os.path.abspath("../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal

if 1:
    gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Input file name", nargs="+")
    parser.add_argument("--tags", default=[], help="Tag", nargs="+")
    args = parser.parse_args()
    hn = ["tof-pid-qa/delta/pt/Pi", "tof-pid-qa/nsigma/pt/Pi",
          "tof-pid-qa/delta/pt/Pr", "tof-pid-qa/nsigma/pt/Pr",
          "tof-pid-beta-qa/tofmass/inclusive"]
    histograms = {}
    for i in hn:
        histograms[i] = None
    for i in args.filename:
        f = TFile(i)
        f.ls()
        for j in histograms:
            f.Get(j).ls()
            if histograms[j] is None:
                histograms[j] = f.Get(j)
                histograms[j].SetDirectory(0)
            else:
                histograms[j].Add(f.Get(j))
    hkeys = list(histograms.keys())
    for i in hkeys:
        h = histograms[i]
        if "TH3" in histograms[i].ClassName():
            limits = {"Pos": 1, "Neg": 2}
            labels = {"Pos": "Positive", "Neg": "Negative"}
            for k in limits:
                h.GetZaxis().SetRange(limits[k], limits[k])
                hp = h.Project3D("yx")
                hp.SetName(i+k)
                set_nice_frame(hp, True)
                histograms[i+k] = hp
                draw_nice_canvas(i+k, gridy=True, gridx=True)
                hp.Draw("COL")
                fitres = TObjArray()
                if "nsigma" in i:
                    hp.FitSlicesY(TF1("fgaus", "gaus", -2, 2), -1, -1, 0, "QNRG4", fitres)
                elif "tofmass" in i:
                    hp.GetYaxis().SetRangeUser(0, 1.2)
                    hp.FitSlicesY(TF1("fgaus", "gaus", 0.9, 1.1), -1, -1, 0, "QNRG4", fitres)
                else:
                    hp.FitSlicesY(TF1("fgaus", "gaus", -300, 300), -1, -1, 0, "QNRG4", fitres)
                if len(args.tags) > 0:
                    draw_label(labels[k] + " tracks " + " ".join(args.tags))
                else:
                    draw_label(labels[k] + " tracks")
                fitres[1].Draw("same")
                fitres[1].SetLineColor(TColor.GetColor("#e41a1c"))
                if "tofmass" not in i:
                    fitres[2].Draw("same")
                fitres[2].SetLineColor(TColor.GetColor("#4daf4a"))
                fitres[2].SetLineColor(TColor.GetColor("#377eb8"))
                for ff in fitres:
                    ff.SetLineWidth(2)
                    ff.SetMarkerColor(ff.GetLineColor())
                leg = draw_nice_legend([0.83, 0.92], [0.83, 0.92], columns=2)
                leg.AddEntry(fitres[1], "#mu", "l")
                if "tofmass" not in i:
                    leg.AddEntry(fitres[2], "#sigma", "l")
            h.GetZaxis().SetRange()
        else:
            draw_nice_canvas(i)
            h.Draw()
    update_all_canvases()
    input("Press enter to exit...")


if __name__ == "__main__":
    main()
