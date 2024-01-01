{
  int ch=1008;//76869;
  TFile *_file0 = TFile::Open("newtsNew.root");
  TFile *_file1 = TFile::Open("TOF/Calib/ChannelCalib/snapshot.root");
  o2::dataformats::CalibTimeSlewingParamTOF *a = (o2::dataformats::CalibTimeSlewingParamTOF *) _file0->Get("ccdb_object");
  o2::dataformats::CalibTimeSlewingParamTOF *b = (o2::dataformats::CalibTimeSlewingParamTOF *) _file1->Get("ccdb_object");
  TH1F *h = new TH1F("h","",1000,0,100);
  TH1F *h2 = new TH1F("h2","",1000,0,100);
  h2->SetLineColor(2);
  for(int i=1; i <= 1000; i++){
    h->SetBinContent(i, a->evalTimeSlewing(ch,h->GetBinCenter(i)) - a->getChannelOffset(ch)*0);
    h2->SetBinContent(i, b->evalTimeSlewing(ch,h2->GetBinCenter(i)) - b->getChannelOffset(ch)*0);
  }
  h->Draw();
  h2->Draw("SAME");
}
