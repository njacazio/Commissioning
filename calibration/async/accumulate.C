int sampling=1;

TF1 *func;

const int MAXPERCH = 2000;

std::vector<o2::dataformats::CalibInfoTOFshort> vecOut[o2::tof::Geo::NCHANNELS];
int mult[o2::tof::Geo::NCHANNELS],nmax=0;

void write(int run, int instance);
void reset(){
  nmax = 0;
  for(int i=0; i < o2::tof::Geo::NCHANNELS; i++){
    mult[i] = 0;
    vecOut[i].clear();
  }
}

void accumulate(int run, long start, long end){
  TFile *fPhase = new TFile(Form("TOF/Calib/LHCphase/o2-dataformats-CalibLHCphaseTOF_%d_%ld_%ld.root",run,start,end));
  o2::dataformats::CalibLHCphaseTOF *calPhase = (o2::dataformats::CalibLHCphaseTOF *) fPhase->Get("ccdb_object");

  reset();
  
  system(Form("ls %d/skim*root >listAcc%d",run,run));

  TChain *t = new TChain("calibTOF","calibTOF");
  FILE *fin = fopen(Form("listAcc%d",run),"r");
  char namefile[300];
  while(fscanf(fin,"%s",namefile) == 1){
    t->AddFile(namefile);
  }
  std::vector<o2::dataformats::CalibInfoTOF> vec, *pVec = &vec;
  t->SetBranchAddress("TOFCalibInfo", &pVec);

  int inst = 0;
  
  for(int k=0; k < t->GetEntries(); k+=1000*sampling){
    for(int i=k; i < k+1000;i++){
      t->GetEvent(i);
      for(const auto& obj : vec){
	int ch = obj.getTOFChIndex();
	int ts = obj.getTimestamp();
	float tot = obj.getTot();
	float dt = obj.getDeltaTimePi() - calPhase->getLHCphase(ts);

	vecOut[ch].emplace_back(ts, dt, tot, obj.getMask(), obj.getFlags());

	mult[ch]++;
	if(mult[ch] > nmax){
	  nmax = mult[ch];
	}

	if(nmax > MAXPERCH){
	  write(run, inst);
	  inst++;
	}
      }
    }
  }
}

void write(int run, int instance){

  TFile *fout = new TFile(Form("accumulated/%d_%d.root",run,instance),"RECREATE");
  TTree *tout = new TTree("treeCollectedCalibInfo","treeCollectedCalibInfo");
  std::vector<o2::dataformats::CalibInfoTOFshort> *pointer;
  tout->Branch("TOFCollectedCalibInfo",&pointer);

  for(int i=0; i < o2::tof::Geo::NCHANNELS; i++){
    pointer = &(vecOut[i]);
    tout->Fill();
  }

  tout->Write();
  fout->Close();
  reset();
}
