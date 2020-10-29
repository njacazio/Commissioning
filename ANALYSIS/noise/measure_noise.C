double tdc_width = 24.3660e-12; // [s]

double max_noise = 1.e3; // [Hz]

void
measure_noise(const char *fname)
{
  auto fin = TFile::Open(fname);
  auto hRuns = (TH1 *)fin->Get("hRuns");
  auto hTimeWin = (TH1 *)fin->Get("hTimeWin");
  auto hCrateCounter = (TH1 *)fin->Get("hCrateCounter");
  auto hIndexCounter = (TH1 *)fin->Get("hIndexCounter");
  
  int crate_count[72] = {0};
  int TRM_count[720]  = {0};

  auto time_window = hTimeWin->GetBinContent(1) / hRuns->GetBinContent(1) * tdc_width;
  
  auto hIndexNoise = (TH1 *)hIndexCounter->Clone("hIndexNoise");
  for (int i = 0; i < 172800; ++i) {
    auto count = hIndexNoise->GetBinContent(i + 1);
    auto counte = sqrt(count);
    auto icrate = i / 2400;
    auto iTRM   = i / 240;
    auto itime = hCrateCounter->GetBinContent(icrate + 1) * time_window;

    if (itime < 1.e-6) continue;
    
    crate_count[icrate] += count;
    TRM_count[iTRM] += count;
    
    auto rate = (float)count / itime;
    auto ratee =  counte / itime ;

    hIndexNoise->SetBinContent(i + 1, rate);
    hIndexNoise->SetBinError(i + 1, ratee);
  }

  auto hCrateNoise = new TH1F("hCrateNoise", "", 72, 0., 72.);
  for (int i = 0; i < 72; ++i) {
    auto rate = crate_count[i];
    auto ratee = sqrt(crate_count[i]);
    auto itime = hCrateCounter->GetBinContent(i + 1) * time_window;

    if (itime < 1.e-6) continue;

    rate /= itime;
    ratee /= itime;
    hCrateNoise->SetBinContent(i + 1, rate);
    hCrateNoise->SetBinError(i + 1, ratee);
  }

  auto hTRMNoise = new TH1F("hTRMNoise", "", 720, 0., 720.);
  
  for (int i = 0; i < 720; ++i){
    auto rate = TRM_count[i];
    auto ratee = sqrt(TRM_count[i]);
    auto icrate = i / 10;
    auto itime = hCrateCounter->GetBinContent(icrate + 1) * time_window;

    if (itime < 1.e-6) continue;

    rate /= itime;
    ratee /= itime;
    hTRMNoise->SetBinContent(i+1, rate);
    hTRMNoise->SetBinError(i+1, ratee);
  }

  hIndexNoise->Draw();
  
}
