void res2(){
  TF1 *func = new TF1("func","gaus(0)+gaus(3)+gaus(6)",-3000,3000);
  func->SetParameter(0,1000);
  func->SetParameter(1,0);
  func->SetParLimits(1,-100,100);
  func->SetParameter(2,100);
  func->SetParLimits(2,50,200);
  func->SetParameter(3,500);
  func->SetParameter(4,400);
  func->SetParLimits(4,250,500);
  func->SetParameter(5,130);
  func->SetParLimits(5,50,300);
  func->SetParameter(6,300);
  func->SetParameter(7,1500);
  func->SetParLimits(7,1000,2000);
  func->SetParameter(8,200);
  func->SetParLimits(8,100,500);
  func->SetNpx(1000);

  TF1 *funcRef = new TF1("funcRef","gaus(0) + pol1(3)",-1000,1000);
  funcRef->SetParameter(0,1000);
  funcRef->SetParameter(1,0);
  funcRef->SetParLimits(1,-100,100);
  funcRef->SetParameter(2,120);
  funcRef->SetParLimits(2,50,300);
  funcRef->SetParameter(3,10);
  funcRef->SetParameter(4,-0.01);
  funcRef->SetNpx(1000);

  TFile *f = new TFile("full.root");
  TTree *t = (TTree *) f->Get("tree");

  int n = t->GetEntries();

  float chi2; t->SetBranchAddress("chi2",&chi2);
  float p; t->SetBranchAddress("p",&p);
  float ptSigned; t->SetBranchAddress("ptSigned",&ptSigned);
  float ptUnsigned;
  int hastrd; t->SetBranchAddress("hastrd",&hastrd);
  float m; t->SetBranchAddress("m",&m);
  float dt; t->SetBranchAddress("dt",&dt);
  float eta; t->SetBranchAddress("eta",&eta);

  TH1F *h = new TH1F("h",";#Delta#Deltat (ps)",1000,-3000,3000);
  TH1F *hD = new TH1F("hD","1.8 < #it{p}_{T} < 2.0 GeV/#it{c};#Delta#Deltat (ps)",1000,-3000,3000);
  TH1F *h2 = new TH1F("h2","",1000,-3000,3000);
  h2->SetLineColor(2);

  TH1F *hRef = new TH1F("hRef",";#Delta#Deltat (ps)",500,-1000,1000);

  int ibinMin = h->FindBin(2500);
  int ibinMax = h->FindBin(3000);
  
  for(int i=0; i < n; i++){
    t->GetEvent(i);
    if(m < 0.1 || m > 0.2) continue;

    if(chi2 < 5 && p > 0.6 && p < 0.7 && !hastrd){ // ref
      hRef->Fill(dt);
    }
    if(hastrd) continue;

    ptUnsigned = fabs(ptSigned);
    if(ptUnsigned < 1.8 || ptUnsigned > 2.0) continue;
    if(fabs(eta)>0.1) continue;
    if(chi2 < 2) h->Fill(dt), hD->Fill(dt);
    else if(chi2 > 5) h2->Fill(dt);
  }

  hRef->Fit(funcRef,"WW");
  
  h->Sumw2();
  hD->Sumw2();
  h2->Sumw2();

  TCanvas *c = new TCanvas;
  c->Divide(2,1);
  c->cd(1)->SetLogy();
  h->Draw();
  h2->Draw("SAME");
  h2->Scale(h->Integral(ibinMin,ibinMax) / h2->Integral(ibinMin,ibinMax));

  c->cd(2);
  hD->Add(h2,-1);
  hD->Draw();
  hD->Fit(func,"WW");

  float sigmaRef = funcRef->GetParameter(2) / sqrt(2.);
  float sigmaTrk = 0;
  float sigma = sqrt(func->GetParameter(2)*func->GetParameter(2) - sigmaRef*sigmaRef - sigmaTrk*sigmaTrk);
  
  printf("TOF resolution = %f ps (ref = %f) after tracking contribution removed (sigmaTrk = %f)\n",sigma,sigmaRef,sigmaTrk);

  new TCanvas;
  hD->Draw();
  hD->SetStats(0);
  
}
