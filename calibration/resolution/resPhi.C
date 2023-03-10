void resPhi(float etaMin=-0.2,float etaMax=0.){
  TF1 *func = new TF1("func","gaus(0)+gaus(3)+gaus(6)",-3000,3000);
  func->SetParameter(0,1000);
  func->SetParameter(1,0);
  func->SetParLimits(1,-100,100);
  func->SetParameter(2,100);
  func->SetParLimits(2,50,200);
  func->SetParameter(3,500);
  func->SetParameter(4,800);
  func->SetParLimits(4,400,1000);
  func->SetParameter(5,130);
  func->SetParLimits(5,50,300);
  func->SetParameter(6,300);
  func->SetParameter(7,2500);
  func->SetParLimits(7,2000,3000);
  func->SetParameter(8,200);
  func->SetParLimits(8,100,500);
  func->SetNpx(1000);

  TF1 *funcRef = new TF1("funcRef","gaus(0) + pol1(3)*0",-1000,1000);
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
  int nbins = 250;

  float chi2; t->SetBranchAddress("chi2",&chi2);
  float p; t->SetBranchAddress("p",&p);
  float ptSigned; t->SetBranchAddress("ptSigned",&ptSigned);
  float ptUnsigned;
  int hastrd; t->SetBranchAddress("hastrd",&hastrd);
  float m; t->SetBranchAddress("m",&m);
  float dt; t->SetBranchAddress("dt",&dt);
  float eta; t->SetBranchAddress("eta",&eta);
  float phi; t->SetBranchAddress("phi",&phi);

  TH2F *hD2 = new TH2F("hD2",";#Delta#Deltat (ps)",18,-TMath::Pi()/36,TMath::Pi()*2-TMath::Pi()/36,nbins,-3000,3000);
  TH2F *hDD2 = new TH2F("hDD2","1.4 < #it{p}_{T} < 1.5 GeV/#it{c};#Delta#Deltat (ps)",18,-TMath::Pi()/36,TMath::Pi()*2-TMath::Pi()/36,nbins,-3000,3000);
  TH2F *h2D2 = new TH2F("h2D2","",18,-TMath::Pi()/36,TMath::Pi()*2-TMath::Pi()/36,nbins,-3000,3000);

  TH1F *hRef = new TH1F("hRef",";#Delta#Deltat (ps)",500,-1000,1000);

  int ibinMin = hD2->GetXaxis()->FindBin(1200);
  int ibinMax = hD2->GetXaxis()->FindBin(1800);
  
  for(int i=0; i < n; i++){
    t->GetEvent(i);
    if(m < 0.1 || m > 0.2) continue;

    if(chi2 < 5 && p > 0.6 && p < 0.7 && !hastrd){ // ref
      hRef->Fill(dt);
    }

//    if(!hastrd) continue;

    if(phi > TMath::Pi()*2 -TMath::Pi()/36) phi -= TMath::Pi()*2;
    
    ptUnsigned = fabs(ptSigned);
    if(ptUnsigned < 1.4 || ptUnsigned > 1.5) continue;
    if(eta<etaMin || eta > etaMax) continue;
    if(chi2 < 2) hD2->Fill(eta,dt), hDD2->Fill(phi,dt);
    else if(chi2 > 5) h2D2->Fill(phi,dt);
  }

  hRef->Fit(funcRef,"WW");

  float xx[100],ex[100],yy[100],ey[100],mean[100],meanerr[100];
  for(int i=1; i <= hDD2->GetNbinsX(); i++){
    TH1D *h = hD2->ProjectionY("hp",i,i);
    TH1D *hD = hDD2->ProjectionY(Form("hDp_%d",i),i,i);
    TH1D *h2 = h2D2->ProjectionY("h2p",i,i);
    h2->Scale(h->Integral(ibinMin,ibinMax) / h2->Integral(ibinMin,ibinMax));
    //  hD->Add(h2,-1);
    new TCanvas;
    hD->Draw();
    hD->Fit(func,"WW");
    float sigmaRef = funcRef->GetParameter(2) / sqrt(2.);
    float sigmaTrk = 0;
    float sigma = sqrt(func->GetParameter(2)*func->GetParameter(2) - sigmaRef*sigmaRef - sigmaTrk*sigmaTrk);
    float sigmaerr = func->GetParError(2) * func->GetParameter(2) / sigma;
    hD->SetStats(0);
    hD->SetTitle(Form("#eta = %.1f",hDD2->GetXaxis()->GetBinCenter(i)));
    TLatex *lt = new TLatex(-2800, hD->GetMaximum()*0.8,Form("#sigma_{TOF} = (%.0f #pm %.0f) ps\n",sigma,sigmaerr));  
    lt->Draw("SAME");
    xx[i-1] = hDD2->GetXaxis()->GetBinCenter(i);
    ex[i-1] = 0;
    yy[i-1] = sigma;
    ey[i-1] = sigmaerr;
    mean[i-1] = func->GetParameter(1);
    meanerr[i-1] = func->GetParError(1);
  }

  TGraphErrors *g = new TGraphErrors(hDD2->GetNbinsX(),xx,yy,ex,ey);
  g->SetMarkerStyle(20);
  g->SetName("gRes");
  TGraphErrors *g2 = new TGraphErrors(hDD2->GetNbinsX(),xx,mean,ex,meanerr);
  g2->SetMarkerStyle(20);
  g2->SetName("gMean");
  new TCanvas;
  g->Draw("AP");
  g->SetTitle("#sigma_{TOF} vs #eta; #phi (rad); #sigma_{TOF} (ps)");
  g->SetMaximum(100);
  g->SetMinimum(50);
  TF1 *ffp = new TF1("ffp","pol0");
  g->Fit(ffp);
  TLatex *lt = new TLatex(-0.8, 60,Form("#sigma_{TOF} = (%.1f #pm %.1f) ps\n",ffp->GetParameter(0),ffp->GetParError(0)));  
  lt->Draw("SAME");

  TFile *fout = new TFile(Form("res_%.1f_%.1f.root",etaMin,etaMax + 1E-6),"RECREATE");
  g->Write();
  g2->Write();
  fout->Close();
}
