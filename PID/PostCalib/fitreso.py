#!/usr/bin/env python3

"""
Script to plot the NSigma, extract resolution and parameters
"""


from debugtrack import DebugTrack
from ROOT import o2, TFile, TF1, TPaveText, TH1
from plotting import draw_nice_canvas, update_all_canvases, draw_nice_legend, draw_pave
from common import get_default_parser, set_verbose_mode, warning_msg


def main(fname,
         paramn="/tmp/tofreso.root",
         particle="Pi",
         rebinx=-2,
         mc=True):
    f = TFile(fname, "READ")
    if not f.IsOpen():
        print("Cannot open", fname)

    dnbase = "tof-pid-qa/event"
    if mc:
        dnbase = f"pidTOF-qa-mc-{particle}"
    if not f.Get(dnbase):
        f.ls()
        raise ValueError("Cannot find directory", dnbase)
    print("Using base directory", dnbase)
    f.Get(dnbase).ls()
    histos = {}

    def get(hn, t, draw=True):
        histos[t] = f.Get(hn)
        if not histos[t]:
            warning_msg("Did not find", t)
            return
        histos[t].SetDirectory(0)
        histos[t].SetName(t)
        histos[t].SetBit(TH1.kNoStats)
        if "TH3" in histos[t].ClassName():
            if draw:
                draw_nice_canvas(f"3d{t}", logz=False)
                histos[t].DrawCopy("COLZ")
            histos[t] = histos[t].Project3D("yx")

        if not draw:
            return
        if rebinx > 0:
            histos[t].RebinX(rebinx)
        if 1:
            draw_nice_canvas(f"2d{t}", logz=True)
            histos[t].DrawCopy("COLZ")

    get(f"{dnbase}/expected_diff/{particle}", "delta")
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

    def drawslice(hn, x=[0.9, 1.1], fit=True):
        if not histos[hn]:
            return
        draw_nice_canvas(f"hp{hn}")
        bins = [histos[hn].GetXaxis().FindBin(x[0]),
                histos[hn].GetXaxis().FindBin(x[1])]
        hp = histos[hn].ProjectionY(f"{hn}-{bins[0]}-{bins[1]}",
                                    *bins)
        hp.SetDirectory(0)
        if fit:
            hp.Fit(fgaus)
        hp.Draw()
        if fit:
            draw_pave(["#mu = {:.3f}".format(fgaus.GetParameter(1)),
                       "#sigma = {:.3f}".format(fgaus.GetParameter(2))])
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
        s = histos["delta"].ProjectionY(f"{i}", i, i)
        s.SetDirectory(0)
        s.Fit(fgaus, "QNR")
        hparmu.SetBinContent(i, fgaus.GetParameter(1))
        hparsigma.SetBinContent(i, fgaus.GetParameter(2))

    draw_nice_canvas("hp")
    bins = [histos["delta"].GetXaxis().FindBin(
        0.9), histos["delta"].GetXaxis().FindBin(1.1)]
    slice1gev = histos["delta"].ProjectionY(f"{bins[0]}-{bins[1]}", *bins)
    slice1gev.SetDirectory(0)
    slice1gev.Fit(fgaus)
    slice1gev.Draw()
    pave = TPaveText(.68, .63, .91, .72, "brNDC")
    pave.AddText("#mu = {:.3f}".format(fgaus.GetParameter(1)))
    pave.AddText("#sigma = {:.3f}".format(fgaus.GetParameter(2)))
    pave.Draw()

    draw_nice_canvas("fit")
    histos["delta"].Draw("COLZ")
    hparmu.Draw("same")
    hparsigma.Draw("same")
    if paramn is not None:
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
