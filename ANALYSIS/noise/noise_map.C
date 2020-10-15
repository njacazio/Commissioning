
TH1*
noise_map(const char *fname, double max_noise = 1.e3 /* [Hz] */)
{
  auto fin           = TFile::Open(fname);
  auto hRuns         = (TH1 *)fin->Get("hRuns");
  auto hTimeWin      = (TH1 *)fin->Get("hTimeWin");
  auto hCrateCounter = (TH1 *)fin->Get("hCrateCounter");
  auto hIndexCounter = (TH1 *)fin->Get("hIndexCounter");

  
  TH2D *hStripNoise     = new TH2D("hStripNoise", ";sector;strip", 18, 0., 18., 91, 0., 91.);
  TH1D *hIndexNoiseFlag = new TH1D("hIndexNoiseFlag",";;channel index", 172800, 0, 172800);
  TH1D *hStripNoiseDist = new TH1D("hStripNoiseDist",";noise rate (Hz/channel)", 10000, 0, 100);
  TH2D *hFeaStripNoise  = new TH2D("hFeaStripNoise", ";sector;strip", 72, 0., 18., 91, 0., 91);
  TH1D *hFeaNoiseDist   = new TH1D("hFeaNoiseDist",";noise rate (Hz/channel)", 10000, 0, 100);
   
  double tdc_width = 24.3660e-12; // [s]
  auto time_window = hTimeWin->GetBinContent(1) / hRuns->GetBinContent(1) * tdc_width;
 
  int StripCounter[18][91]            = {0};
  int FeaCounter[18][91][4]           = {0};
  double IntegratedTime[18][91]       = {0.};
  double IntegratedTimeFea[18][91][4] = {0.};
 
  auto hIndexNoise = (TH1 *)hIndexCounter->Clone("hIndexNoise");
  for (int i = 0; i < 172800; ++i) {
    auto count  = hIndexNoise->GetBinContent(i + 1);
    auto counte = sqrt(count);
    auto icrate = i / 2400;
    auto iTRM   = i / 240;
    auto itime  = hCrateCounter->GetBinContent(icrate + 1) * time_window;

    // start measure time from 1 micro second
    if (itime < 1.e-6) continue;
    if (count == 0) continue; // check if this channel was active
    
    //  auto eIndex = o2::tof::Geo::getECHFromIndexes(drmID, trmID, chain, tdcID, channel);
    // how is the detector index defined?
    // TOF has 18 sectors
    // one sector has 91 strip; total 1638 strip
    // one strip has 96 channels; total 157248 channels
    // 157248 [0-157247]
    //
    // one has to know how the channels are arranged in the strip
    // the strip has two rows (padz = [0-1])
    // one row has 48 channels (padx = [0-47)

    // one of the smartest way to plot stuff that is
    // good both in terms of electornics
    // and in terms of the detector is to
    // make plots of the FEA cards
    // because there is no way that a FEA can be half on / half off 

    // make a 2D plot that will give a graphical representation of how
    // actually TOF is
    // x axis, sector
    // y axis, the strip
    
    auto rate  = (float)count / itime;
    auto ratee =  counte / itime ;
    hIndexNoise->SetBinContent(i + 1, rate);
    hIndexNoise->SetBinError(i + 1, ratee);

    if (rate > max_noise) continue;

    int crate    = i / 2400;
    int crate_   = i % 2400;
    int slot     = crate_ / 240;
    int slot_    = crate_ % 240;
    int chain    = slot_ / 120;
    int chain_   = slot_ % 120;
    int tdc      = chain_ / 8;
    int tdc_     = chain_ % 8;
    int channel  = tdc_ ;
   
      
    auto eIndex  = o2::tof::Geo::getECHFromIndexes(crate, slot + 3, chain, tdc, channel);
    auto dIndex  = o2::tof::Geo::getCHFromECH(eIndex);
    if (dIndex < 0) continue;
    auto sector  = dIndex / 8736;
    auto sector_ = dIndex % 8736;
    auto strip   = sector_ / 96;
    auto strip_  = sector_ % 96;
    auto strrow  = strip_ / 48;
    auto strrow_ = strip_ % 48; 
    auto fea     = strrow_ / 12;
    
    
    //  std::cout << "  strip: " << strip << "  strip row: "<< strrow << "  fea: "<< fea <<  std::endl;
    
    StripCounter[sector][strip]           += count;
    IntegratedTime[sector][strip]         += itime;
    FeaCounter[sector][strip][fea]        += count;
    IntegratedTimeFea[sector][strip][fea] += itime;
  }

  for (int isector = 0; isector < 18; isector++){
    for (int istrip = 0; istrip < 91; istrip++){
      auto count = StripCounter[isector][istrip];
      auto itime = IntegratedTime[isector][istrip];
      
      if (itime < 1.e-6) continue;
      
      auto rate  = (float)count / itime;
      auto ratee =  sqrt(count) / itime ;
      
      //if (rate > 100) continue;
      
      hStripNoise->SetBinContent(isector + 1, istrip + 1, rate);
      hStripNoise->SetBinError(isector + 1, istrip + 1, ratee);
      hStripNoiseDist->Fill(rate);

      
      for (int iFea = 0; iFea < 4; iFea++){

	auto countFea = FeaCounter[isector][istrip][iFea];
	auto itimeFea = IntegratedTimeFea[isector][istrip][iFea];
	if (itimeFea < 1.e-6) continue;
	auto rateFea  = (float)countFea / itimeFea;
	auto rateeFea =  sqrt(countFea) / itimeFea;
    	
	hFeaStripNoise->SetBinContent(isector * 4 + (3 - iFea) + 1, istrip + 1, rateFea);
	hFeaStripNoise->SetBinError(isector * 4 + (3 - iFea) + 1, istrip + 1, rateeFea);
	hFeaNoiseDist->Fill(rateFea);
     
      }
    } 
  }


  // hIndexNoise->Draw();
  TCanvas *cStripNoise = new TCanvas("cStripNoise","cStripNoise", 1000, 1600);
  cStripNoise->cd();
  cStripNoise->SetLogz();
  hStripNoise->SetStats(0);
  hStripNoise->SetMaximum(10.);
  hStripNoise->SetMinimum(0.1);
  hStripNoise->Draw("colz");

  TCanvas *cFeaStripNoise = new TCanvas("cFeaStripNoise","cFeaStripNoise", 1000, 1600);
  cFeaStripNoise->cd();
  cFeaStripNoise->SetLogz();
  hFeaStripNoise->SetStats(0);
  hFeaStripNoise->SetMaximum(10.);
  hFeaStripNoise->SetMinimum(0.1);
  hFeaStripNoise->Draw("colz");

  TCanvas *cNoiseDist = new TCanvas("cNoiseDist","cNoiseDist", 800, 800);
  cNoiseDist->cd();
  cNoiseDist->SetLogx();
  hFeaNoiseDist->SetStats(0);
  hFeaNoiseDist->SetLineColor(kRed+2);
  hFeaNoiseDist->SetLineWidth(2);
  hFeaNoiseDist->Draw();
  hStripNoiseDist->SetLineWidth(2);
  hStripNoiseDist->Draw("same");

  TLegend *leg = new TLegend(0.2, 0.6,0.4, 0.7);
  leg->AddEntry(hFeaNoiseDist, "Fea noise");
  leg->AddEntry(hStripNoiseDist, "Strip noise");
  leg->SetBorderSize(0);
  leg->Draw("same");

  TFile *fout = new TFile("noise_map.root", "RECREATE");
  fout->cd();
  
  hStripNoise->Write();
  hFeaStripNoise->Write("hFeaNoise");
  hStripNoiseDist->Write();
  hFeaNoiseDist->Write();
  fout->Close();
  
  return hStripNoiseDist;
  
}
