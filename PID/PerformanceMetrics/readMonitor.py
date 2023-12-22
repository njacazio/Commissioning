#!/usr/bin/env python3

from ROOT import TFile, TCanvas, TH2F


def main(fn=["/tmp/timeMonitoring.root",
             "/tmp/timeMonitoringPrep.root",
             "/tmp/timeMonitoringTrk.root",
             "/tmp/timeMonitoringEvTime.root"]):
    g = []
    for i in fn:
        f = TFile(i)
        g.append(f.Get(f.GetListOfKeys().At(0).GetName()))
        f.Close()
    c = []
    h = {}
    for i in enumerate(g):
        c.append(TCanvas(f"{i[0]}"))
        x = list(i[1].GetX())
        x.sort()
        y = list(i[1].GetY())
        y.sort()

        h[i[0]] = TH2F(f"h{i[0]}", f"{fn[i[0]]}", 100, 0, x[-1], 20, 0, 20)
        # h[i[0]] = TH2F(f"h{i[0]}", f"{fn[i[0]]}", 100, 0, x[-1], 100, 0, y[-1])
        h[i[0]].GetXaxis().SetTitle(i[1].GetXaxis().GetTitle())
        h[i[0]].GetYaxis().SetTitle(i[1].GetYaxis().GetTitle())
        for j in range(i[1].GetN()):
            h[i[0]].Fill(i[1].GetPointX(j), i[1].GetPointY(j))
        if 0:
            i[1].Draw("AP")
        else:
            h[i[0]].Draw("COLZ")
        times = i[1].GetY()
        average = sum(times) / len(times)
        print(f"Average time for {fn[i[0]]} is {average} museconds")
        c[-1].Modified()
        c[-1].Update()
    input("Press enter to continue...")


main()
