void prepareRun(int run=544392, int jira=4546){
  system(Form("cat ../listaRuns |grep %d >input1",run));

  int irun;
  long start,stop;

  FILE *f1 = fopen("input1","r");
  int nread = fscanf(f1,"%d %ld %ld",&irun,&start,&stop);
  if(nread < 3){
    printf("Problem with input1\n");
    return;
  }
  printf("%d) %d %ld %ld\n",run,irun,start,stop);

  system(Form("ls ../TOF/Calib/LHCphase/*|grep _%d_ >input2",run));
  FILE *f2 = fopen("input2","r");
  char namefile[400];
  nread = fscanf(f2,"%s",namefile);
  if(nread < 1){
    printf("Problem with input2\n");
    return;
  }
  printf("input: %s\n",namefile);
  TFile *fin = new TFile(namefile);
  o2::dataformats::CalibLHCphaseTOF *phase = (o2::dataformats::CalibLHCphaseTOF *) fin->Get("ccdb_object");
  int size = phase->size()-1;
  printf("N slot = %d\n",size);
  
  system(Form("echo \"\\n# Run %d -> LHCphase\" >>com",run));
  o2::dataformats::CalibLHCphaseTOF *newphase;

  for(int i=0; i < size; i++){
    long startSlot = phase->timestamp(i);
    long stopSlot = phase->timestamp(i+1);
    startSlot *= 1000;
    stopSlot *= 1000;
    
    if(i==0 && startSlot > start){
      startSlot = start;

      printf("ADJUSTING START!!!!!!\n");
      printf("%ld -> start\n",start);
    } else if(i==0) {
      start = startSlot;
      printf("%ld -> start\n",start);
    }
    
    if(i==size-1 && stopSlot < stop){
      stopSlot = stop;
      printf("ADJUSTING STOP!!!!!!\n");
    } else if(i==size-1) {
      stop = stopSlot;
    }  

    newphase = new o2::dataformats::CalibLHCphaseTOF;
    newphase->addLHCphase(0, phase->LHCphase(i));
    newphase->addLHCphase(1999999999, phase->LHCphase(i));
    newphase->setStartValidity(startSlot);
    newphase->setEndValidity(stopSlot);
    printf("%ld %ld %f -> %s\n",startSlot,stopSlot,phase->LHCphase(i),Form("TOF/Calib/LHCphase/o2-dataformats-CalibLHCphaseTOF_%d_%ld_%ld.root",run,startSlot,stopSlot));

    TFile *fout = new TFile(Form("TOF/Calib/LHCphase/o2-dataformats-CalibLHCphaseTOF_%d_%ld_%ld.root",run,startSlot,stopSlot),"RECREATE");
    fout->WriteObjectAny(newphase, "o2::dataformats::CalibLHCphaseTOF", "ccdb_object");
    fout->Close();

    system(Form("echo \"o2-ccdb-upload --host \\\"$ ccdbhost\\\" -p TOF/Calib/LHCphase -f %s -k ccdb_object --starttimestamp %ld --endtimestamp %ld -m \\\"adjustableEOV=true;runNumber=%d;JIRA=[O2-%d];\\\"\" >> com",Form("TOF/Calib/LHCphase/o2-dataformats-CalibLHCphaseTOF_%d_%ld_%ld.root",run,startSlot,stopSlot),startSlot,stopSlot,run,jira));
  }
  system(Form("echo \"\\n# Run %d -> ChannelCalib\" >>com",run));
  system(Form("echo \"o2-ccdb-upload --host \\\"$ ccdbhost\\\" -p TOF/Calib/ChannelCalib -f %s -k ccdb_object --starttimestamp %ld --endtimestamp %ld -m \\\"adjustableEOV=true;runNumber=%d;JIRA=[O2-%d];\\\"\" >> com",Form("TOF/Calib/ChannelCalib/%d_ts.root",run),start,stop,run,jira));

  printf("%ld -> stop\n",stop);



  
}
