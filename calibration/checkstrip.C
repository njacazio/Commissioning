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

double MyFunc(double* x, double* params) {
  int i1 = int(x[0]+0.5)%96;
  int i2 = int(x[0]+0.5)/96 ? (i1 - 48) : (i1 - 1);
  
  if(i1 > 95) return 0;
  if(i2 < 0) return 0;
  if(int(x[0]+0.5) == 48) return 0;
  
  int i1row = i1%48;
  int i2row = i2%48;
  int row1 = i1/48;
  int row2 = i2/48;

  float d1 =  params[i1row];
  float d2 =  params[i2row];
  if(row1) d1 = params[i1row+48];
  if(row2) d2 = params[i2row+48];

  return (d1 - d2); 
}


void checkstrip(int strip){
  int ntotbin = 50;

  TF1 *ff = new TF1("fChanOffset",MyFunc,0,200,96);
  ff->SetNpx(1000);
  for(int i=0;i < 48;i++){
    ff->SetParLimits(i,-2000,2000);
  }
  for(int i=48;i < 96;i++){
    ff->SetParLimits(i,-2000,2000);
  }  
  ff->FixParameter(24,0);

  TFile *f = new TFile("tofclusCalInfo.root");
  f->ls();
  TTree *t = (TTree *) f->Get("o2sim");
  std::vector<o2::tof::CalibInfoCluster> v,*pv=&v;
  t->SetBranchAddress("TOFClusterCalInfo",&pv);

  TFile *fch = new TFile("channel-all.root");
  TH1F *hchan = (TH1F *) fch->Get("hchan");

  TFile *ftot = new TFile("tot.root");
  TProfile *htot = (TProfile *) ftot->Get(Form("htot_%d",strip));

  TH2F *h = new TH2F(Form("strip%d",strip),";pair;#Deltat (ps)",200,-0.5,199.5,200,-2000,2000);
  TH2F *ha = new TH2F(Form("strip%da",strip),";pair;#Deltat (ps)",200,-0.5,199.5,200,-2000,2000);
  TH2F *hb = new TH2F(Form("strip%db",strip),";pair;#Deltat (ps)",200,-0.5,199.5,200,-2000,2000);

  printf("start loop\n");
  int nentr = 0;
  for(int i=0; i < t->GetEntries(); i++){
    t->GetEvent(i);
    
    for(uint64_t j=0; j < v.size(); j++){
      o2::tof::CalibInfoCluster& cl = v[j];

      int ch = cl.getCH();
      int dch = cl.getDCH();
      int stripC = ch/96;

      if(stripC != strip) continue;
      double dt = cl.getDT();
      
      float tot1 = cl.getTOT1()*48.E-3;
      float tot2 = cl.getTOT2()*48.E-3;

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
      int chL1 = ch%96;
      int chL2 = chL1 + dch;
      int comb = 96*shift + chL1;

      dt -= hchan->GetBinContent(ch+1) - hchan->GetBinContent(ch+1+dch);
      dt -= htot->Interpolate(tot1 + (chL1+1)*ntotbin) - htot->Interpolate(tot2 + (chL2+1)*ntotbin);      

      h->Fill(comb, dt);
      if(tot1 > tot2) ha->Fill(comb, dt);
      else hb->Fill(comb, dt);

      nentr++;
    }    
  }
  int np=0;
  float x[200],y[200],ex[200],ey[200],dy[200],dey[200];
  TF1 *fg = new TF1("fg","gaus",-1000,1000);
  fg->SetParameter(0,1);
  fg->SetParameter(1,0);
  fg->SetParameter(2,100);
  TF1 *fg2 = new TF1("fg2","gaus",-1000,1000);
  fg2->SetParameter(0,1);
  fg2->SetParameter(1,0);
  fg2->SetParameter(2,100);

  for (int i=0; i < 200; i++){
    TH1D *htemp = ha->ProjectionY(Form("h%da",i),i+1,i+1);
    TH1D *htemp2 = hb->ProjectionY(Form("h%db",i),i+1,i+1);
    if(htemp->Integral() < 50 || htemp2->Integral() < 50) continue;
    htemp->Fit(fg,"WW");
    htemp2->Fit(fg2,"WW");
    x[np] = i;
    ex[np] = 0;
    y[np] = (fg->GetParameter(1) + fg2->GetParameter(1))*0.5;
    dy[np] = fg->GetParameter(1) - fg2->GetParameter(1);
    dey[np] = sqrt(fg->GetParError(1)*fg->GetParError(1) + fg2->GetParError(1)*fg2->GetParError(1));
    ey[np] = dey[np]*0.5;
    np++;
  }

  if(np < 96) return;
  
  TGraphErrors *gdelta = new TGraphErrors(np,x,dy,ex,dey);
  gdelta->SetMarkerStyle(20);
  TGraphErrors *g = new TGraphErrors(np,x,y,ex,ey);
  g->SetMarkerStyle(20);
  h->Draw("colz");
  new TCanvas;
  g->Draw("AP");
  g->Fit(ff,"");
  printf("Chi2 = %f\n",ff->GetChisquare()/ff->GetNDF());
  printf("strip %d -> %d entries\n",strip,nentr);
  new TCanvas;
  gdelta->Draw("AP");
  TH1F *hoffset = new TH1F("hoffset",";offset (ps);",100,-1000,1000);
  for(int i=0; i < 96;i++){
   hchan->SetBinContent(96*strip + i + 1, hchan->GetBinContent(96*strip + i + 1) + ff->GetParameter(i));
   hchan->SetBinError(96*strip + i + 1, ff->GetParError(i));
   if(i != 24)  hoffset->Fill(ff->GetParameter(i));
  }
  new TCanvas;
  hoffset->Draw();
  new TCanvas;
  ha->Draw("colz");
  new TCanvas;
  hb->Draw("colz");

  TFile *fout = new TFile("outOffset.root","RECREATE");
  hchan->Write();
  fout->Close();
}
