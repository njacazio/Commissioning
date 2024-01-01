void check(int run=544013){
  TFile *_file0 = TFile::Open(Form("TOF/Calib/ChannelCalib/%d_ts.root",run));
  o2::dataformats::CalibTimeSlewingParamTOF *a = (o2::dataformats::CalibTimeSlewingParamTOF *) _file0->Get("ccdb_object");

  TH1F *hSigmaPeak = new TH1F("hSigmaPeak","GOOD channels;#sigma_{peak} (ps)",100,0,500);
  TH1F *hFrPeak = new TH1F("hFrPeak","GOOD channels;Fraction under peak",100,0,1);
  TH2F *hFrSigmaPeak = new TH2F("hFrSigmaPeak","GOOD channels;Fraction under peak;#sigma_{peak} (ps)",50,0,1,50,0,500);
  TH1F *hChOffset = new TH1F("hChOffset","GOOD channels;ChOffset (ps)",1000,-100000,100000);
  
  int noacc = - (96 * 15 * 3);
  int nbad = - (96 * 15 * 3);
  int ngood = 0;
  int nreal = o2::tof::Geo::NCHANNELS - (96 * 15 * 3);
  for(int i=0; i < o2::tof::Geo::NCHANNELS; i++){
    if(a->isProblematic(i)){
      if(fabs(a->getSigmaPeak(i)) < 1E-6){
	noacc++;
      }
      nbad++;
    } else {
      hSigmaPeak->Fill(a->getSigmaPeak(i));
      hFrPeak->Fill(a->getFractionUnderPeak(i));
      hFrSigmaPeak->Fill(a->getFractionUnderPeak(i),a->getSigmaPeak(i));
      hChOffset->Fill(a->getChannelOffset(i));
      ngood++;
    }
  }
  printf("Noff = %d (%.1f%c), Nproblematic= %d (%.1f%c), Ngood = %d of %d (%.1f%c)\n",noacc,noacc*1./nreal*100,'%',nbad-noacc,(nbad-noacc)*1./nreal*100,'%',ngood,nreal,ngood*1./nreal*100,'%');

  new TCanvas;
  hChOffset->Draw();
  new TCanvas;
  hSigmaPeak->Draw();
  new TCanvas;
  hFrPeak->Draw();
  TCanvas *c = new TCanvas;
  c->SetLogz();
  hFrSigmaPeak->Draw("colz");

  TFile *fo = new TFile(Form("ts_check_%d.root",run),"RECREATE");
  hChOffset->Write();
  hSigmaPeak->Write();
  hFrPeak->Write();
  hFrSigmaPeak->Write();
  fo->Close();
  
}
