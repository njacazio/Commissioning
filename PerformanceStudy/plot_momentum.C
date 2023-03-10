
#include "TChain.h"
#include "TFile.h"
#include "TH1F.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TF1.h"
#include "TCut.h"
#include "TGraphErrors.h"
#include "TStyle.h"
#include "TLeaf.h"
#include "TMultiGraph.h"
#include "THnSparse.h"
#include "TMath.h"
#include "TList.h"
#include <iostream>
#include <fstream>

using namespace std;

void addDFToChain(TString fileName, TChain &chain)
{
  TFile f(fileName, "READ");
  auto *lk = f.GetListOfKeys();
  for (int i = 0; i < lk->GetEntries(); i++)
  {
    TString dfname = lk->At(i)->GetName();
    if (!dfname.Contains("DF_"))
      continue;
    TString tname = Form("%s?#%s/O2deltatof", fileName.Data(), dfname.Data());
    cout << tname << endl;
    chain.Add(tname);
    // break;
  }
}

TList *plot_momentum(TString fileName = "${HOME}/cernbox2/LHC22m_523308_apass3_relval_cpu2/0/AnalysisResults_trees_TOFCALIB.root")
{
  TList *listOfOutput = new TList();
  gStyle->SetOptFit(0111);
  gStyle->SetMarkerStyle(20);
  gStyle->SetMarkerSize(0.5);
  gStyle->SetMarkerColor(kAzure);
  gStyle->SetLineColor(kAzure);

  TChain chain;
  if (fileName.EndsWith(".root"))
  {
    addDFToChain(fileName, chain);
  }
  else if (fileName.EndsWith(".txt"))
  {
    std::ifstream infile(fileName.Data());
    std::string line;
    while (std::getline(infile, line))
    {
      addDFToChain(line, chain);
    }
  }

  // f.Close();
  chain.Print();

  //----------------------------------------------------------------------------------------
  // Analisi

  cout << chain.GetEntries() << endl;
  chain.ls();
  TCanvas *c1 = new TCanvas("c1", "c1");
  c1->cd();
  // chain.Draw("fP");
  TH2F *hsqrt = new TH2F("hsqrt", "hsqrt", 40, -10, 10, 100, -1000, 1000);
  chain.Draw("fDoubleDelta:fPt>>hsqrt", "", "Colz");

  //----------------------------------------------------------------------------------------
  // Fit DoubleDelta per la referenza in una regione cinematica

  TH1F *hRef = new TH1F("hRef", "hRef", 100, -2000, 2000);
  TCut minP = "fP>0.6";
  TCut maxP = "fP<0.7";
  TCut minTOFChi2 = "fTOFChi2<5";
  TCut maxTOFChi2 = "fTOFChi2>=0";

  chain.Draw("fDoubleDelta>>hRef", minP && maxP && minTOFChi2 && maxTOFChi2, "Colz");
  TAxis *XhRef = hRef->GetXaxis();
  XhRef->SetTitle("#Delta#Delta_{T} (ps)");
  TF1 *fRefg = new TF1("fRefg", "gaus");
  fRefg->SetRange(-2000, 2000);
  hRef->Fit(fRefg, "R");

  const float RefSigma = fRefg->GetParameter(2) / sqrt(2);
  const float RefSigmaErr = fRefg->GetParError(2) / sqrt(2);

  cout << "Sigma Reference= (" << RefSigma << "+-" << RefSigmaErr << ")" << endl;

  //----------------------------------------------------------------------------------------
  // Fit DoubleDelta per una diversa regione cinematica per un solo range di impulso
  /*
    //Fit DoubleDelta particella di referenza in una diversa regione cinematica per un solo intervallo di Pt
    TH1F *hDelta = new TH1F("hDelta", "hDelta", 100, -2000, 2000);
    TCut minPt = "fPt>1.1";
    TCut maxPt = "fPt<1.2";
    new TCanvas;
    chain.Draw("fDoubleDelta>>hDelta", minPt && maxPt && minTOFChi2 && maxTOFChi2, "Colz");
    TF1 *fDelta = new TF1("fDelta", "gaus");
    fDelta->SetRange(-2000, 2000);
    hDelta->Fit(fDelta, "R,WW");
    const float RefSigmaDelta= sqrt(fDelta->GetParameter(2)*fDelta->GetParameter(2)-RefSigma*RefSigma);
    const float RefSigmaErrDelta= fDelta->GetParError(2)*fDelta->GetParameter(2)/RefSigmaDelta;
    cout<< "Sigma= " <<RefSigmaDelta<<" +- "<<RefSigmaErrDelta<<endl;
  */

  //----------------------------------------------------------------------------------------
  // Fit DoubleDelta per una diversa regione cinematica

  ////// RANGE DI IMPULSO, ETA E PHI valori da modificare ///////
  const Float_t PtRangeMin = 0.3, PtRangeMax = 1.3, DeltaPtRange = 0.1;     // 0.3 | 1.3 | 0.2
  const Float_t EtaRangeMin = -0.8, EtaRangeMax = 0.8, DeltaEtaRange = 0.2; // -0.8 | 0.8 | 0.2
  const Float_t PhiRangeMin = 0, PhiRangeMax = TMath::Pi() * 2;
  const Float_t DeltaPhiRange = TMath::Pi() * 2 / 18; // 0 | 2pi | pi/9
  ///////////////////////////////////////////////////////////////

  const Int_t nPtRanges = (PtRangeMax - PtRangeMin) / DeltaPtRange;
  const Int_t nEtaRanges = (EtaRangeMax - EtaRangeMin) / DeltaEtaRange;
  const Int_t nPhiRanges = (PhiRangeMax - PhiRangeMin) / DeltaPhiRange;

  // Attempt at Draw a THn
  //   Int_t bins[4] = {nPtRanges, nEtaRanges, nPhiRanges, 100};
  //   Double_t xmin[4] = {PtRangeMin, EtaRangeMin, PhiRangeMin, -2000.f};
  //   Double_t xmax[4] = {PtRangeMax, EtaRangeMax, PhiRangeMax, 2000.f};
  //   THnSparseF hs("hs", "hs", 4, bins, xmin, xmax);
  //   new TCanvas();
  //   chain.Draw("fPt:fEta:fPhi:fDoubleDelta>>hs", minP && maxP && minTOFChi2 && maxTOFChi2, "Colz");
  //   Printf("%f", hs.GetEntries());
  //   return;

  Float_t Pt;
  chain.SetBranchAddress("fPt", &Pt);
  Float_t Eta;
  chain.SetBranchAddress("fEta", &Eta);
  Float_t Phi;
  chain.SetBranchAddress("fPhi", &Phi);
  Float_t TOFChi2;
  chain.SetBranchAddress("fTOFChi2", &TOFChi2);
  Float_t DoubleDelta;
  chain.SetBranchAddress("fDoubleDelta", &DoubleDelta);

  Float_t iPt, jEta, kPhi;

  //---------------------------------------------------------
  // Definisco tutti gli istogrammi

  TCanvas *c2 = new TCanvas("c2", "c2");
  TH1F *hDelta0[nPtRanges];
  TAxis *XhDelta0[nPtRanges];
  TF1 *fDelta0[nPtRanges];
  TH1F *hDelta[nPtRanges][nEtaRanges][nPhiRanges];
  TF1 *fDelta = new TF1("fDelta", "gaus", -2000, 2000);

  Float_t PtMiddle[nPtRanges];
  Float_t PhiMiddle[nPhiRanges];

  for (Int_t i = 0; i < nPtRanges; i++)
  {
    iPt = PtRangeMin + i * DeltaPtRange;
    PtMiddle[i] = iPt + 1 / 2 * DeltaPtRange;
    hDelta0[i] = new TH1F(Form("hDelta_%.1f_%.1f", iPt, iPt + DeltaPtRange), Form("hDelta (%.1f , %.1f)", iPt, iPt + DeltaPtRange), 100, -2000, 2000);
    fDelta0[i] = new TF1(Form("fDelta_%.1f_%.1f", iPt, iPt + DeltaPtRange), "gaus", -2000, 2000);
    XhDelta0[i] = hDelta0[i]->GetXaxis();
    XhDelta0[i]->SetTitle("#Delta#Delta_{T} (ps)");
    for (Int_t j = 0; j < nEtaRanges; j++)
      for (Int_t k = 0; k < nPhiRanges; k++)
        hDelta[i][j][k] = new TH1F(Form("hDelta_%i_%i_%i", i, j, k), Form("hDelta_%i_%i_%i", i, j, k), 100, -2000, 2000);
  }

  //---------------------------------------------------------
  // Riempio tutti gli istogrammi

  TFile *foutV = new TFile("out_Visual.root", "RECREATE");
  const Int_t nentries = chain.GetEntries();
  for (Int_t ientry = 0; ientry < nentries; ientry++)
  {
    if (ientry % 10000 == 0)
    {
      Printf("%f%", float(ientry) / nentries * 100);
    }
    chain.GetEntry(ientry);
    for (Int_t i = 0; i < nPtRanges; i++)
    {
      iPt = PtRangeMin + i * DeltaPtRange;
      if (Pt > iPt && Pt < (iPt + DeltaPtRange) && TOFChi2 < 5 && TOFChi2 >= 0)
        hDelta0[i]->Fill(DoubleDelta);
      for (Int_t j = 0; j < nEtaRanges; j++)
      {
        jEta = EtaRangeMin + j * DeltaEtaRange;
        for (Int_t k = 0; k < nPhiRanges; k++)
        {
          kPhi = PhiRangeMin + k * DeltaPhiRange;
          PhiMiddle[k] = kPhi + 1 / 2 * DeltaPhiRange;
          // hDelta->Reset();
          if (Pt > iPt && Pt < (iPt + DeltaPtRange) && TOFChi2 < 5 && TOFChi2 >= 0 && Eta > jEta && Eta < (jEta + DeltaEtaRange) && Phi > kPhi && Phi < (kPhi + DeltaPhiRange))
            hDelta[i][j][k]->Fill(DoubleDelta);
        }
      }
    }
  }

  //---------------------------------------------------------
  // Estraggo tutti i parametri

  Float_t RefSigmaDelta[nPtRanges][nEtaRanges][nPhiRanges], RefSigmaErrDelta[nPtRanges][nEtaRanges][nPhiRanges];
  Float_t MeanSigmaDelta[nPtRanges][nEtaRanges][nPhiRanges], MeanSigmaErrDelta[nPtRanges][nEtaRanges][nPhiRanges];
  Float_t RefSigmaDelta0[nPtRanges], RefSigmaErrDelta0[nPtRanges], MeanSigmaDelta0[nPtRanges], MeanSigmaErrDelta0[nPtRanges]; // in tutti gli angoli

  for (Int_t i = 0; i < nPtRanges; i++)
  {
    hDelta0[i]->Fit(fDelta0[i], "R,WW");
    hDelta0[i]->Write();
    RefSigmaDelta0[i] = sqrt(fDelta0[i]->GetParameter(2) * fDelta0[i]->GetParameter(2) - RefSigma * RefSigma);
    RefSigmaErrDelta0[i] = fDelta0[i]->GetParError(2) * fDelta0[i]->GetParameter(2) / RefSigmaDelta0[i];
    MeanSigmaDelta0[i] = fDelta0[i]->GetParameter(1);
    MeanSigmaErrDelta0[i] = fDelta0[i]->GetParError(1);
    for (Int_t j = 0; j < nEtaRanges; j++)
      for (Int_t k = 0; k < nPhiRanges; k++)
      {
        hDelta[i][j][k]->Fit(fDelta, "R,WW");
        RefSigmaDelta[i][j][k] = sqrt(fDelta->GetParameter(2) * fDelta->GetParameter(2) - RefSigma * RefSigma);
        RefSigmaErrDelta[i][j][k] = fDelta->GetParError(2) * fDelta->GetParameter(2) / RefSigmaDelta[i][j][k];
        MeanSigmaDelta[i][j][k] = fDelta->GetParameter(1);
        MeanSigmaErrDelta[i][j][k] = fDelta->GetParError(1);
      }
  }

  foutV->Close();

  /*    for (Int_t i = 0; i < nPtRanges; i++)
      for (Int_t j = 0; j < nEtaRanges; j++)
        for (Int_t k = 0; k < nPhiRanges; k++)
        {
          delete hDelta[i][j][k];
          hDelta[i][j][k] = nullptr;
        }  */

  //---------------------------------------------------------
  // Stampa delle risoluzioni

  for (Int_t i = 0; i < nPtRanges; i++)
    cout << "\nPt= (" << PtRangeMin + i * DeltaPtRange << " , " << PtRangeMin + (i + 1) * DeltaPtRange << ") --> Sigma= (" << RefSigmaDelta0[i] << " +- " << RefSigmaErrDelta0[i] << ")" << endl;
  cout << endl;

  ///////// DA CANCELLARE - Stampa di tutti i valori
  /*
  for (Int_t i = 0; i < nPtRanges; i++)
      for (Int_t j = 0; j < nEtaRanges; j++)
        for (Int_t k = 0; k < nPhiRanges; k++)
          cout << i << j << k << " " << RefSigmaDelta[i][j][k] << " " << RefSigmaErrDelta[i][j][k] << " " << MeanSigmaDelta[i][j][k] << " " << MeanSigmaErrDelta[i][j][k] << endl;
   */

  //----------------------------------------------------------------------------------------
  // Output plots

  TFile *out_Plots = new TFile("out_Plots.root", "RECREATE");

  // MeanPt
  TGraphErrors *MeanPt = new TGraphErrors(nPtRanges, PtMiddle, MeanSigmaDelta0, 0, MeanSigmaErrDelta0);
  MeanPt->SetTitle("Mean vs p_{T} interval");
  MeanPt->SetName("MeanPt");
  TAxis *XaxisMeanPt = MeanPt->GetXaxis();
  TAxis *YaxisMeanPt = MeanPt->GetYaxis();
  XaxisMeanPt->SetTitle("P_{T} (GeV/c)");
  YaxisMeanPt->SetTitle("Mean #Delta#Deltat (ps)");
  MeanPt->Write();

  // SigmaPt
  TGraphErrors *SigmaPt = new TGraphErrors(nPtRanges, PtMiddle, RefSigmaDelta0, 0, RefSigmaErrDelta0);
  SigmaPt->SetTitle("#sigma_{TOF} vs p_{T} interval");
  SigmaPt->SetName("SigmaPt");
  TAxis *XaxisSigmaPt = SigmaPt->GetXaxis();
  TAxis *YaxisSigmaPt = SigmaPt->GetYaxis();
  XaxisSigmaPt->SetTitle("P_{T} (GeV/c)");
  YaxisSigmaPt->SetTitle("#sigma_{TOF} (ps)");
  SigmaPt->Write();

  // EtaPhi
  TMultiGraph *EtaPhiPt[nPtRanges];
  TAxis *XaxisEtaPhiPt[nPtRanges];
  TAxis *YaxisEtaPhiPt[nPtRanges];

  TGraphErrors *graphEtaPt[nEtaRanges];
  for (Int_t i = 0; i < nPtRanges; i++)
  {
    EtaPhiPt[i] = new TMultiGraph();
    iPt = PtRangeMin + i * DeltaPtRange;
    EtaPhiPt[i]->SetTitle(Form("Shift for p_{T} (%.1f , %.1f)", iPt, iPt + DeltaPtRange));
    XaxisEtaPhiPt[i] = EtaPhiPt[i]->GetXaxis();
    YaxisEtaPhiPt[i] = EtaPhiPt[i]->GetYaxis();
    EtaPhiPt[i]->SetName(Form("EtaPhiPt%i", i));
    XaxisEtaPhiPt[i]->SetTitle("#Phi (rad)");
    YaxisEtaPhiPt[i]->SetTitle("Shift (ps)");

    for (Int_t j = 0; j < nEtaRanges; j++)
    {
      jEta = EtaRangeMin + j * DeltaEtaRange;
      if (i != 0)
      {
        delete graphEtaPt[j];
        graphEtaPt[j] = nullptr;
      }
      graphEtaPt[j] = new TGraphErrors(nPhiRanges, PhiMiddle, RefSigmaDelta[i][j], 0, RefSigmaErrDelta[i][j]);
      graphEtaPt[j]->SetName(Form("Eta (%.1f , %.1f)", jEta, jEta + DeltaEtaRange));
      EtaPhiPt[i]->Add(graphEtaPt[j]);
    }
    EtaPhiPt[i]->Write();
  }

  out_Plots->Close();
  return listOfOutput;
}
