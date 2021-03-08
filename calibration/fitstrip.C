#include"TROOT.h"
#include"TFile.h"
#include"TTree.h"
#include"TCanvas.h"
#include"TH1F.h"
#include"TH2F.h"
#include"TF1.h"
#include"TGraphErrors.h"
#include"TProfile.h"
#include "DataFormatsTOF/CalibInfoCluster.h"
#include "TOFBase/Geo.h"

TTree *t;
std::vector<o2::tof::CalibInfoCluster> v,*pv=&v;
TH1F *hchan = nullptr;
TProfile *htot[o2::tof::Geo::NSTRIPS];
TProfile *htotOld[o2::tof::Geo::NSTRIPS];
const int ncomb = 2*96;
TH1F *hsh[o2::tof::Geo::NSTRIPS][ncomb];
TFile *foutTOT = nullptr;
TH2F *hcheck = nullptr;
TH1F *hcheck2 = nullptr;

double MyFunc(double* x, double* params) {
  int i1 = int(x[0]+0.5)%96;
  int i2 = int(x[0]+0.5)/96 ? (i1 - 48) : (i1 - 1);
  
  if(i1 > 95) return 0;
  if(i2 < 0) return 0;
  
  return (params[i1] - params[i2]); 
}

void fitoffset(bool applytot=false,int stripsel=1306){
  TF1 *ff = new TF1("fChanOffset",MyFunc,0,ncomb,96);
  ff->SetNpx(ncomb*10);
  ff->FixParameter(24,0);
  
  for(int is=0; is < o2::tof::Geo::NSTRIPS; is++){
    for(int i=0; i < ncomb; i++){
      if(! hsh[is][i]) hsh[is][i] = new TH1F(Form("hsh_%d_%d",is,i),"",50,-5000,5000);
      else  hsh[is][i]->Reset();
    }
  }
  
  for(int i=0; i < t->GetEntries(); i++){
    t->GetEvent(i);
    
    for(uint64_t j=0; j < v.size(); j++){
      o2::tof::CalibInfoCluster& cl = v[j];
      int ch = cl.getCH();
      int strip = ch/96;
      
      int dch = cl.getDCH();
      float dt = cl.getDT();
      
      float tot1 = cl.getTOT1()*48E-3;
      float tot2 = cl.getTOT2()*48E-3;
      
      if(dch > 0){
	ch += dch;
	dt = -dt;
	dch = -dch;
	float inv = tot1;
	tot1 = tot2;
	tot2 = inv;
      } 
      
      int shift = 0; // left
      if(dch == -1) shift = 0; // left 
      else if(dch == -48) shift = 1; //bottom
      else continue;
      int chL = ch%96;
      int comb = 96*shift + chL;

      if(applytot){
	dt -= htot[strip]->Interpolate(tot1) - htot[strip]->Interpolate(tot2);
      }
      
      hsh[strip][comb]->Fill(dt);
    }
  }
  int np=0;
  float x[ncomb],ex[ncomb],y[ncomb],ey[ncomb];
  TF1 *fg = new TF1("fg","gaus",-5000,5000);
  //   TF1 *fg = new TF1("fg","[0]*(TMath::Exp(-(x-[1]-[3])*(x-[1]-[3])/[2]/[2]) + TMath::Exp(-(x-[1]+[3])*(x-[1]+[3])/[2]/[2])*[4])",-5000,5000);
  fg->SetParameter(0,100);
  fg->SetParameter(1,0);
  fg->SetParLimits(1,-5000,5000);
  fg->SetParameter(2,60);
  fg->SetParLimits(2,50,500);
  
  hchan = new TH1F("hchan","",o2::tof::Geo::NSTRIPS*96,0,96*o2::tof::Geo::NSTRIPS);
  TGraphErrors *gRef = nullptr;
  for(int is=0; is < o2::tof::Geo::NSTRIPS; is++){
    np = 0;
    for(int i=0; i < ncomb; i++){
      if(hsh[is][i]->GetEntries() < 30) continue;
      fg->SetParameter(1,hsh[is][i]->GetBinCenter(hsh[is][i]->GetMaximumBin()));
      float peak = hsh[is][i]->GetBinCenter(hsh[is][i]->GetMaximumBin());
      hsh[is][i]->Fit(fg,"W,Q0","",peak - 1000,peak +1000);
      float xmin = fg->GetParameter(1) - fg->GetParameter(2)*5;
      float xmax = fg->GetParameter(1) + fg->GetParameter(2)*5;
      
      hsh[is][i]->Fit(fg,"Q0","",xmin,xmax);
      
      x[np] = i;
      ex[np] = 0;
      y[np] = fg->GetParameter(1);
      ey[np] = fg->GetParError(1);
      np++;
    }
    TGraphErrors *g = new TGraphErrors(np,x,y,ex,ey);
    
    if(np==0) continue;
    g->Fit(ff,"Q0");
    for(int i=0; i < 96;i++){
      hchan->SetBinContent(i+1+is*96,ff->GetParameter(i));
      hchan->SetBinError(i+1+is*96,ff->GetParError(i));
    }
    if(is != stripsel) delete g;
    else gRef = g;
  }
  
  new TCanvas;
  TGraphErrors *g = gRef;
  g->SetMarkerStyle(20);
  g->Draw("AP");
  g->Fit(ff);
  
  printf("Chi2 = %f\n",ff->GetChisquare()/ff->GetNDF());
  
  TH1F *herr = new TH1F("herr","",100,0,500);
  for(int i=0;i < 96;i++) herr->Fill(ff->GetParError(i));
  new TCanvas;
  herr->Draw();
  
  new TCanvas;
  TH1F *hpar = new TH1F("hpar","",96,0,96);
  for(int i=0; i < 96;i++){
    hpar->SetBinContent(i+1,ff->GetParameter(i));
    hpar->SetBinError(i+1,ff->GetParError(i));
  }
  hpar->Draw();
  
  new TCanvas;
  hchan->Draw();
  
  TFile *fout = new TFile("channel-all.root","RECREATE");
  hchan->Write();
  fout->Close();

  // for(int is=0; is < o2::tof::Geo::NSTRIPS; is++){
  //   for(int i=0; i < ncomb; i++){
  //     delete hsh[is][i];
  //     hsh[is][i] = nullptr;
  //   }
  // }
  printf("DONE\n");
}

