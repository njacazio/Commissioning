void makeplot(){
  TFile *f = new TFile("full.root");
  TTree *t = (TTree *) f->Get("tree");

  const char *variable = "p^{2}/m / (texp/12.5 ns) (GeV/#it{c})";

  float chi2T; t->SetBranchAddress("chi2",&chi2T);
  float pT; t->SetBranchAddress("p",&pT);
  float etaT; t->SetBranchAddress("eta",&etaT);
  float phiT; t->SetBranchAddress("phi",&phiT);
  float lT; t->SetBranchAddress("l",&lT);
  float mT; t->SetBranchAddress("m",&mT);
  float texpT; t->SetBranchAddress("texp",&texpT);
  float dtT; t->SetBranchAddress("dt",&dtT);
  int hastrd; t->SetBranchAddress("hastrd",&hastrd);

  TF1 *ff = new TF1("ff","gaus",-1000,1000);

  float sigmaRef = 100.3;

  int npbin = 100;
  float pmax = 25;
  
  const int neta = 10;
  float etaMin = -0.9;
  float etaMax = 0.9;
  float etaRangeInv = 1./(etaMax - etaMin);
  TH2F *hpi[neta];
  TH1D *hsigmaPi[neta];
  TH2F *hsigmaPi2D = new TH2F("hSigmaPi2D",Form("pions; %s; #eta",variable),npbin,0,pmax,neta,etaMin,etaMax);
  TH2F *hka[neta];
  TH1D *hsigmaKa[neta];
  TH2F *hsigmaKa2D = new TH2F("hSigmaKa2D",Form("kaons; %s; #eta",variable),npbin,0,pmax,neta,etaMin,etaMax);
  TH2F *hpr[neta];
  TH1D *hsigmaPr[neta];
  TH2F *hsigmaPr2D = new TH2F("hSigmaPr2D",Form("protons; %s; #eta",variable),npbin,0,pmax,neta,etaMin,etaMax);
  TH2F *hde[neta];
  TH1D *hsigmaDe[neta];
  TH2F *hsigmaDe2D = new TH2F("hSigmaDe2D",Form("deuterons; %s; #eta",variable),npbin,0,pmax,neta,etaMin,etaMax);
  for(int i=0; i < neta; i++){
    hpi[i] = new TH2F(Form("hpi_%d",i),Form("pions;%s;#eta;#Delta#Deltat (ps)",variable),npbin,0,pmax,100,-1000,1000);
    hka[i] = new TH2F(Form("hka_%d",i),Form("kaons;%s;#eta;#Delta#Deltat (ps)",variable),npbin,0,pmax,100,-1000,1000);
    hpr[i] = new TH2F(Form("hpr_%d",i),Form("protons;%s;#eta;#Delta#Deltat (ps)",variable),npbin,0,pmax,100,-1000,1000);
    hde[i] = new TH2F(Form("hde_%d",i),Form("deuterons;%s;#eta;#Delta#Deltat (ps)",variable),npbin,0,pmax,100,-1000,1000);
  }
  
  for(int i=0; i < t->GetEntries(); i++){
    t->GetEvent(i);
    if(hastrd) continue;
    int ieta = (etaT - etaMin) * etaRangeInv * neta;
    if(ieta < 0 || ieta >= neta || mT < 0.1) continue;
    
    float beta;
    beta = pT / sqrt(mT*mT + pT*pT);
    
    if(mT < 0.15){
      hpi[ieta]->Fill(pT*pT/(mT)/(texpT/12500), dtT);
    } else if(mT < 0.5) {
      hka[ieta]->Fill(pT*pT/(mT)/(texpT/12500), dtT);
    } else if(mT < 1) {
      hpr[ieta]->Fill(pT*pT/(mT)/(texpT/12500), dtT);
    } else if(mT < 2) {
      hde[ieta]->Fill(pT*pT/(mT)/(texpT/12500), dtT);
    }
  }

  for(int i=0; i < neta; i++){
    hpi[i]->Draw("colz");
    hpi[i]->FitSlicesY(ff, 0, -1, 0, "WW");
    TH1D * hp1 = (TH1D *) gDirectory->FindObject(Form("%s_1",hpi[i]->GetName()));
    TH1D * hp2 = (TH1D *) gDirectory->FindObject(Form("%s_2",hpi[i]->GetName()));
    hp1->Draw("SAME");
    hp2->Draw("SAME");
    hsigmaPi[i] = new TH1D(*hp2);
    for(int j=1; j <= hsigmaPi[i]->GetNbinsX(); j++){
      float sigmaBin = hsigmaPi[i]->GetBinContent(j);
      float sigmaBinErr = fabs(hsigmaPi[i]->GetBinError(j));
      hsigmaPi[i]->SetBinContent(j, sqrt(fabs(sigmaBin*sigmaBin - sigmaRef*sigmaRef)));
      hsigmaPi[i]->SetBinError(j,sigmaBin / hsigmaPi[0]->GetBinContent(j) * sigmaBinErr);
      hsigmaPi2D->SetBinContent(j,i+1,hsigmaPi[i]->GetBinContent(j));
      hsigmaPi2D->SetBinError(j,i+1,hsigmaPi[i]->GetBinError(j));
    }
  }  
  for(int i=0; i < neta; i++){
    hka[i]->Draw("colz");
    hka[i]->FitSlicesY(ff, 0, -1, 0, "WW");
    TH1D * hp1 = (TH1D *) gDirectory->FindObject(Form("%s_1",hka[i]->GetName()));
    TH1D * hp2 = (TH1D *) gDirectory->FindObject(Form("%s_2",hka[i]->GetName()));
    hp1->Draw("SAME");
    hp2->Draw("SAME");
    hsigmaKa[i] = new TH1D(*hp2);
    for(int j=1; j <= hsigmaKa[i]->GetNbinsX(); j++){
      float sigmaBin = hsigmaKa[i]->GetBinContent(j);
      float sigmaBinErr = fabs(hsigmaKa[i]->GetBinError(j));
      hsigmaKa[i]->SetBinContent(j, sqrt(fabs(sigmaBin*sigmaBin - sigmaRef*sigmaRef)));
      hsigmaKa[i]->SetBinError(j,sigmaBin / hsigmaKa[0]->GetBinContent(j) * sigmaBinErr);
      hsigmaKa2D->SetBinContent(j,i+1,hsigmaKa[i]->GetBinContent(j));
      hsigmaKa2D->SetBinError(j,i+1,hsigmaKa[i]->GetBinError(j));
    }
  }
  for(int i=0; i < neta; i++){
    hpr[i]->Draw("colz");
    hpr[i]->FitSlicesY(ff, 0, -1, 0, "WW");
    TH1D * hp1 = (TH1D *) gDirectory->FindObject(Form("%s_1",hpr[i]->GetName()));
    TH1D * hp2 = (TH1D *) gDirectory->FindObject(Form("%s_2",hpr[i]->GetName()));
    hp1->Draw("SAME");
    hp2->Draw("SAME");
    hsigmaPr[i] = new TH1D(*hp2);
    for(int j=1; j <= hsigmaPr[i]->GetNbinsX(); j++){
      float sigmaBin = hsigmaPr[i]->GetBinContent(j);
      float sigmaBinErr = fabs(hsigmaPr[i]->GetBinError(j));
      hsigmaPr[i]->SetBinContent(j, sqrt(fabs(sigmaBin*sigmaBin - sigmaRef*sigmaRef)));
      hsigmaPr[i]->SetBinError(j,sigmaBin / hsigmaPr[0]->GetBinContent(j) * sigmaBinErr);
      hsigmaPr2D->SetBinContent(j,i+1,hsigmaPr[i]->GetBinContent(j));
      hsigmaPr2D->SetBinError(j,i+1,hsigmaPr[i]->GetBinError(j));
    }
  }

  TCanvas *c = new TCanvas;
  c->Divide(2,2);
  c->cd(1);
  for(int i=0; i < neta; i++){
    if(i==0) hsigmaPi[i]->Draw();
    else  hsigmaPi[i]->Draw("SAME");
  }
  hsigmaPi2D->Draw("surf2");
  hsigmaPi2D->SetMaximum(200);
  //  hsigmaPi2D->GetXaxis()->SetRange(1,13);

  c->cd(2);
  for(int i=0; i < neta; i++){
    if(i==0) hsigmaKa[i]->Draw();
    else  hsigmaKa[i]->Draw("SAME");
  }
  hsigmaKa2D->Draw("surf2");
  hsigmaKa2D->SetMaximum(1000);
  hsigmaKa2D->GetXaxis()->SetRange(1,hsigmaKa[0]->FindBin(1.5));

  c->cd(3);
  for(int i=0; i < neta; i++){
    if(i==0) hsigmaPr[i]->Draw();
    else  hsigmaPr[i]->Draw("SAME");
  }
  hsigmaPr2D->Draw("surf2");
  hsigmaPr2D->SetMaximum(2000);
  hsigmaPr2D->GetXaxis()->SetRange(1,hsigmaPr[0]->FindBin(3));

  new TCanvas;
  int iref = 0;
  int iref2 = neta/2;
  hsigmaPi[iref]->Draw();
  hsigmaKa[iref]->Draw("SAME");
  hsigmaKa[iref]->SetLineColor(2);
  hsigmaKa[iref]->GetXaxis()->SetRange(1,hsigmaKa[iref]->FindBin(1.5));
  hsigmaPr[iref]->Draw("SAME");
  hsigmaPr[iref]->SetLineColor(4);
  hsigmaPr[iref]->GetXaxis()->SetRange(1,hsigmaPr[iref]->FindBin(3));
  hsigmaPi[iref2]->Draw("SAME");
  hsigmaKa[iref2]->Draw("SAME");
  hsigmaKa[iref2]->SetLineColor(2);
  hsigmaKa[iref2]->GetXaxis()->SetRange(1,hsigmaKa[iref2]->FindBin(1.5));
  hsigmaPr[iref2]->Draw("SAME");
  hsigmaPr[iref2]->SetLineColor(4);
  hsigmaPr[iref2]->GetXaxis()->SetRange(1,hsigmaPr[iref2]->FindBin(3));

  hsigmaPi[iref]->GetYaxis()->SetTitle("#it{#sigma}^{#it{X}}_{sel}");

}
