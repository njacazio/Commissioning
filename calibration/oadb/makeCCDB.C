using namespace o2::tof;

void makeCCDB(){
  ParameterCollection tof("tofParams");

  const int npasses = 4;
  const char* passes[npasses] = {"unanchored", "apass1", "apass2", "apass3"};
  float resolution[npasses] = {80, 90, 90, 80};

  for(int ip=0; ip < npasses; ip++){
    tof.addParameter(passes[ip], "time_resolution", resolution[ip]);
    tof.addParameter(passes[ip], "eff_center", 0.995);
    tof.addParameter(passes[ip], "eff_boundary1", 0.94);
    tof.addParameter(passes[ip], "eff_boundary2", 0.833);
    tof.addParameter(passes[ip], "eff_boundary3", 0.1);
  }

  const auto& mappa = tof.getFullMap();
  for(const auto& [pass, value] : mappa){
    std::cout << "pass name = " << pass  << std::endl;
    const bool alreadyPresent = (mappa.find(pass) != mappa.end());
    std::cout << "alreadyPresent =" << alreadyPresent << ", size = " << mappa.at(pass).size() <<  std::endl;
    tof.print(pass);
  }
  TFile algFile("ccdb.root", "recreate");
  algFile.WriteObjectAny(&tof, "o2::tof::ParameterCollection", "ccdb_object");
  algFile.Close();
  
}
