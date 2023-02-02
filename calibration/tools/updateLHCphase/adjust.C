void adjust(const char* fn, float cal){
  TFile *f = new TFile(fn);
  o2::dataformats::CalibLHCphaseTOF *obj = (o2::dataformats::CalibLHCphaseTOF *) f->Get("ccdb_object");

  o2::dataformats::CalibLHCphaseTOF objNew;

  for(int i=0; i < obj->size(); i++){
    int ts = obj->timestamp(i);
    float newval = obj->getLHCphase(ts) + cal;
    if(i==0) printf("old=%.1f new=%f\n",obj->getLHCphase(ts), newval);
    objNew.addLHCphase(ts, newval);
  }

  TFile *fout = new TFile(Form("updated_%s",fn),"RECREATE");
  fout->WriteObjectAny(&objNew, objNew.Class(), "ccdb_object");
  fout->Close();
}
