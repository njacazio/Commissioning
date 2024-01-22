#include "DataFormatsTOF/Diagnostic.h"
#include "TChain.h"
#include "TFile.h"


float slotsize = 300; // in sec
int timeMargin = 180; // in sec
int sampling = 1;

void calibDia(int run){
  system("mkdir TOF");
  system("mkdir TOF/Calib");
  system("mkdir TOF/Calib/Diagnostic");
  system("ls skim_calib*|grep -v part >listacal");
  system("ls skim_calib*|awk -F\".root\" '{print $1}'|awk -F\"part\" '{print $2,$1\"part\"$2\".root\"}'|sort -n|awk '{print $2}' >>listacal");

  FILE *f = fopen("listacal","r");

  int nfile = 0;
  char namefile[300];

  TChain *t = new TChain("calibTOF");
  /*
  mTree = (TTree*)fin->Get("calibTOF");
  mCurrentEntry = 0;
  */
  
  while(fscanf(f,"%s",namefile) == 1){
    printf("adding %s\n",namefile);
    t->AddFile(namefile);
  }

  o2::tof::Diagnostic diaObj, *pDiaObj = &diaObj;
  t->SetBranchAddress("TOFDiaInfo", &pDiaObj);

  printf("Sorting indices...\n");

  std::vector<std::pair<int, unsigned long>> indices;
  for (unsigned long i = 0; i < t->GetEntries(); i+=sampling) { // check time order inside the tree
    t->GetEvent(i);
    const auto& info = diaObj.getTFIDInfo();
    indices.push_back(std::make_pair(i, info.tfCounter));
  }
  std::sort(indices.begin(), indices.end(),
	    [&](const auto& a, const auto& b) {
	      return a.second < b.second;
	    });

  printf("...done\n");

  printf("Processing Diagnostic...\n");
  double cts=-1;
  double ts;
  o2::tof::Diagnostic *cslot = nullptr;

  int nslot = 0;
  
  for (unsigned long i = 0; i < t->GetEntries(); i++) { // check time order inside the tree
    if(!(i%10000)){
      printf("status: %lu/%lld\n",i,t->GetEntries());
    }
    t->GetEvent(indices[i].first);
    const auto& info = diaObj.getTFIDInfo();
    ts = info.creation*0.001;
    
    if(ts > cts + slotsize){
      if(nslot == 1){ // add margin
	cts -= timeMargin;
      }
      // new slot
      if(cts > 0){ // close previous slot
	TFile *fout = new TFile(Form("TOF/Calib/Diagnostic/dia_%d_%.0f_%.0f.root",run,cts,ts+timeMargin),"RECREATE");
	
	fout->WriteObjectAny(cslot, cslot->Class(), "ccdb_object");
	fout->Close();
	printf("Closing current slot %.0f %.0f -> %s\n",cts,ts+timeMargin,Form("TOF/Calib/Diagnostic/dia_%d_%.0f_%.0f.root",run,cts,ts+timeMargin));
	cslot->print(true);
      }
      cts = ts;
      nslot++;
      printf("Opening a new slot (%d) at %.0f\n",nslot,ts);
      cslot = new o2::tof::Diagnostic;
    }

    // add
    const auto& vec = diaObj.getVector();
    for (auto const& el : vec) {
      cslot->fill(el.first, el.second);
    }
  }
  
  printf("...done\n");
}
