void checkPhase(const char* period="LHC22r"){
  TFile *f = new TFile(Form("FT0TOF_trending_%s_apass2.root",period));
  f->ls();
  TH1F *hDelta = (TH1F *) f->Get("trend_t0TOFFT0");
  TH1F *hTof = (TH1F *) f->Get("trend_t0TOF");

  hDelta->Add(hTof,-1);
  hDelta->Scale(-1);

  hDelta->SetLineColor(2);
  hDelta->SetMarkerColor(2);

  hTof->Draw("PL");
  hTof->SetMaximum(200);
  hTof->SetMinimum(-200);
  hDelta->Draw("PL,SAME");

  float thresholdTOF = 15;
  float thresholdFT0 = 50;

  FILE *fout = fopen(period,"w");
  for(int i=1; i<=hTof->GetNbinsX();i++){
    float tof = hTof->GetBinContent(i);
    bool badTOF = fabs(tof) > thresholdTOF;
    float ft0 = hDelta->GetBinContent(i);
    bool badFT0 = fabs(ft0) > thresholdFT0;

    if(badTOF){
      printf("%s problematic for TOF\n",hTof->GetXaxis()->GetBinLabel(i));
      fprintf(fout,"%s %.1f\n",hTof->GetXaxis()->GetBinLabel(i),tof);
    }
    if(badFT0){
      printf("%s problematic for FT0 -> notify FT0 group\n",hTof->GetXaxis()->GetBinLabel(i));
    }
  }
  fclose(fout);
}
