void testDia(const char *fn="TOF/Calib/Diagnostic/dia.root"){
  TFile *f = new TFile(fn);

  TH2F *h = new TH2F("hErr","P err;crate;TRM",72,0,72,13,0,13);
  
  o2::tof::Diagnostic *dia = (o2::tof::Diagnostic *) f->Get("ccdb_object");
  dia->print(true);
  
  o2::tof::CalibTOFapi api(0, nullptr, nullptr, dia);

  api.loadDiagnosticFrequencies();

  const std::vector<std::pair<int, float>> &err = api.getTRMerrorProb();

  for (const auto el : err ){
    std::cout << "first = " << el.first << " - second = " << el.second << std::endl;
    h->Fill(el.first /100, el.first % 100, el.second);
  }

  h->Draw("colz");
  h->SetStats(0);
  h->SetMaximum(1);
}
