void checkch(int ch){
  int strip = ch/96;
  int chLoc = ch%96;
  
  TFile *f1 = new TFile("outputCCDBfromOCDBor.root");
  o2::dataformats::CalibTimeSlewingParamTOF* mTimeSlewingObj = (o2::dataformats::CalibTimeSlewingParamTOF*) f1->Get("TimeSlewing");

  TFile *f2 = new TFile("tot.root");
  TProfile *htot = (TProfile *) f2->Get(Form("htot_%d",strip));

  TH1D *hnew = new TH1D("hnew","",30,0,30);
  TH1D *hnew2 = new TH1D("hnew2","",30,0,30);
  
  TH1D *hr2 = new TH1D("hr2",Form("channel %d;tot (ns); #Deltat",ch),30,0,30);
  hr2->SetLineColor(2);
  hr2->Reset();
  hnew2->SetLineColor(4);
  hnew2->SetMarkerColor(4);

  for(int i=1; i <= hr2->GetNbinsX(); i++){
  // float evalTimeSlewing(int channel, float tot) const
    float x = hr2->GetBinCenter(i);
    hr2->SetBinContent(i,mTimeSlewingObj->evalTimeSlewing(ch, x) - mTimeSlewingObj->evalTimeSlewing(ch, 10.5));

    hnew->SetBinContent(i, htot->GetBinContent(i + (chLoc+1)*50) - htot->GetBinContent(11 + (chLoc+1)*50));
    hnew->SetBinError(i, htot->GetBinError(i + (chLoc+1)*50));
    hnew2->SetBinContent(i, htot->GetBinContent(i) - htot->GetBinContent(11));
    hnew2->SetBinError(i, htot->GetBinError(i));
  }

  hr2->Draw();
  hr2->SetStats(0);
  hnew->Draw("SAME");
  hnew2->Draw("SAME");
  hr2->SetMaximum(600);
  hr2->SetMinimum(-1200);

  TLegend *leg = new TLegend(0.5,0.5,0.7,0.7);
  leg->AddEntry(hr2,"Run-2 cal","l");
  leg->AddEntry(hnew,"O2 cosmics (ch)","lp");
  leg->AddEntry(hnew,"O2 cosmics (strip)","lp");
  leg->SetFillStyle(0);
  leg->Draw("SAME");
}
