class myclass {
public:
  myclass(float ps, float etas, float phis, float deltats, float chi2s, float ls, int hastrds, UChar_t trdPatts, float ptSigneds, float chi2trds, float fXs, float fAlphas, float fYs, float fZs, float fSnps, float fTgls) : p(ps), eta(etas), phi(phis), deltat(deltats), chi2(chi2s), l(ls), hastrd(hastrds), trdPatt(trdPatts), ptSigned(ptSigneds), chi2trd(chi2trds), fX(fXs), fAlpha(fAlphas), fY(fYs), fSnp(fSnps), fTgl(fTgls) {}
  float p;
  float eta;
  float phi;
  float deltat;
  float chi2;
  float l;
  int hastrd;
  UChar_t trdPatt;
  float ptSigned;
  float chi2trd;
  float fX;
  float fAlpha;
  float fY;
  float fZ;
  float fSnp;
  float fTgl;
};

void checkGrid(const char* filename, int instance){
  TGrid::Connect("alien://");
  TFile *f = TFile::Open(filename);
  int ndir = f->GetListOfKeys()->GetSize();

  float pRefMin = 0.6;
  float pRefMax = 0.7;

  float chiTh = 5;
  float deltatTh = 500;
  
  const int maxColIndex = 20000;

  const float massEl = 0.0005;
  const float massPi = 0.13957039;
  const float massPiSquare = massPi*massPi;
  const float massKa = 0.493677;
  const float massPr = 0.93827208816;
  const float massDe = 1.8756;
  
  int prevColNum = -1;
  std::vector<myclass> vec[maxColIndex];
  
  int indexCol;
  float tofChi2;
  float itsChi2;
  float expMom;
  float length;
  float trkTime;
  float expPi, tof, betaPi;
  float eta = 0;
  float phi = 0;
  float texpPi;
  UChar_t clsFindable;
  TH2F *h = new TH2F("h",";<p_{TOF}> (GeV/#it{c}); #Deltat_{#pi} - #Deltat_{#pi}^{ref}",200,0,5,200,-1000,1000);
  TH2F *h2 = new TH2F("h2",";<p_{TOF}> (GeV/#it{c}); #Deltat_{#pi} - #Deltat_{#pi}^{ref}",200,0,5,200,-1000,1000);

  TH1F *hGood = new TH1F("hGood","",500,-3000,3000);
  TH1F *hDiff = new TH1F("hDiff","",500,-3000,3000);
  TH1F *hBad = new TH1F("hBad","",500,-3000,3000);
  hBad->SetLineColor(2);

  TFile *fout = new TFile(Form("tree_%04d.root",instance),"RECREATE");
  TTree *tout = new TTree("tree","tree");
  float chi2T; tout->Branch("chi2",&chi2T);
  float pT; tout->Branch("p",&pT);
  float etaT; tout->Branch("eta",&etaT);
  float phiT; tout->Branch("phi",&phiT);
  float lT; tout->Branch("l",&lT);
  float mT; tout->Branch("m",&mT);
  float texpT; tout->Branch("texp",&texpT);
  float dtT; tout->Branch("dt",&dtT);
  int hastrd; tout->Branch("hastrd",&hastrd);
  float ptSigned; tout->Branch("ptSigned",&ptSigned);
  float trdChi2; tout->Branch("trdchi2",&trdChi2);
  UChar_t trdPatt; tout->Branch("trdPatt",&trdPatt);
  float fX; // tout->Branch("fX",&fX);
  float fAlpha; // tout->Branch("fAlpha",&fAlpha);
  float fY; // tout->Branch("fY",&fY);
  float fZ; // tout->Branch("fZ",&fZ);
  float fSnp; // tout->Branch("fSnp",&fSnp);
  float fTgl; // tout->Branch("fTgl",&fTgl);

  for (int i=0; i < ndir; i++){
    TTree *tt = (TTree *) f->Get(Form("%s/O2track_iu",f->GetListOfKeys()->At(i)->GetName()));
    if(!tt) continue;
    TTree *te = (TTree *) f->Get(Form("%s/O2trackextra",f->GetListOfKeys()->At(i)->GetName()));
    tt->SetBranchAddress("fIndexCollisions",&indexCol);
    tt->SetBranchAddress("fTgl",&fTgl);
    tt->SetBranchAddress("fSnp",&fSnp);
    tt->SetBranchAddress("fAlpha",&fAlpha);
    tt->SetBranchAddress("fSigned1Pt",&ptSigned);
    tt->SetBranchAddress("fX",&fX);
    tt->SetBranchAddress("fY",&fY);
    tt->SetBranchAddress("fZ",&fZ);

    te->SetBranchAddress("fITSChi2NCl",&itsChi2);
    te->SetBranchAddress("fTOFChi2",&tofChi2);
    te->SetBranchAddress("fTRDChi2",&trdChi2);
    te->SetBranchAddress("fTOFExpMom",&expMom);
    te->SetBranchAddress("fLength",&length);
    te->SetBranchAddress("fTrackTime",&trkTime);
    te->SetBranchAddress("fTRDPattern",&trdPatt);
    te->SetBranchAddress("fTPCNClsFindable",&clsFindable);
  
    printf("Size = %lld or %lld\n",tt->GetEntries(),te->GetEntries());

    for(int j=0; j < prevColNum+1; j++){
      vec[j].clear();
    }
    prevColNum = -1;
    
    for(int j=0; j < tt->GetEntries(); j++){
      tt->GetEvent(j);
      te->GetEvent(j);

      if(clsFindable < 110) continue;
      
      if(indexCol < 0 || indexCol >= maxColIndex) continue;
      if(itsChi2 < 0 || tofChi2 < 0) continue;

      if(indexCol > prevColNum){
	prevColNum = indexCol;
      }
      betaPi = expMom / sqrt(massPiSquare + expMom*expMom);
      expPi = length / (betaPi * 29.979246E-3); // in ps
      tof = expPi + trkTime*1000; // in ps
      eta = log(tan(0.25f * TMath::Pi() - 0.5f * atan(fTgl)));
      phi = asin(fSnp) + fAlpha + TMath::Pi();
      if(phi < 0) phi += 2*TMath::Pi();
      if(phi > 2*TMath::Pi()) phi -= 2*TMath::Pi();

      if(trdChi2 >= 0) hastrd = 1;
      else hastrd = 0;

      vec[indexCol].emplace_back(expMom, eta, phi, tof - expPi, tofChi2, length, hastrd, trdPatt, ptSigned, trdChi2, fX, fAlpha, fY, fZ, fSnp,fTgl);
    }

    for(int j=0; j < prevColNum+1; j++){
      if(vec[j].size() < 2) continue;

      for(int k1 = 0; k1 < vec[j].size(); k1++){
	const auto& p1 = vec[j][k1];
	if(p1.p < pRefMin || p1.p > pRefMax || p1.chi2 > chiTh || fabs(p1.deltat) > deltatTh || p1.hastrd) continue;
	for(int k2 = 0; k2 < vec[j].size(); k2++){
	  if(k1 == k2) continue;
	  const auto& p2 = vec[j][k2];
	  if(p2.chi2 < chiTh){
	    h->Fill(p2.p, p2.deltat - p1.deltat);
	  } else if(p2.chi2>chiTh) {
	    h2->Fill(p2.p, p2.deltat - p1.deltat);
	  }	    
	  if(p2.p > pRefMin && p2.p < pRefMax){
	    if(p2.chi2<chiTh){
	      hGood->Fill(p2.deltat - p1.deltat);
	      hDiff->Fill(p2.deltat - p1.deltat);
	    }
	    else if(p2.chi2>chiTh+2) hBad->Fill(p2.deltat - p1.deltat);
	  }
	  fX = p2.fX;
	  fAlpha = p2.fAlpha;
	  fY = p2.fY;
	  fZ = p2.fZ;
	  fSnp = p2.fSnp;
	  fTgl = p2.fTgl;
	  ptSigned = 1./ p2.ptSigned;
          hastrd = p2.hastrd;
	  trdChi2 = p2.chi2trd;
	  chi2T = p2.chi2;
	  etaT = p2.eta;
	  phiT = p2.phi;
	  lT = p2.l;
	  pT = p2.p,
	  dtT = p2.deltat - p1.deltat;
	  mT = massPi;
	  trdPatt = p2.trdPatt;
	  betaPi = pT / sqrt(mT*mT + pT*pT);
	  texpPi = texpT = lT / (betaPi * 29.979246E-3); // in ps
	  if(fabs(dtT) < 3000) tout->Fill();
	  mT = massKa;
	  betaPi = pT / sqrt(mT*mT + pT*pT);
	  texpT = lT / (betaPi * 29.979246E-3); // in ps
	  dtT = p2.deltat - p1.deltat + texpPi - texpT;
	  if(fabs(dtT) < 3000) tout->Fill();
	  mT = massPr;
	  betaPi = pT / sqrt(mT*mT + pT*pT);
	  texpT = lT / (betaPi * 29.979246E-3); // in ps
	  dtT = p2.deltat - p1.deltat + texpPi - texpT;
	  if(fabs(dtT) < 3000) tout->Fill();
	  mT = massDe;
	  betaPi = pT / sqrt(mT*mT + pT*pT);
	  texpT = lT / (betaPi * 29.979246E-3); // in ps
	  dtT = p2.deltat - p1.deltat + texpPi - texpT;
	  if(fabs(dtT) < 3000) tout->Fill();
	  mT = massEl;
	  betaPi = pT / sqrt(mT*mT + pT*pT);
	  texpT = lT / (betaPi * 29.979246E-3); // in ps
	  dtT = p2.deltat - p1.deltat + texpPi - texpT;
	  if(fabs(dtT) < 3000) tout->Fill();
	}
      }
    }
  }

  tout->Write();
  fout->Close();
  
  h->Draw("colz");
  TF1 *ff = new TF1("ff","gaus",-1000,1000);
  
  h->FitSlicesY(ff,0,-1,0,"WR");
  TH1D * hp1 = (TH1D *) gDirectory->FindObject("h_1");
  TH1D * hp2 = (TH1D *) gDirectory->FindObject("h_2");
  hp1->Draw("SAME");
  hp2->Draw("SAME");
  new TCanvas;
  hGood->Draw();
  hGood->Fit(ff,"W","",-1000,1000);
  //  hBad->Draw("SAME");
  hGood->Sumw2();
  hBad->Sumw2();
  hDiff->Sumw2();
  hBad->Scale(hGood->Integral(80,160) / (hBad->Integral(80,160) + 1));
  new TCanvas;
  hDiff->Add(hBad,-1);
  hDiff->Draw();

  int refbin = hp2->FindBin((pRefMin+pRefMax)*0.5);
  float sigma = ff->GetParameter(2)/sqrt(2.);//hp2->GetBinContent(refbin)/sqrt(2.);
  printf("Resolution: %.2f < <p> < %.2f GeV/c -- sigmaDelta = %.1f ps - sigma = sigmaDelta/sqrt{2} = %.1f\n",pRefMin,pRefMax,ff->GetParameter(2),sigma);

  new TCanvas;
  TH1D *hsigma = new TH1D(*hp2);
  hsigma->SetName("hsigma");
  for(int i=1; i <= hsigma->GetNbinsX(); i++){
    float sigmaBin = hsigma->GetBinContent(i);
    float sigmaBinErr = fabs(hsigma->GetBinError(i));
    hsigma->SetBinContent(i, sqrt(fabs(sigmaBin*sigmaBin - sigma*sigma)));
    hsigma->SetBinError(i,sigmaBin / hsigma->GetBinContent(i) * sigmaBinErr);
  }
  hsigma->Draw();
}
