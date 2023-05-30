void compare(){
  TFile *f = new TFile("feelight.root");
  o2::tof::TOFFEElightInfo *fee = (o2::tof::TOFFEElightInfo *) f->Get("ccdb_object");

  TFile *f2 = new TFile("hitmap.root");
  TH2F *hit = (TH2F *) f2->Get("HitMapNoiseFiltered");
  hit->Divide(hit);

  TH2F *h = new TH2F("h","MC;Index #phi;Index #eta",18*48,0,18*48,91*2,0,91*2);
  TH2F *h2 = new TH2F("h2","Data;Index #phi;Index #eta",18*48,0,18*48,91*2,0,91*2);
  TH2F *h3 = new TH2F("h3","Data vs MC;Index #phi;Index #eta",18*48,0,18*48,91*2,0,91*2);
  
  for(int ic=0; ic < o2::tof::Geo::NCHANNELS; ic++){
    int isec = ic/8736;
    int istrip = (ic%8736)/96;
    int ipadz = (ic%96)/48;
    int ipadx = ic%48;
    int ix = isec*48 + ipadx;
    int iy = istrip*2 + ipadz;
    int irefx = ix/12 + 1;
    int irefy = iy/2 + 1;
    if( fee->getChannelEnabled(ic) ){
      h->Fill(isec*48 + ipadx, istrip*2 + ipadz);
      h3->Fill(isec*48 + ipadx, istrip*2 + ipadz);
    }
    if( hit->GetBinContent(irefx, irefy) && fee->getChannelEnabled(ic)){
      h2->Fill(isec*48 + ipadx, istrip*2 + ipadz);
    }
    else {
      fee->mChannelEnabled[ic] = false;
    }
  }
  TCanvas *c = new TCanvas();
  c->Divide(3,1);
  c->cd(1);
  h->Draw("colz");
  c->cd(2);
  h2->Draw("box");
  c->cd(3);
  h3->Draw("colz");
  h2->Draw("box,same");
  h->SetStats(0);
  h2->SetStats(0);
  h3->SetStats(0);

  printf("map comparsion: data/MC = %f%c\n",h2->Integral()*100/h->Integral(),'%');
  TFile *fo = new TFile("newfee.root","RECREATE");
  fo->WriteObjectAny(fee, "o2::tof::TOFFEElightInfo","ccdb_object");
  fo->Close();
}
