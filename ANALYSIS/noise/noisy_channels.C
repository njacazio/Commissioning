void print_noisy_channel(int i, std::ofstream &fout)
{
  int sm = i / 9600;
  int sm_ = i % 9600; 
  int link = sm_ / 2400;
  int link_ = sm_ % 2400;
  int slot = link_ / 240;
  int slot_ = link_ % 240;
  int chain = slot_ / 120;
  int chain_ = slot_ % 120;
  int chip = chain_ / 8;
  int chip_ = chain_ % 8;
  int channel = chip_ ;
  fout << sm <<  " " << link << " " << slot + 3 << " " << chain << " " << chip << " " << channel << std::endl;
}

void
noisy_channels(const char *fname, double max_noise = 1.e3 /* [Hz] */)
{
  auto fin = TFile::Open(fname);
  auto hRuns = (TH1 *)fin->Get("hRuns");
  auto hTimeWin = (TH1 *)fin->Get("hTimeWin");
  auto hCrateCounter = (TH1 *)fin->Get("hCrateCounter");
  auto hIndexCounter = (TH1 *)fin->Get("hIndexCounter");

  double tdc_width = 24.3660e-12; // [s]
  auto time_window = hTimeWin->GetBinContent(1) / hRuns->GetBinContent(1) * tdc_width;
  
  std::ofstream fout;
  fout.open("noisy_channels.txt", std::ios::out);
  
  auto hIndexNoise = (TH1 *)hIndexCounter->Clone("hIndexNoise");
  for (int i = 0; i < 172800; ++i) {
    auto count = hIndexNoise->GetBinContent(i + 1);
    auto counte = sqrt(count);
    auto icrate = i / 2400;
    auto iTRM   = i / 240;
    auto itime = hCrateCounter->GetBinContent(icrate + 1) * time_window;

    if (itime < 1.e-6) continue;
    
    auto rate = (float)count / itime;
    auto ratee =  counte / itime ;
    hIndexNoise->SetBinContent(i + 1, rate);
    hIndexNoise->SetBinError(i + 1, ratee);
    if (rate < max_noise) continue;
    print_noisy_channel(i, fout);
  }

  fout.close();

  auto c = new TCanvas("c", "c", 800, 800);
  c->SetLogy();
  auto hframe = c->DrawFrame(0., 0.1, 172800., 100.e6, ";channel index;rate (Hz)");
  hframe->GetXaxis()->SetMaxDigits(6);
  hIndexNoise->SetMarkerStyle(24);
  hIndexNoise->SetMarkerSize(0.8);
  hIndexNoise->Draw("same");

  TLine line;
  line.SetLineStyle(kDashed);
  line.DrawLine(0., 1.e3, 172800., 1.e3);
  
}
