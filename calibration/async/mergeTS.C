void mergeTS(){
  FILE *f = fopen("lista","r");

  int nfiles=0;
  char nfile[18][300];
  
  while(fscanf(f,"%s",nfile[nfiles]) == 1){
    nfiles++;
  }

  if(!nfiles){
    return;
  }
  
  o2::dataformats::CalibTimeSlewingParamTOF* ts[18];

  for(int i=0; i < nfiles; i++){
    TFile *ff = new TFile(nfile[i]);
    ts[i] = (o2::dataformats::CalibTimeSlewingParamTOF*) ff->Get("ccdb_object");
  }

  for(int i=1; i < nfiles; i++){
    *(ts[0]) += *(ts[i]);
  }

  
  TFile *fsl = new TFile("merged.root","RECREATE");
  fsl->WriteObjectAny(ts[0], ts[0]->Class(), "ccdb_object");
  fsl->Close();
  
}
