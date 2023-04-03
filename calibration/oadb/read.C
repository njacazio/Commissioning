void read(const char*pass ="unanchored"){
  TFile *f = new TFile("ccdb.root");
  o2::tof::ParameterCollection *a = (o2::tof::ParameterCollection *) f->Get("ccdb_object");

  printf("Num of passes = %lu\n",a->getFullMap().size());
  printf("asking for pass: %s\n",pass);
  
  if(a->getSize(pass) > -1){
    a->print(pass);
    const auto& params = a->getPars(pass);
    if(params.count("eff_3center")){
      printf("here -> %f\n",params.at("eff_center"));
    }
  }
  else printf("pass not available\n");
}
