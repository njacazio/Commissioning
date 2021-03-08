TH1F *hchan = nullptr;
const int nstrip = o2::tof::Geo::NSTRIPS;
TF1 *fg;
TTree *t;
int counts[160000];
std::vector<o2::tof::CosmicInfo> v,*pv=&v;
TH1F *hdt[nstrip];
TH1F *hall,*horig;
int thr;
TProfile *htot[o2::tof::Geo::NSTRIPS];
TH2F *hL;
TH2F *hTot;

float range = 10000;

void makestep(){
  float calstrip[nstrip];
  for(int i=0; i < nstrip; i++){
    calstrip[i] = 0;
  }

  // read cal from file
  FILE *fincal = fopen("stripcal.txt","r");
  if(fincal){
    int istrip;
    float cal,ecal;
    while(fscanf(fincal,"%d %f %f",&istrip,&cal,&ecal) == 3){
      calstrip[istrip] = cal;
    }
    fclose(fincal);
  }
  
  hall->Reset();
  horig->Reset();
  for(int k1=0;k1<nstrip;k1++){
    hdt[k1]->Reset();
  }
  hL->Reset();
  hTot->Reset();

  for(int i=0; i < t->GetEntries(); i++){
    t->GetEvent(i);
    
    if(v.size()>80){
      continue;
    }
    for(int j=0; j < v.size();j++){
      int strip1 = v[j].getCH1()/96;
      int strip2 = v[j].getCH2()/96;

      if(counts[v[j].getCH1()] > thr) continue;
      if(counts[v[j].getCH2()] > thr) continue;

      float tot1 = v[j].getTOT1();
      float tot2 = v[j].getTOT2();
      
      float deltat = v[j].getDeltaTime() - calstrip[strip1] + calstrip[strip2];
      horig->Fill(v[j].getDeltaTime());
      
      if(hchan) deltat += hchan->GetBinContent(v[j].getCH1()+1) - hchan->GetBinContent(v[j].getCH2()+1);

      if(htot[strip1]) deltat += htot[strip1]->Interpolate(tot1);
      if(htot[strip2]) deltat -= htot[strip2]->Interpolate(tot2);

      //      if(htot[strip1] && htot[strip2]) printf("time slewing = %f - ch offset = %f\n",htot[strip1]->Interpolate(tot1) - htot[strip2]->Interpolate(tot2), hchan->GetBinContent(v[j].getCH1()+1) - hchan->GetBinContent(v[j].getCH2()+1));
      
      hdt[strip1]->Fill(deltat);
      hdt[strip2]->Fill(-deltat);
      hall->Fill(deltat);
      hL->Fill(v[j].getL(),deltat);
      hTot->Fill(tot1,deltat);
    }
  }

  FILE *foutcal = fopen("stripcal.txt","w");
  
  TFile *fout = new TFile("offset_strip.root","RECREATE");
  hall->Write();
  horig->Write();
  hL->Write();
  hTot->Write();
  for(int k1=0;k1<nstrip;k1++){
    if(hdt[k1]->GetEntries() > 50){
      float peak = hdt[k1]->GetBinCenter(hdt[k1]->GetMaximumBin());
      //      hdt[k1]->Draw();
      hdt[k1]->Fit(fg,"WW,Q0","",peak - range,peak + range);
      fprintf(foutcal,"%d %f %f\n",k1,fg->GetParameter(1)*0.5 + calstrip[k1],fg->GetParError(1));
      hdt[k1]->Write();
    }
  }
  fout->Close();
  fclose(foutcal);
}
void fitglobal(bool isCal = true, float scaling=1){
  range /= scaling;
  hL = new TH2F("hL",";L;#Deltat",100,500,1000,500,-50000,50000);
  hTot = new TH2F("hTot",";Tot;#Deltat",90,0,30,500,-50000,50000);
  // read time sleewing
  TFile *ftot = new TFile("tot.root");
  for(int i=0; i < o2::tof::Geo::NSTRIPS; i++){
    htot[i] = (TProfile *) ftot->Get(Form("htot_%d",i));
  }

  TFile *f = new TFile("tofclusCalInfo.root");
  t = (TTree *) f->Get("o2sim");
  t->SetBranchAddress("TOFCosmics",&pv);
  
  thr = t->GetEntries()/100;
  // noise scan
  for(int i=0;i < 160000;i++){
    counts[i] = 0;
  }
  for(int i=0; i < t->GetEntries(); i++){
    t->GetEvent(i);
    
    for(int j=0; j < v.size();j++){
      counts[v[j].getCH1()]++;
      counts[v[j].getCH2()]++;
    } 
  }

  // for(int i=0;i < 160000;i++){
  //   if(counts[i] > 0) printf("%d -> %d\n",i,counts[i]);
  // }
  if(!hchan && isCal){
    TFile *fch = TFile::Open("channel-all.root");
    if(! fch) isCal = false;
    else hchan = (TH1F *) fch->Get("hchan");
  }

  hall = new TH1F("hall","",25000,-5E6/scaling,5E6/scaling);
  horig = new TH1F("horig","",25000,-5E6,5E6);
  for(int k1=0;k1<nstrip;k1++){
    hdt[k1] = new TH1F(Form("dt_%d",k1),"",25000,-5E6/scaling,5E6/scaling);
  }

  fg = new TF1("fg","gaus");
  // fg->SetParameter(0,100);
  // fg->SetParameter(1,0);
  // fg->SetParameter(2,10000);
  // fg->SetParLimits(2,100,1000);
  for(int istep=0;istep < 20;istep++){
    makestep();
  }
}
