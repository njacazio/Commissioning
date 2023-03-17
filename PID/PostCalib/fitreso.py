#!/usr/bin/env python3

"""
Script to plot the NSigma, extract resolution and parameters
"""

import os
from debugtrack import DebugTrack
from ROOT import o2, TFile, TF1, TPaveText, TH1
from plotting import draw_nice_canvas, update_all_canvases, draw_nice_legend, draw_pave, draw_label
from common import get_default_parser, set_verbose_mode, warning_msg


def main(fname,
         paramn="/tmp/tofreso.root",
         particle="Pi",
         rebinx=-2,
         mc=True):
    f = TFile(fname, "READ")
    if not f.IsOpen():
        print("Cannot open", fname)

    dnbase = "tof-pid-qa"
    if mc:
        dnbase = f"pidTOF-qa-mc-{particle}"
    if not f.Get(dnbase):
        f.ls()
        raise ValueError("Cannot find directory", dnbase)
    print("Using base directory", dnbase)
    f.Get(dnbase).ls()
    histos = {}

    def get(histoname, histotype, draw=True, alternative=None):
        histos[histotype] = f.Get(histoname)
        if not histos[histotype]:
            if alternative is not None:
                warning_msg("Did not find", histotype, "named", histoname, "trying", alternative)
                return get(alternative, histotype, draw, None)
            warning_msg("Did not find", histotype, "named", histoname)
            return
        histos[histotype].SetDirectory(0)
        histos[histotype].SetName(histotype)
        histos[histotype].SetBit(TH1.kNoStats)
        histos[histotype].SetBit(TH1.kNoTitle)
        if "TH3" in histos[histotype].ClassName():
            if draw:
                draw_nice_canvas(f"3d{histotype}", logz=False)
                histos[histotype].DrawCopy("COLZ")
            histos[histotype] = histos[histotype].Project3D("yx")

        if not draw:
            return
        if rebinx > 0:
            histos[histotype].RebinX(rebinx)
        if 1:
            draw_nice_canvas(f"2d{histotype}", logz=True)
            histos[histotype].DrawCopy("COLZ")
            draw_label(histos[histotype].GetTitle(), x=0.95, y=0.96, align=31)

    get(f"{dnbase}/expected_diff/{particle}", "delta", alternative=f"{dnbase}/delta/{particle}")
    get(f"{dnbase}/nsigma/{particle}", "nsigma")
    if mc:
        for i in ["El", "Mu", "Pi", "Ka", "Pr", "De", "Tr", "He", "Al"]:
            get(f"{dnbase}/nsigmaMC/{i}", f"nsigmaMC{i}", draw=False)
    f.Close()

    purity = None
    efficiency = None
    if mc:
        def docut(hn, y=[-3, 3]):
            if not histos[hn]:
                warning_msg("Can't find", hn)
                return
            bins = [histos[hn].GetYaxis().FindBin(y[0]),
                    histos[hn].GetYaxis().FindBin(y[1])]
            hp = histos[hn].ProjectionX(f"{hn}-cut-[{y[0]}, {y[1]}]{bins[0]}-{bins[1]}",
                                        *bins)
            print(hp.GetName())
            hp.SetDirectory(0)
            return hp
        draw_nice_canvas(f"Purity{particle}")
        purity = docut(f"nsigma")
        purity.SetName(f"purity{particle}")
        purity.SetTitle("Purity")
        purity.Divide(docut(f"nsigmaMC{particle}"))
        purity.Draw()

        draw_nice_canvas(f"Efficiency{particle}")
        efficiency = docut(f"nsigmaMC{particle}", [-1000, 1000])
        efficiency.SetName(f"efficiency{particle}")
        efficiency.SetTitle("Efficiency")
        efficiency.Divide(docut(f"nsigmaMC{particle}"))
        efficiency.Draw()

    fgaus = TF1("gaus", "gaus", -200, 200)

    def drawslice(hn, x=[0.9, 1.1], fit=True, can_name=None):
        if not histos[hn]:
            return
        if can_name is None:
            draw_nice_canvas(f"hp{hn}")
        else:
            draw_nice_canvas(can_name)

        bins = [histos[hn].GetXaxis().FindBin(x[0]),
                histos[hn].GetXaxis().FindBin(x[1])]
        binsx = [histos[hn].GetXaxis().GetBinLowEdge(bins[0]),
                 histos[hn].GetXaxis().GetBinUpEdge(bins[1])]
        hp = histos[hn].ProjectionY(f"{hn}-{bins[0]}-{bins[1]}",
                                    *bins)
        hp.SetBit(TH1.kNoStats)
        hp.SetBit(TH1.kNoTitle)
        hp.SetDirectory(0)
        if fit:
            if hp.GetEntries() > 10:
                hp.Fit(fgaus)
        hp.Draw()
        draw_label("{} [{:.2f},{:.2f}] {}".format(hp.GetTitle(), *binsx, histos[hn].GetXaxis().GetTitle()),
                   0.95, 0.96, align=31)
        if fit:
            draw_pave(["#mu = {:.3f}".format(fgaus.GetParameter(1)),
                       "#sigma = {:.3f}".format(fgaus.GetParameter(2))])
        return hp
    drawslice("delta")
    drawslice("nsigma")

    if not histos["delta"]:
        update_all_canvases()
        return

    hparmu = histos["delta"].ProjectionX("mu")
    hparmu.Clear()
    hparmu.SetLineColor(2)
    hparmu.SetDirectory(0)

    hparsigma = histos["delta"].ProjectionX("sigma")
    hparsigma.Clear()
    hparsigma.SetLineColor(3)
    hparsigma.SetDirectory(0)

    debugtrack = DebugTrack()
    # debugtrack = o2.pid.tof.DebugTrack()
    tofpar = o2.pid.tof.TOFResoParams()
    # exptimes = o2.pid.tof.ExpTimes(o2.pid.tof.DebugTrack, 2)
    exptimes = o2.pid.tof.ExpTimes(DebugTrack, 2)
    print(exptimes.GetExpectedSigma(tofpar, debugtrack))

    def param(x, parameters):
        debugtrack.mp = x[0]
        tofpar.SetParameter(0, parameters[0])
        tofpar.SetParameter(1, parameters[1])
        tofpar.SetParameter(2, parameters[2])
        tofpar.SetParameter(3, parameters[3])
        tofpar.SetParameter(4, parameters[4])
        # tofpar.Print()
        collisionTimeRes = 20.0
        tofSignal = 1.
        return exptimes.GetExpectedSigma(tofpar, debugtrack, tofSignal, collisionTimeRes)

    for i in range(1, histos["delta"].GetNbinsX()+1):
        s = histos["delta"].ProjectionY(f"{histos['delta'].GetName()}{i}_for_fit_slices", i, i)
        s.SetDirectory(0)
        if s.GetEntries() < 10:
            continue
        s.Fit(fgaus, "QNR")
        hparmu.SetBinContent(i, fgaus.GetParameter(1))
        hparsigma.SetBinContent(i, fgaus.GetParameter(2))

    draw_nice_canvas("fit")
    histos["delta"].Draw("COLZ")
    hparmu.Draw("same")
    hparsigma.Draw("same")
    if paramn is not None:
        if not os.path.isfile(paramn):
            warning_msg("Can't find", paramn)
        else:
            tofpar.LoadParamFromFile(paramn, "TOFResoParams")

    fresoorig = TF1("paramorig", param, 0.1, 1.5, tofpar.size())
    for i in range(tofpar.size()):
        fresoorig.SetParameter(i, tofpar.GetParameter(i))
    fresoorig.SetLineColor(1)
    fresoorig.Draw("same")
    sorig = ""
    for i in range(0, fresoorig.GetNpar()):
        sorig += " --p{} {:.2f}".format(i, fresoorig.GetParameter(i))

    freso = TF1("param", param, 0.1, 1.5, tofpar.size())
    freso.SetParLimits(0, 0, 0.1)
    freso.SetParLimits(1, 0, 0.1)
    freso.SetParLimits(2, 0, 0.1)
    freso.SetParLimits(3, 0, 200)
    freso.SetParLimits(4, 0, 200)
    hparsigma.Fit(freso, "QNR", "", 0.2, 2)
    freso.Draw("same")
    leg = draw_nice_legend()
    leg.AddEntry(fresoorig, "Starting")
    leg.AddEntry(freso, "Refitted")
    s = ""
    for i in range(0, freso.GetNpar()):
        s += " --p{} {:.2f}".format(i, freso.GetParameter(i))
    print("Starting calib", sorig)
    print("Post calib", s)

    update_all_canvases()


if __name__ == "__main__":
    parser = get_default_parser(__doc__ +
                                "Basic example: `./fitreso.py paths/AnalysisResults.root`")
    parser.add_argument('files',
                        type=str,
                        nargs="+",
                        help='Input files')
    parser.add_argument('--mc', action='store_true', help='MC mode')
    args = parser.parse_args()
    set_verbose_mode(args)

    for i in args.files:
        main(i, mc=args.mc)
    input("press enter to continue")