void fittot(bool onlytot=false, bool write=true){
  if(! hchan) return;

  if(! foutTOT) foutTOT = new TFile("tot.root","RECREATE");
  else foutTOT->cd();
  for(int is=0; is < o2::tof::Geo::NSTRIPS; is++){
    if(! htot[is]) htot[is] = new TProfile(Form("htot_%d",is),"",100*96*0+1000,0,1000*96*0 + 1000);
    if(onlytot && ! htotOld[is]) htotOld[is] = new TProfile(Form("htotOld_%d",is),"",100*96*0+1000,0,1000*96*0 + 1000);
  }

  if(! hcheck) hcheck = new TH2F("hcheck","",2000,0,1000,200,-1000,1000);
  else hcheck->Reset();
  if(! hcheck2) hcheck2 = new TH1F("hcheck2","",400,-10000,10000);
  else hcheck2->Reset();
  
  for(int i=0; i < t->GetEntries(); i++){
    t->GetEvent(i);
    for(uint64_t j=0; j < v.size(); j++){
      o2::tof::CalibInfoCluster& cl = v[j];
      int ch = cl.getCH();
      int strip = ch/96;

      bool skip = false;
      
      int dch = cl.getDCH();
      float dt = cl.getDT();
      
      float tot1 = cl.getTOT1()*48E-3;
      float tot2 = cl.getTOT2()*48E-3;
      
      if(dch > 0){
	ch += dch;
	dt = -dt;
	dch = -dch;
	float inv = tot1;
	tot1 = tot2;
	tot2 = inv;
      }

      int chL1 = ch%96;
      int chL2 = chL1 + dch;
      dt -= hchan->GetBinContent(ch+1) - hchan->GetBinContent(ch+1+dch);

      float dtExp1 = 0;
      float dtExp2 = 0;
      if(onlytot && write){
	dtExp1 = htotOld[strip]->Interpolate(tot1 + chL1*1000*0);
	dtExp2 = -htotOld[strip]->Interpolate(tot2 + chL2*1000*0);

	if(abs(dt-dtExp1-dtExp2) > 1000) skip=1;
      }
      
      if(strip == 273) hcheck->Fill(tot1,dt);
      if(strip == 273) hcheck->Fill(tot2,-dt);

      if(skip) continue;

      if(write){
	htot[strip]->Fill(tot1 + chL1*1000*0,dt-dtExp2);
	htot[strip]->Fill(tot2 + chL2*1000*0,-dt+dtExp1);
      }
      else if(onlytot){
	htotOld[strip]->Fill(tot1 + chL1*1000*0,dt);
	htotOld[strip]->Fill(tot2 + chL2*1000*0,-dt);
      }
    }
  }


  if(write){
    for(int i=0; i < t->GetEntries(); i++){
      t->GetEvent(i);
      for(uint64_t j=0; j < v.size(); j++){
        o2::tof::CalibInfoCluster& cl = v[j];
        int ch = cl.getCH();
        int strip = ch/96;

        bool skip = false;
      
        int dch = cl.getDCH();
        float dt = cl.getDT();
      
        float tot1 = cl.getTOT1()*48E-3;
        float tot2 = cl.getTOT2()*48E-3;

        int chL1 = ch%96;
        int chL2 = chL1 + dch;
        dt -= hchan->GetBinContent(ch+1) - hchan->GetBinContent(ch+1+dch);
        hcheck2->Fill(dt - htot[strip]->Interpolate(tot1 + chL1*1000*0) + htot[strip]->Interpolate(tot2 + chL2*1000*0));
      }
    }

    printf("Write\n");
    hcheck2->Write();
    hcheck->Write();
    for(int is=0; is < o2::tof::Geo::NSTRIPS; is++){
      if(htot[is]->GetEntries() > 100){
	htot[is]->Write();
      }
    }
    foutTOT->Close();
  }
  printf("DONE\n");
}

void readprevious(){
  TFile *f = new TFile("channel-all.root");
  hchan = (TH1F *) f->Get("hchan");
}

int fitstrip(bool onlytot=false, int stripsel=1306){
  TFile *f = new TFile("tofclusCalInfo.root");
  t = (TTree *) f->Get("o2sim");
  t->SetBranchAddress("TOFClusterCalInfo",&pv);

  if(! onlytot){
    printf("Fit Offset\n\n");
    fitoffset(0, stripsel);
  }
  else{
    readprevious();
  }
  printf("Fit TOT\n");
  fittot(onlytot, !onlytot);
  if(! onlytot){
    printf("Re-Fit Offset\n\n");
    fitoffset(1, stripsel);
  }
  else{
    printf("Fit TOT-2\n");
    fittot(onlytot, 1);
  }
  printf("Forcing exit\n");

  gROOT->Reset();
  return 0;
}

