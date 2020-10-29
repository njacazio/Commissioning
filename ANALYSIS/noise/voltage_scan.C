#include "style.C"
//TString outputdir = "/home/neelima/Desktop/commisionning/20201021_noise_scan/results/";
TString outputdir = "/home/preghenella/cernbox/ALICE/TOF/Commissioning2020/20201021_noise_scan/results";
const int nruns   = 30;
int run[nruns]    = {42, 43, 44, 45, 46, 47, 48, 51, 52, 54, 55, 56, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 71, 72, 73, 74, 75, 76, 77, 78}; 
int hv[nruns]     = {13000, 13000, 13000, 13000, 13000, 13000, 12750, 12750, 12750, 12750, 12750, 12750, 12500, 12500, 12500, 12500, 12500, 12500, 12250, 12250, 12250, 12250, 12250, 12250, 12000, 12000, 12000, 12000, 12000, 12000};
int thr[nruns]    = {1000, 900, 800, 700, 600, 500, 1000, 900, 800, 700, 600, 500, 1000, 900, 800, 700, 600, 500, 1000, 900, 800, 700, 600, 500, 1000, 900, 800, 700, 600, 500};

int normaliseTo = -1;
bool fitPol2 = false;

std::pair<double,double>
rate_value(int run, int sector, int strip, int fea) 
{
  auto fin = TFile::Open(Form("%s/noise_map.%d.root", outputdir.Data(), run));
  if (sector == -1) {
    auto f = (TF1*)gROOT->GetFunction("gaus");
    auto hFeaNoiseDist = (TH1 *)fin->Get("hFeaNoiseDist");
    hFeaNoiseDist->Fit(f, "0q", "", 0., 1.0);
    auto rate = f->GetParameter(1);
    auto ratee = f->GetParError(1);
    //    auto rate = hFeaNoiseDist->GetMean();
    //    auto ratee = hFeaNoiseDist->GetMeanError();
    return {rate,ratee};  }
  auto hFeaStripNoise = (TH2 *)fin->Get("hFeaNoise");
  // fea = 3 - fea; // filling is 3,2,1,0 on histogram
  auto rate = hFeaStripNoise->GetBinContent(4 * sector + fea + 1, strip + 1);
  auto ratee = hFeaStripNoise->GetBinError(4 * sector + fea + 1, strip + 1);
  return {rate,ratee}; 
}

void
voltage_scan(int sector = 4, int strip = 44, int fea = 2)
{
  style();
  int color[5] = {kRed+1, kOrange-3, kYellow+2, kGreen+2, kAzure-3};
  TGraphErrors* fea_Noise[5];
  TGraph2DErrors* fea_Noise_2D = new TGraph2DErrors();

  std::pair<double,double> normalise_rate = {1., 1.};
  if (normaliseTo != -1) normalise_rate = rate_value(run[normaliseTo], sector, strip, fea);
  std::cout << " normalise rate = " << normalise_rate.first << std::endl;
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
      fea_Noise[i]->SetPoint(j, thr[irun], rate.first / normalise_rate.first);
      fea_Noise[i]->SetPointError(j, 0., rate.second / normalise_rate.first);

      fea_Noise_2D->SetPoint(irun, hv[irun], thr[irun], rate.first / normalise_rate.first );
      fea_Noise_2D->SetPointError(irun, 0., 0., rate.second / normalise_rate.first);
    }
  } 

  auto f2d = new TF2("f2d", "[0] + [1] * (x - 13000.) + [2] * (x - 13000.) * (x - 13000.) + [3] * (y - 500.) + [4] * (y - 500.) * (y - 500.)");
  f2d->SetParameter(0, 0.5);
  if (normaliseTo != -1) f2d->SetParameter(0, 1.);
  f2d->FixParameter(2, 0.);
  f2d->FixParameter(4, 0.);
  fea_Noise_2D->Fit(f2d, "0");
  if (fitPol2) {
    f2d->ReleaseParameter(2);
    fea_Noise_2D->Fit(f2d, "0");
    f2d->ReleaseParameter(4);
    fea_Noise_2D->Fit(f2d, "0");
  }
  
  auto f1d = new TF1("f1d", "[0] + [1] * ([5] - 13000.) + [2] * ([5] - 13000.) * ([5] - 13000.) + [3] * (x - 500.) + [4] * (x - 500.) * (x - 500.)", 400., 1100.);
  f1d->SetLineStyle(kDashed);
  for (int i = 0; i < 5; ++i)
    f1d->SetParameter(i, f2d->GetParameter(i));
  
  auto c = new TCanvas("c", "c", 800, 800);
  
  if (normaliseTo == -1) c->DrawFrame(400., 0., 1100., 1., ";THR (mV);noise rate (Hz/channel)");
  else c->DrawFrame(400., 0., 1100., 2., ";THR (mV);normalised noise rate");
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

  gROOT->ProcessLine(Form(".! mkdir -p %s", outputdir.Data()));
  if (normaliseTo == -1)
    { c->SaveAs(Form("%s/Sector%d_Strip%d_Fea%d_normalisation1.png",outputdir.Data(), sector, strip, fea));}
  else
    c->SaveAs(Form("%s/Sector%d_Strip%d_Fea%d_normalisation%d.png",outputdir.Data(), sector, strip, fea, normaliseTo));
  new TCanvas;
  fea_Noise_2D->Draw("surf");
  
}
