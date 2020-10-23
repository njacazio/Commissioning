#include "style.C"
TString outputdir = "/home/neelima/Desktop/commisionning/20201021_noise_scan/results/";
const int nruns   = 30;
int run[nruns]    = {42, 43, 44, 45, 46, 47, 48, 51, 52, 54, 55, 56, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 71, 72, 73, 74, 75, 76, 77, 78}; 
int hv[nruns]     = {13000, 13000, 13000, 13000, 13000, 13000, 12750, 12750, 12750, 12750, 12750, 12750, 12500, 12500, 12500, 12500, 12500, 12500, 12250, 12250, 12250, 12250, 12250, 12250, 12000, 12000, 12000, 12000, 12000, 12000};
int thr[nruns]    = {1000, 900, 800, 700, 600, 500, 1000, 900, 800, 700, 600, 500, 1000, 900, 800, 700, 600, 500, 1000, 900, 800, 700, 600, 500, 1000, 900, 800, 700, 600, 500};

std::pair<double,double>
rate_value(int run, int sector, int strip, int fea) 
{
  auto fin = TFile::Open(Form("%s/noise_map.%d.root", outputdir.Data(), run));
  if (sector == -1) {
    auto hFeaNoiseDist = (TH1 *)fin->Get("hFeaNoiseDist");
    auto rate = hFeaNoiseDist->GetMean();
    auto ratee = hFeaNoiseDist->GetMeanError();
    return {rate,ratee};  }
  auto hFeaStripNoise = (TH2 *)fin->Get("hFeaNoise");
  // fea = 3 - fea; // filling is 3,2,1,0 on histogram
  auto rate = hFeaStripNoise->GetBinContent(4 * sector + fea + 1, strip + 1);
  auto ratee = hFeaStripNoise->GetBinError(4 * sector + fea + 1, strip + 1);
  return {rate,ratee}; 
}

void
voltage_scan(int sector = 4, int strip = 44, int fea = 1)
{
  style();
  int color[5] = {kRed+1, kOrange-3, kYellow+2, kGreen+2, kAzure-3};
  TGraphErrors* fea_Noise[5];
  TGraph2DErrors* fea_Noise_2D = new TGraph2DErrors();
  for (int i = 0; i < 5; i++){
    fea_Noise[i] = new TGraphErrors();
    fea_Noise[i]->SetMarkerStyle(20); 
    fea_Noise[i]->SetMarkerSize(1.5);
    fea_Noise[i]->SetMarkerColor(color[i]);
    fea_Noise[i]->SetLineColor(color[i]);
    fea_Noise[i]->SetLineWidth(2);
    for (int j = 0; j < 6; j++){
      auto irun = 6*i+j;
      auto rate = rate_value(run[irun], sector, strip, fea);
      fea_Noise[i]->SetPoint(j, thr[irun], rate.first);
      fea_Noise[i]->SetPointError(j, 0., rate.second);

      fea_Noise_2D->SetPoint(irun, hv[irun], thr[irun], rate.first);
      fea_Noise_2D->SetPointError(irun, 0., 0., rate.second);
    }
  } 

  auto f2d = new TF2("f2d", "[0] + ([1] * x + [2] * x * x + [3] * y + [4] * y * y)");
  f2d->FixParameter(2, 0.);
  f2d->FixParameter(4, 0.);
  fea_Noise_2D->Fit(f2d, "0");
  f2d->ReleaseParameter(2);
  fea_Noise_2D->Fit(f2d, "0");
  f2d->ReleaseParameter(4);
  fea_Noise_2D->Fit(f2d, "0");

  
  auto f1d = new TF1("f1d", "[0] + ([1] * [5] + [2] * [5] * [5] + [3] * x + [4] * x * x)", 400., 1100.);
  f1d->SetLineStyle(kDashed);
  for (int i = 0; i < 5; ++i)
    f1d->SetParameter(i, f2d->GetParameter(i));
  
  auto c = new TCanvas("c", "c", 800, 800);
 
  c->DrawFrame(400., 0., 1100., 1., ";THR (mV);noise rate (Hz/channel)");
  TLegend *leg = new TLegend(0.22, 0.65, 0.45, 0.9);
  leg->SetTextSize(0.04);
  leg->SetBorderSize(0);
  leg->SetHeader("HV (V)");
  for (int i = 0; i < 5; i++){
    fea_Noise[i]->Draw("pcsame");
    f1d->SetParameter(5, hv[i*6]);
    f1d->SetLineColor(color[i]);
    f1d->DrawCopy("same");
    leg->AddEntry(fea_Noise[i], Form("%d", hv[i*6]));
    
   
  }
  
  leg->Draw("same");
  new TCanvas;
  fea_Noise_2D->Draw("surf");
  
}
