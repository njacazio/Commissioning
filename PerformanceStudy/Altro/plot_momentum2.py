#!/usr/bin/env python3


from ROOT import gROOT, gSystem
import argparse
if 1:
    gROOT.LoadMacro("../plot_momentum.C")
    from ROOT import plot_momentum


def main(file_list):
    for i in file_list:
        print("Processing file", i)
        plot_momentum(i)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="User of plot_momentum")
    parser.add_argument("input_files", nargs="+")
    args = parser.parse_args()
    main(args.input_files)
    gSystem.ProcessEvents()
    input("Press enter to continue")


def plot_momentum2(fileName="AO2D-64987.root"):
    ROOT.gStyle.SetOptFit(1111)
    ROOT.gStyle.SetMarkerStyle(20)
    ROOT.gStyle.SetMarkerSize(0.5)
    ROOT.gStyle.SetMarkerColor(ROOT.kAzure)
    ROOT.gStyle.SetLineColor(ROOT.kAzure)

    chain = ROOT.TChain()

    f = ROOT.TFile(fileName, "READ")
    lk = f.GetListOfKeys()

    for i in range(lk.GetEntries()):
        dfname = lk.At(i).GetName()
        if not dfname.Contains("DF_"):
            continue
        tname = "{}?#{}{}".format(
            fileName.Data(), dfname.Data(), "/O2deltatof")
        print(tname)
        chain.Add(tname)
    f.Close()

    print(chain.GetEntries())
    chain.ls()
    c1 = ROOT.TCanvas("c1", "c1")
    c1.cd()
    hsqrt = ROOT.TH2F("hsqrt", "hsqrt", 40, -10, 10, 100, -1000, 1000)
    chain.Draw("fDoubleDelta:fPt>>hsqrt", "", "Colz")

    hRef = ROOT.TH1F("hRef", "hRef", 100, -2000, 2000)
    minP = "fP>0.6"
    maxP = "fP<0.7"
    minTOFChi2 = "fTOFChi2<5"
    maxTOFChi2 = "fTOFChi2>=0"

    chain.Draw("fDoubleDelta>>hRef",
               minP and maxP and minTOFChi2 and maxTOFChi2, "Colz")
    fRefg = ROOT.TF1("fRefg", "gaus")
    fRefg.SetRange(-2000, 2000)
    hRef.Fit(fRefg, "R")

    RefSigma = fRefg.GetParameter(2) / ROOT.TMath.Sqrt(2)
    RefSigmaErr = fRefg.GetParError(2) / ROOT.TMath.Sqrt(2)

    print("Sigma Reference= ({}+-{})".format(RefSigma, RefSigmaErr))

    PtRangeMin = 0.3
    PtRangeMax = 1.3
    DeltaPtRange = 0.1
    nPtRanges = int((PtRangeMax - PtRangeMin) / DeltaPtRange)

    # Open output file
    foutV = ROOT.TFile("out_Visual.root", "RECREATE")

    # Get number of entries and define variables
    chain = ROOT.TChain("tree")
    chain.Add("input_file.root")
    nentries = chain.GetEntries()
    minPt = ROOT.TCut()
    maxPt = ROOT.TCut()
    RefSigma = 0.0
    RefSigmaDelta = [0.0] * nPtRanges
    RefSigmaErrDelta = [0.0] * nPtRanges
    MeanSigmaDelta = [0.0] * nPtRanges
    MeanSigmaErrDelta = [0.0] * nPtRanges
    PtMiddle = [0.0] * nPtRanges
    Pt = ROOT.TLeaf()
    TOFChi2 = ROOT.TLeaf()
    DoubleDelta = ROOT.TLeaf()

    # Get leaf objects
    Pt = chain.GetLeaf("fPt")
    TOFChi2 = chain.GetLeaf("fTOFChi2")
    DoubleDelta = chain.GetLeaf("fDoubleDelta")

    # Create canvas and histograms
    c2 = ROOT.TCanvas("c2", "c2")
    hDelta = []
    fDelta = []

    for i in range(nPtRanges+1):
        iPt = PtRangeMin + i * DeltaPtRange
        PtMiddle.append(iPt + 1 / 2 * DeltaPtRange)
        hDelta.append(ROOT.TH1F(f"hDelta_{iPt:.1f}_{iPt+DeltaPtRange:.1f}",
                                f"hDelta ({iPt:.1f}, {iPt+DeltaPtRange:.1f})", 100, -2000, 2000))
        fDelta.append(
            ROOT.TF1(f"fDelta_{iPt:.1f}_{iPt+DeltaPtRange:.1f}", "gaus", -2000, 2000))
        for k in range(nentries):
            chain.GetEntry(k)
            if Pt.GetValue() > iPt and Pt.GetValue() < (iPt + DeltaPtRange) and TOFChi2.GetValue() < 5 and TOFChi2.GetValue() >= 0:
                hDelta[i].Fill(DoubleDelta.GetValue())
        hDelta[i].Fit(fDelta[i], "R,WW")
        hDelta[i].Write()
        RefSigmaDelta.append(ROOT.TMath.Sqrt(fDelta[i].GetParameter(
            2) * fDelta[i].GetParameter(2) - RefSigma * RefSigma))
        RefSigmaErrDelta.append(fDelta[i].GetParError(
            2) * fDelta[i].GetParameter(2) / RefSigmaDelta[i])
        MeanSigmaDelta.append(fDelta[i].GetParameter(1))
        MeanSigmaErrDelta.append(fDelta[i].GetParError(2))
        print(
            f"\nPt interval= ({iPt:.1f},{iPt+DeltaPtRange:.1f}) --> Sigma= ({RefSigmaDelta[i]:.3f}+-{RefSigmaErrDelta[i]:.3f})")

    foutV.Close()
    # Output plots
    nPtRanges = 10
    PtMiddle = array('d', [0.0]*nPtRanges)
    MeanSigmaDelta = array('d', [0.0]*nPtRanges)
    RefSigmaDelta = array('d', [0.0]*nPtRanges)
    MeanSigmaErrDelta = array('d', [0.0]*nPtRanges)
    RefSigmaErrDelta = array('d', [0.0]*nPtRanges)

    # Create TGraphErrors for Mean vs Pt interval
    MeanPt = ROOT.TGraphErrors(nPtRanges, PtMiddle, MeanSigmaDelta, array(
        'd', [0.0]*nPtRanges), MeanSigmaErrDelta)
    MeanPt.SetTitle("Mean vs Pt interval")
    MeanPt.SetName("MeanPt")
    XaxisMeanPt = MeanPt.GetXaxis()
    YaxisMeanPt = MeanPt.GetYaxis()
    XaxisMeanPt.SetTitle("Pt")
    YaxisMeanPt.SetTitle("MeanDelta")

    # Create TGraphErrors for Sigma vs Pt interval
    SigmaPt = ROOT.TGraphErrors(nPtRanges, PtMiddle, RefSigmaDelta, array(
        'd', [0.0]*nPtRanges), RefSigmaErrDelta)
    SigmaPt.SetTitle("Sigma vs Pt interval")
    SigmaPt.SetName("SigmaPt")
    XaxisSigmaPt = SigmaPt.GetXaxis()
    YaxisSigmaPt = SigmaPt.GetYaxis()
    XaxisSigmaPt.SetTitle("Pt")
    YaxisSigmaPt.SetTitle("Sigma")

    # Create output file and write TGraphErrors to it
    out_Plots = ROOT.TFile("out_Plots.root", "RECREATE")
    MeanPt.Write()
    SigmaPt.Write()
    out_Plots.Close()
