#!/usr/bin/env python3


from ROOT import o2, gInterpreter, gSystem
import os


gInterpreter.Declare("""
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

""")

if 1:
    from ROOT import getTS


def main():
    runs = {}
    with open("/tmp/intermediate.txt") as f:
        for i in f:
            print(i)
            i = i.strip()
            i = i.replace("= ", "=")
            i = i.replace(" ps", "")
            i = i.split(" ")
            run = int(i[0].split("/")[2])
            passname = i[0].split("/")[3]
            params = {"reso": float(i[1].replace("Reso=", "")),
                      "p0": float(i[2].replace("P0=", "")),
                      "p1": float(i[3].replace("P1=", "")),
                      "p2": float(i[4].replace("P2=", "")),
                      "p3": float(i[5].replace("P3=", ""))}
            runs.setdefault(run, {})[passname] = params
            # print(i)
            # break
    # print(runs)
    os.makedirs("/tmp/ccdboadbupload", exist_ok=True)

    UPLOAD_FILE_NAME = "uploadToCCDB.sh"
    with open("/tmp/ccdboadbupload/uploadToCCDB.sh", "w") as f:

        f.write("#!/bin/bash\n")
        f.write("\n")
        f.write("# Script to upload the converted OADB parameters to the CCDB\n")
        f.write("# For Run2 converted data\n")
        f.write("# Upload with `bash uploadToCCDB.sh`\n")
        # f.write("# Upload with `bash uploadToCCDB.sh`\n")
        f.write("\n")
        f.write("export ccdbhost=http://alice-ccdb.cern.ch\n")
        # f.write("export ccdbhost=http://ccdb-test.cern.ch:8080\n")
        f.write("\n")

        for i in runs:
            tof = o2.tof.ParameterCollection("ccdb_object")
            tof.addParameter("unanchored", "time_resolution", 80)
            unanchoredset = False
            for passname in runs[i]:
                tof.addParameter(passname, "time_resolution", runs[i][passname]["reso"])
                for j in [0, 1, 2, 3]:
                    tof.addParameter(passname, f"TrkRes.Pi.P{j}", runs[i][passname][f"p{j}"])
                    tof.addParameter(passname, f"TrkRes.Ka.P{j}", runs[i][passname][f"p{j}"])
                    tof.addParameter(passname, f"TrkRes.Pr.P{j}", runs[i][passname][f"p{j}"])
                    if not unanchoredset:
                        tof.addParameter("unanchored", f"TrkRes.Pi.P{j}", runs[i][passname][f"p{j}"])
                        tof.addParameter("unanchored", f"TrkRes.Ka.P{j}", runs[i][passname][f"p{j}"])
                        tof.addParameter("unanchored", f"TrkRes.Pr.P{j}", runs[i][passname][f"p{j}"])
                unanchoredset = True
            tof.SaveAs(f"/tmp/ccdboadbupload/Run2OADBConvertedParameters_Run{i}.root")
            tslimits = getTS(i)
            tslimits = tslimits.replace("SOR", "")
            tslimits = tslimits.replace("EOR", "")
            f.write(
                f"o2-ccdb-upload --host \"$ccdbhost\" -p Analysis/PID/TOFRun2 -f Run2OADBConvertedParameters_Run{i}.root -k ccdb_object {tslimits} -m \"runNumber={i};JIRA=[O2-4133];\"\n")
    packed_output = "packed_converted_calib.zip"
    instr = ["Instructions:",
             f"  1) download `{packed_output}` attached to this ticket",
             f"  2) unzip `{packed_output}`",
             f"  3) run `bash {UPLOAD_FILE_NAME}` ad described in the header"]
    pack_cmd = f"zip -r {os.path.join('/tmp/ccdboadbupload/', packed_output)} /tmp/ccdboadbupload/*"

    for i in instr:
        print(i)
    print(pack_cmd)


main()


# void readFromFile(TString fname)
# {
#   ifstream myfile(fname.Data());
#   ofstream outfile("/tmp/tofoadbcalibs/ccdbupload.sh", ios::out);
#   string line;
#   TString l = "";
#   if (!myfile.is_open()) {
#     Printf("File %s not open", fname.Data());
#     return;
#   }


#   while (getline(myfile, line)) {
#     Printf("%s", line.c_str());
#     l = line;
#     TObjArray* arr = l.Tokenize("/");
#     TString year = arr->At(0)->GetName();
#     TString period = arr->At(1)->GetName();
#     TString run = arr->At(2)->GetName();
#     TString pass = arr->At(3)->GetName();
#     TObjArray* parr = pass.Tokenize("-");
#     for (int i = 0; i < parr->GetEntries(); i++) {
#       auto ll = readTOFparams(run.Atoi(), pass.Data());
#       l += " " + ll;
#     }
#     outfile << l << endl;

#     // auto tslimits = getTS(run.Atoi());
#     // outfile << Form("o2-ccdb-upload --host \"$ccdbhost\" -p asd -f /tmp/tofoadbcalibs/Run2OADBConvertedParameters_Run%i.root -k ccdb_object %s -m \"runNumber=%i;JIRA=[O2-4000];\"",
#     //     run.Atoi(),
#     //     ll.Data(),
#     //     run.Atoi())
#     //         << endl;
#   }
#   myfile.close();
# }
