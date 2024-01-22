void extractMap(){
  TFile *f = new TFile("QC.root");

  o2::quality_control::core::MonitorObjectCollection *mon = (o2::quality_control::core::MonitorObjectCollection *) f->Get("int/TOF/Digits");
  if(!mon){
    mon = (o2::quality_control::core::MonitorObjectCollection *) f->Get("TOF/Digits");
  }
  o2::quality_control::core::MonitorObject *mHitMap = (o2::quality_control::core::MonitorObject *) mon->FindObject("HitMapNoiseFiltered");
  TH2F *hObj = (TH2F *) mHitMap->getObject();

  TFile *fout = new TFile("hitmap.root","RECREATE");
  hObj->Write();
  fout->Close();
}
