/*

  Simple macro to read info from OADB file TOFPIDParams.root

  @P. Antonioli / INFN - BO

*/

#include "AliOADBContainer.h"
#include "AliTOFPIDParams.h"

AliTOFPIDParams* tofPar = nullptr;
TString readTOFparams(Int_t run,
    const char* pass,
    const char* oadbfile = "$ALICE_PHYSICS/OADB/COMMON/PID/data/TOFPIDParams.root")

{
  TString fname = Form("%s", oadbfile);

  TString passName = Form("%s", pass);
  TFile* oadbf = new TFile(fname);
  if (!oadbf->IsOpen()) {
    oadbf->Close();
    delete oadbf;
    return "OADB file not found";
  }
  AliOADBContainer* oadbc = dynamic_cast<AliOADBContainer*>(oadbf->Get("TOFoadb"));
  tofPar = dynamic_cast<AliTOFPIDParams*>(oadbc->GetObject(run, "TOFparams", passName));
  oadbf->Close();
  delete oadbf;
  delete oadbc;

  TString result = "";
  if (tofPar) {
    result += Form("Reso=%6.2f ps", tofPar->GetTOFresolution());
    for (Int_t i = 0; i < 4; i++) {
      result += Form(" P%d=%6.4f", i, tofPar->GetSigParams(i));
    }
  }
  return result;
}

void readFromFile(TString fname)
{
  ifstream myfile(fname.Data());
  ofstream outfile("/tmp/tofoadbcalibs/intermediate.txt", ios::out);
  string line;
  TString l = "";
  if (!myfile.is_open()) {
    Printf("File %s not open", fname.Data());
    return;
  }

  while (getline(myfile, line)) {
    Printf("%s", line.c_str());
    l = line;
    TObjArray* arr = l.Tokenize("/");
    TString year = arr->At(0)->GetName();
    TString period = arr->At(1)->GetName();
    TString run = arr->At(2)->GetName();
    TString pass = arr->At(3)->GetName();
    TObjArray* parr = pass.Tokenize("-");
    for (int i = 0; i < parr->GetEntries(); i++) {
      auto ll = readTOFparams(run.Atoi(), pass.Data());
      l += " " + ll;
    }
    outfile << l << endl;

  }
  myfile.close();
}
