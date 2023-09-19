#include "DataFormatsTOF/ParameterContainers.h"
using namespace o2::tof;
void makeCCDB(int runNumber,
    TString passes)
{
  ParameterCollection tof("tofParams");
  tof.addParameter("unanchored", "time_resolution", 80);
  TObjArray* arr = passes.Tokenize("-");
  for (int i = 0; i < arr->GetEntries(); i++) {
    TString pass = arr->At(i)->GetName();
    readTOFparams(runNumber, pass.Data());
    tof.addParameter(pass.Data(), "time_resolution", tofPar->GetTOFresolution());
    for (int j = 0; j < 4; j++) {
      tof.addParameter(pass.Data(), Form("TrkRes.Pi.P%i", j), tofPar->GetSigParams(j));
      tof.addParameter(pass.Data(), Form("TrkRes.Ka.P%i", j), tofPar->GetSigParams(j));
      tof.addParameter(pass.Data(), Form("TrkRes.Pr.P%i", j), tofPar->GetSigParams(j));
    }
  }

  TFile algFile(Form("/tmp/tofoadbcalibs/Run2OADBConvertedParameters_Run%i.root", runNumber), "recreate");
  algFile.WriteObjectAny(&tof, "o2::tof::ParameterCollection", "ccdb_object");
  algFile.Close();
}

std::string getTS(int run)
{
  gSystem->Exec(Form("curl -i -L http://alice-ccdb.cern.ch/RCT/Info/RunInformation/%i > /tmp/rct.txt", run));
  ifstream rctfile("/tmp/rct.txt");
  string rctline;
  string SORline;
  string EORline;
  while (getline(rctfile, rctline)) {
    rctline.erase(std::remove_if(rctline.begin(), rctline.end(), [](auto const& c) -> bool { return !std::isalnum(c); }), rctline.end());
    //cout <<"'"<< rctline <<"'"<<endl;
    if (rctline.find("EOR") != std::string::npos) {
      EORline = rctline;
      cout << "Found '" << rctline << "'" << endl;
    }
    if (rctline.find("SOR") != std::string::npos) {
      SORline = rctline;
      cout << "Found '" << rctline << "'" << endl;
    }
  }
  return Form("--starttimestamp %s --endtimestamp %s", SORline.c_str(), EORline.c_str());
  return Form("Run %i %s %s", run, SORline.c_str(), EORline.c_str());
}

void readFromFile(TString fname)
{
  ifstream myfile(fname.Data());
  ofstream outfile("/tmp/tofoadbcalibs/ccdbupload.sh", ios::out);
  string line;
  TString l = "";
  if (!myfile.is_open()) {
    Printf("File %s not open", fname.Data());
    return;
  }

  outfile << "#!/bin/bash" << endl;
  outfile << "" << endl;
  outfile << "export ccdbhost=http://alice-ccdb.cern.ch" << endl;
  outfile << "" << endl;

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

    // auto tslimits = getTS(run.Atoi());
    // outfile << Form("o2-ccdb-upload --host \"$ccdbhost\" -p asd -f /tmp/tofoadbcalibs/Run2OADBConvertedParameters_Run%i.root -k ccdb_object %s -m \"runNumber=%i;JIRA=[O2-4000];\"",
    //     run.Atoi(),
    //     ll.Data(),
    //     run.Atoi())
    //         << endl;
  }
  myfile.close();
}
