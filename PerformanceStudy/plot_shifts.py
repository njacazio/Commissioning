#!/usr/bin/env python3


from ROOT import TFile, TF1, TObjArray, TColor, gROOT, TGraphErrors
import argparse
import sys
import os
sys.path.append(os.path.abspath("../QC/analysis/AO2D/"))
if 1:
    from plotting import draw_nice_canvas, update_all_canvases, set_nice_frame, draw_nice_legend, draw_nice_frame, draw_label, draw_diagonal

if 1:
    gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")


def main():
    fin = TFile("/tmp/523308.root", "READ")
    fin.ls()
    obj = fin.Get("ccdb_object")
    # obj.print()
    pars = obj.getPars("unanchored")
    mEtaN = 0
    mEtaStart = 0
    mEtaStop = 0

    mContent = {}
    for i in pars:
        # print(*i)
        if i[0] == "Shift.etaN":
            mEtaN = i[1]
        if i[0] == "Shift.etaStop":
            mEtaStop = i[1]
        if i[0] == "Shift.etaStart":
            mEtaStart = i[1]
        if "Shift.etaC" in i[0]:
            mContent[i[0]] = i[1]
    mInvEtaWidth = 1.0 / ((mEtaStop - mEtaStart) / mEtaN)

    def getEta(etaIndex):
        return mEtaStart + (etaIndex+0.5) / mInvEtaWidth

    def getShift(eta):
        if (mEtaN == 0):
            return 0.0
        if (eta <= mEtaStart):
            etaIndex = 0
        elif (eta >= mEtaStop):
            etaIndex = (mEtaN - 1)
        else:
            etaIndex = (eta - mEtaStart) * mInvEtaWidth
        etaIndex = int(etaIndex)
        print("Eta", eta, "EtaIndex", etaIndex, "shift", mContent[f"Shift.etaC{etaIndex}"])
        return mContent[f"Shift.etaC{etaIndex}"]

    gr = TGraphErrors()
    set_nice_frame(gr)
    gr.SetMarkerStyle(20)
    gr.SetTitle(";#eta;Shift")
    print("mEtaN", mEtaN, "mEtaStart", mEtaStart, "mEtaStop", mEtaStop, "mInvEtaWidth", mInvEtaWidth)
    for i in range(int(mEtaN)):
        eta = getEta(i)
        gr.SetPoint(gr.GetN(), eta, getShift(eta))
        gr.SetPointError(gr.GetN()-1, 1./mInvEtaWidth, 0)

    draw_nice_canvas("Shift")
    gr.Draw("ALP")
    update_all_canvases()
    input("Press Enter to continue...")


main()
