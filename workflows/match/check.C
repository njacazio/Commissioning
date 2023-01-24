void setHisto(TH1 *h, int icolor=1){
    h->SetLineColor(icolor);
    h->SetMarkerColor(icolor);
    h->SetMarkerStyle(20);
    h->SetMarkerSize(1.5);
    h->GetXaxis()->SetTitleSize(0.05);
    h->GetXaxis()->SetNdivisions(409);
    h->GetXaxis()->CenterTitle();
    h->GetYaxis()->SetTitleSize(0.05);
    h->GetYaxis()->SetNdivisions(409);    
    h->GetYaxis()->CenterTitle();
    h->Sumw2();
}

void check(const char* filename="TOFperformance.root"){
  TFile *f = new TFile(filename);
  TTree *t = (TTree *) f->Get("tree");
  int nev = t->GetEntries();

  // histo vars
  int nbinPt = 50;
  float minPt = 0;
  float maxPt = 5;
  
  // set variables
  int ch; t->SetBranchAddress("ch",&ch);
  float pt; float ptSigned; t->SetBranchAddress("pt",&ptSigned);
  int source; t->SetBranchAddress("source",&source); //0=TPC,1=ITS-TPC,2=TPC-TRD,3=ITS-TPC-TRD
  const char* sources[4] = {"TPC","ITS-TPC","TPC-TRD","ITS-TPC-TRD"};
  float eta; t->SetBranchAddress("eta",&eta);
  float phi; t->SetBranchAddress("phi",&phi);
  float tof; t->SetBranchAddress("tof",&tof);
  float trkTime; t->SetBranchAddress("trkTime",&trkTime);
  float dx; t->SetBranchAddress("dx",&dx);
  float dz; t->SetBranchAddress("dz",&dz);
  float expPi; t->SetBranchAddress("expPi",&expPi);
  float chi2; t->SetBranchAddress("chi2",&chi2);

  // define histos
  int icolor[4] = {1,2,4,6};
  TH1F *hPt[4];
  TProfile *hFr[4];
  TProfile *hCand[4];
  TProfile *hMatch[4];
  TH2F *hPosDx = new TH2F("hPosDx","run 523667 ITS-TPC POS tracks #it{p}_{T} > 2 GeV/#it{c}; strip # ;#Delta#it{x} (cm);",1638,0,1638,25,-50,50);
  setHisto(hPosDx, icolor[1]);
  TH2F *hNegDx = new TH2F("hNegDx","run 523667 ITS-TPC NEG tracks #it{p}_{T} > 2 GeV/#it{c}; strip # ;#Delta#it{x} (cm);",1638,0,1638,25,-50,50);
  setHisto(hNegDx, icolor[1]);

  TH1F *hPosDx1D = new TH1F("hPosDx1D","run 523667 ITS-TPC tracks #it{p}_{T} > 2 GeV/#it{c}; #Delta#it{x} (cm);",100,-50,50);
  setHisto(hPosDx1D, 2);
  TH1F *hNegDx1D = new TH1F("hNegDx1D","run 523667 ITS-TPC NEG tracks #it{p}_{T} > 2 GeV/#it{c}; #Delta#it{x} (cm);",100,-50,50);
  setHisto(hNegDx1D, 4);

  TProfile *hEffPosITSTPC = new TProfile("hEffPosITSTPC","run 523667 ITS-TPC tracks;#it{p}_{T} (GeV/#it{c});matching efficieny",nbinPt,minPt,maxPt);
  setHisto(hEffPosITSTPC, 2);
  TProfile *hEffNegITSTPC = new TProfile("hEffNegITSTPC","run 523667 ITS-TPC NEG tracks;#it{p}_{T} (GeV/#it{c});matching efficieny",nbinPt,minPt,maxPt);
  setHisto(hEffNegITSTPC, 4);

  for(int i=0; i < 4; i++){
    hPt[i] = new TH1F(Form("hPt_%s",sources[i]),Form("run 523667; #it{p}_{T} (GeV/#it{c});entries"),nbinPt*2,-maxPt,maxPt);
    setHisto(hPt[i], icolor[i]);

    hFr[i] = new TProfile(Form("hFr_%s",sources[i]),Form("run 523667; #it{charge} x #it{p}_{T} (GeV/#it{c});fraction"),nbinPt,minPt,maxPt);
    setHisto(hFr[i], icolor[i]);

    hCand[i] = new TProfile(Form("hCand_%s",sources[i]),Form("run 523667; #it{p}_{T} (GeV/#it{c});cand match efficiency"),nbinPt,minPt,maxPt);
    setHisto(hCand[i], icolor[i]);

    hMatch[i] = new TProfile(Form("hMatch_%s",sources[i]),Form("run 523667; #it{p}_{T} (GeV/#it{c});matching efficiency"),nbinPt,minPt,maxPt);
    setHisto(hMatch[i], icolor[i]);
  }
  
  for(int i=0; i < nev; i++){
    t->GetEvent(i);
    if(fabs(eta) > 0.8) continue;
    pt = fabs(ptSigned);

    hFr[0]->Fill(pt, source==0);
    hFr[1]->Fill(pt, source==1);
    hFr[2]->Fill(pt, source==2);
    hFr[3]->Fill(pt, source==3);    

    hPt[source]->Fill(ptSigned);
    hCand[source]->Fill(pt, ch>-1);
    hMatch[source]->Fill(pt, (ch>-1) && (chi2 < 10));

    if(source == 1 && pt > 2){
      if(ptSigned > 0){
	hPosDx->Fill(ch/96, dx);
	hPosDx1D->Fill(dx);
      } else {
	hNegDx->Fill(ch/96, dx);
	hNegDx1D->Fill(dx);
      }
    }

    if(source == 1){
      if(ptSigned > 0){
	hEffPosITSTPC->Fill(pt,(ch>-1) && (chi2 < 10));
      } else {
	hEffNegITSTPC->Fill(pt,(ch>-1) && (chi2 < 10));
      }
    }
  }

  TCanvas *cPt = new TCanvas("cPt","cPt");
  cPt->SetLogy();
  cPt->SetBottomMargin(0.15);
  cPt->SetLeftMargin(0.15);
  cPt->SetRightMargin(0.05);
  hPt[0]->SetMinimum(1);
  hPt[0]->Draw("P");
  hPt[0]->SetStats(0);
  hPt[1]->Draw("P,SAME");
  hPt[2]->Draw("P,SAME");
  hPt[3]->Draw("P,SAME");
  TLegend *legPt = new TLegend(0.7,0.7,0.95,0.9);
  legPt->SetFillStyle(0);
  for(int is=0; is < 4; is++)
    legPt->AddEntry(hPt[is],sources[is],"lp");
  legPt->Draw("SAME");

  TCanvas *cFr = new TCanvas("cFr","cFr");
  cFr->SetBottomMargin(0.15);
  cFr->SetLeftMargin(0.15);
  cFr->SetRightMargin(0.05);
  hFr[0]->Draw("P");
  hFr[0]->SetMaximum(1);
  hFr[0]->SetMinimum(0);
  hFr[0]->SetStats(0);
  hFr[1]->Draw("P,SAME");
  hFr[2]->Draw("P,SAME");
  hFr[3]->Draw("P,SAME");
  TLegend *legFr = new TLegend(0.7,0.7,0.95,0.9);
  legFr->SetFillStyle(0);
  for(int is=0; is < 4; is++)
    legFr->AddEntry(hFr[is],sources[is],"lp");
  legFr->Draw("SAME");

  TCanvas *cCand = new TCanvas("cCand","cCand");
  cCand->SetBottomMargin(0.15);
  cCand->SetLeftMargin(0.15);
  cCand->SetRightMargin(0.05);
  hCand[0]->Draw("P");
  hCand[0]->SetMaximum(1);
  hCand[0]->SetMinimum(0);
  hCand[0]->SetStats(0);
  hCand[1]->Draw("P,SAME");
  hCand[2]->Draw("P,SAME");
  hCand[3]->Draw("P,SAME");
  TLegend *legCand = new TLegend(0.7,0.7,0.95,0.9);
  legCand->SetFillStyle(0);
  for(int is=0; is < 4; is++)
    legCand->AddEntry(hCand[is],sources[is],"lp");
  legCand->Draw("SAME");

  TCanvas *cMatch = new TCanvas("cMatch","cMatch");
  cMatch->SetBottomMargin(0.15);
  cMatch->SetLeftMargin(0.15);
  cMatch->SetRightMargin(0.05);
  hMatch[0]->Draw("P");
  hMatch[0]->SetMaximum(1);
  hMatch[0]->SetMinimum(0);
  hMatch[0]->SetStats(0);
  hMatch[1]->Draw("P,SAME");
  hMatch[2]->Draw("P,SAME");
  hMatch[3]->Draw("P,SAME");
  TLegend *legMatch = new TLegend(0.7,0.7,0.95,0.9);
  legMatch->SetFillStyle(0);
  for(int is=0; is < 4; is++)
    legMatch->AddEntry(hMatch[is],sources[is],"lp");
  legMatch->Draw("SAME");

  TCanvas *cDx = new TCanvas("cDx","cDx");
  cDx->Divide(2,1);
  cDx->cd(1)->SetLogz();
  cDx->cd(1)->SetBottomMargin(0.15);
  cDx->cd(1)->SetLeftMargin(0.15);
  cDx->cd(1)->SetRightMargin(0.05);
  hPosDx->Draw("colz");
  hPosDx->SetStats(0);
  cDx->cd(2)->SetLogz();
  cDx->cd(2)->SetBottomMargin(0.15);
  cDx->cd(2)->SetLeftMargin(0.15);
  cDx->cd(2)->SetRightMargin(0.05);
  hNegDx->Draw("colz");
  hNegDx->SetStats(0);

  TCanvas *cDx1D = new TCanvas("cDx1D","cDx1D");
  cDx1D->SetBottomMargin(0.15);
  cDx1D->SetLeftMargin(0.15);
  cDx1D->SetRightMargin(0.05);
  cDx1D->SetLogy();
  cDx1D->SetGridy();
  hPosDx1D->Draw("P");
  hPosDx1D->SetStats(0);
  hPosDx1D->SetMaximum(5E4);
  hPosDx1D->SetMinimum(1);
  hNegDx1D->Draw("P,SAME");
  TLegend *legDx = new TLegend(0.7,0.7,0.95,0.9);
  legDx->SetFillStyle(0);
  legDx->AddEntry(hPosDx1D,"POS","lp");
  legDx->AddEntry(hNegDx1D,"NEG","lp");
  legDx->Draw("SAME");

  TCanvas *cEffITSTPC = new TCanvas("cEffITSTPC","cEffITSTPC");
  cEffITSTPC->SetBottomMargin(0.15);
  cEffITSTPC->SetLeftMargin(0.15);
  cEffITSTPC->SetRightMargin(0.05);
  cEffITSTPC->SetGridy();
  hEffPosITSTPC->Draw("P");
  hEffPosITSTPC->SetStats(0);
  hEffPosITSTPC->SetMaximum(1);
  hEffPosITSTPC->SetMinimum(0);
  hEffNegITSTPC->Draw("P,SAME");
  TLegend *legEffITSTPC = new TLegend(0.7,0.7,0.95,0.9);
  legEffITSTPC->SetFillStyle(0);
  legEffITSTPC->AddEntry(hEffPosITSTPC,"POS","lp");
  legEffITSTPC->AddEntry(hEffNegITSTPC,"NEG","lp");
  legEffITSTPC->Draw("SAME");

}
