void makedef(){
  TFile *fCal = new TFile("newtsNew.root");
  o2::dataformats::CalibTimeSlewingParamTOF *ts = (o2::dataformats::CalibTimeSlewingParamTOF *) fCal->Get("ccdb_object");

  int chPerSec = 91*96;
  for(int i=0; i < o2::tof::Geo::NCHANNELS; i++){
    int sector = i / chPerSec;
    int ch = i % chPerSec;
    ts->setFractionUnderPeak(sector, ch, 0.99) ;
  }

  TFile *fsl = new TFile("TOF/Calib/ChannelCalib/default.root","RECREATE");
  fsl->WriteObjectAny(ts, ts->Class(), "ccdb_object");
  fsl->Close();

}
