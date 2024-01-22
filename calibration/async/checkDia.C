void checkDia(const char* run=""){
  system(Form("ls %s/TOF/Calib/Diagnostic/*|awk -F\"_\" '{print $1\"_\"$2\"_\"$3\"_\"$4,$3}' >diagnostics",run));

  FILE *f = fopen("diagnostics","r");

  char path[200];
  int np=0;
  float x[1000],y[1000],ytrm[1000],row[1000],crate[72][1000], trm[72][10][1000] = {0};
  float ts;
  while(fscanf(f,"%s %f",path,&ts) == 2){
    TFile *ff = new TFile(path);
    o2::tof::Diagnostic *dia = (o2::tof::Diagnostic *) ff->Get("ccdb_object");
    x[np] = ts;//np*5;
    row[np] = dia->getFrequencyROW();
    if(row[np] < 0){
      printf("TO BE CHECKED -> %s\n",path);
      ff->Close();
      continue;
    }
    const auto& vec =  dia->getVector();
    for(const auto& obj : vec){
      int ic = dia->getCrate(obj.first);
      int itrm = dia->getSlot(obj.first);
      if(itrm > 2 && itrm < 13){
	itrm -= 3;
	trm[ic][itrm][np] += obj.second;
	//	printf("%d %d\n",ic,itrm);
      }
    }
    for(int ic=0; ic < 72; ic++){
      crate[ic][np] = dia->getFrequencyEmptyCrate(ic);
      if(crate[ic][np] > row[np]) printf("%f) %f > %f\n",x[np],crate[ic][np],row[np]);
      //      for(int itrm=0; itrm < 10; itrm++){
      //	trm[ic][itrm][np] = dia->getFrequency(dia->getTRMKey(ic, itrm));
      //      }
    }
    np++;
    ff->Close();
  }

  float nrowall[1000] = {0};
  for(int i=0; i < np; i++){
    y[i] = 0;
    ytrm[i] = 0;
    for(int ic=0; ic < 72; ic++){
      y[i] += crate[ic][i];
      nrowall[i] += (row[i] -  crate[ic][i]*0);
      for(int itrm=0; itrm < 10; itrm++){
	ytrm[i] += trm[ic][itrm][i];
      }
    }
    y[i] = (row[i] - y[i]/72) / row[i];
    ytrm[i] = (nrowall[i] - ytrm[i]/10) / nrowall[i];
  }
  TGraph *g = new TGraph(np,x,y);
  TGraph *g2 = new TGraph(np,x,ytrm);
  g->SetMarkerStyle(20);
  g->Draw("AP");
  g2->SetMarkerStyle(20);
  g2->SetMarkerColor(2);
  g2->SetLineColor(2);
  g2->Draw("P");
  g->SetTitle(Form("Crate <eff> in 5 mins time slot inside run %s;time elapsed (min);<#varepsilon>",run));
  g->GetXaxis()->SetTimeDisplay(1);
  g->GetXaxis()->SetTimeFormat("%d/%m h%H%F1970-01-01 00:00:00s0");
  g->GetXaxis()->SetNdivisions(409);
  g->SetMaximum(1);
  g->SetMinimum(0);
  TLegend *leg = new TLegend(0.2,0.4,0.5,0.7);
  leg->SetFillStyle(0);
  leg->AddEntry(g,"Crate eff","lp");
  leg->AddEntry(g2,"TRM eff","lp");
  leg->Draw("SAME");
}
