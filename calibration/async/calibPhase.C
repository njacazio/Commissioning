float fitPhase(TH1D *h);

int sampling=1;

TF1 *func;

void calibPhase(int run){
  system(Form("ls %d/skim*root >listPhase",run));
  TFile *chanCal = TFile::Open("TOF/Calib/ChannelCalib/snapshot.root");
  o2::dataformats::CalibTimeSlewingParamTOF *cal = (o2::dataformats::CalibTimeSlewingParamTOF *) chanCal->Get("ccdb_object");

  o2::dataformats::CalibLHCphaseTOF calPhase, *pCalPhase = &calPhase;
  
  func = new TF1("func","gaus");
  
  TChain *t = new TChain("calibTOF","calibTOF");
  FILE *fin = fopen("listPhase","r");
  char namefile[300];
  while(fscanf(fin,"%s",namefile) == 1){
    t->AddFile(namefile);
  }
  std::vector<o2::dataformats::CalibInfoTOF> vec, *pVec = &vec;
  t->SetBranchAddress("TOFCalibInfo", &pVec);

  int startoffset = 120;
  int nbin = startoffset + 120;
  int binsize = 300;
  int startTS = 0;
  for(int i=0; i < t->GetEntries(); i++){
    t->GetEvent(i);
    if(vec.size()){
      startTS = vec[0].getTimestamp() - 120*startoffset;
      break;
    }
  }
  t->GetEvent(0);
  int endTS = startTS + nbin*binsize;
  
  TH1F *h = new TH1F("h","",nbin,startTS,endTS);
  TH2F *h2 = new TH2F("h2","",nbin,startTS,endTS,8000,0,200000);
  for(int k=0; k < t->GetEntries(); k+=1000*sampling){
    for(int i=k; i < k+1000;i++){
      t->GetEvent(i);
      for(const auto& obj : vec){
	int ch = obj.getTOFChIndex();
	int ts = obj.getTimestamp();
	float tot = obj.getTot();
	float dt = obj.getDeltaTimePi() - cal->evalTimeSlewing(ch, tot);
	h->Fill(ts);
	h2->Fill(ts,dt);
      }
    }
  }

  new TCanvas;
  h2->Draw("colz");

  new TCanvas;
  int istart = h->GetNbinsX();
  int istop = 0;
  int nslot = 0;
  int startSlot[1000];
  int endSlot[1000];
  float phase[1000];
  for (int j=1; j<=h->GetNbinsX(); j++){
    if(h->GetBinContent(j) < 1000){
      continue;
    }
    if(j < istart){
      istart = j;
    }
    if(j > istop){
      istop = j;
    }
    int ts = h->GetBinCenter(j) - binsize/2;
    
    if(nslot){
      endSlot[nslot-1] = ts;
    }
    
    startSlot[nslot] = ts;
    endSlot[nslot] = ts + binsize;
    if(!nslot){
      startSlot[nslot] -= binsize; // only for the first slot
    }
    
    TH1D *hpro = h2->ProjectionY("tmp",j,j);
    
    phase[nslot] = fitPhase(hpro);
    
    nslot++;
  }
  endSlot[nslot-1] += binsize; // only for the last slot

  TFile *fcheck = new TFile(Form("check_%d.root",run),"RECREATE");
  FILE *fout = fopen(Form("phase_%d.txt",run),"w");
  
  double x[1000],y[1000],ex[1000],ey[1000];
  for(int k=0; k < nslot; k++){
    fprintf(fout,"%d %d %.0f\n",startSlot[k],endSlot[k],phase[k]);
    ex[k] = (endSlot[k] - startSlot[k])/2;
    x[k] = startSlot[k] + ex[k];
    y[k] = phase[k];
    ey[k] = 0;
    calPhase.addLHCphase(startSlot[k], phase[k]);
  }
  calPhase.addLHCphase(endSlot[nslot-1], phase[nslot-1]);
  calPhase.setStartValidity(long(startSlot[0])*1000);
  calPhase.setEndValidity(long(endSlot[nslot-1])*1000);
    
  fclose(fout);
  
  TGraphErrors *g = new TGraphErrors(nslot,x,y,ex,ey);
  g->SetMarkerStyle(20);
  new TCanvas;
  g->Draw("AP");
  h->Write();
  h2->Write();
  g->Write();
  fcheck->Close();

  TFile *fcalOut = new TFile(Form("TOF/Calib/LHCphase/o2-dataformats-CalibLHCphaseTOF_%d_%ld_%ld.root",run,long(startSlot[0])*1000,long(endSlot[nslot-1])*1000),"RECREATE");
  fcalOut->WriteObjectAny(pCalPhase, pCalPhase->Class(), "ccdb_object");
  fcalOut->Close();  
}

float fitPhase(TH1D *h){
  float val = 0;
  int binmax = h->GetMaximumBin();
  float xpeak = h->GetBinCenter(binmax);

  h->Fit(func,"WW","",xpeak-300,xpeak+300);

  return func->GetParameter(1);
}
