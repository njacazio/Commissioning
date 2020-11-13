void calib(){
    TFile *fsleewing = new TFile("outputCCDBfromOCDB.root"); // taken from alien:///alice/cern.ch/user/n/noferini/commissioning/outputCCDBfromOCDB.root
    o2::dataformats::CalibTimeSlewingParamTOF *ob = (o2::dataformats::CalibTimeSlewingParamTOF *) fsleewing->Get("TimeSlewing");

/*
    float feac[72][200];
    int fcrate,ffea;
    float valcal;
    FILE *fifea = fopen("fea.cal","r");

    for(int i=0; i < 72;i++)
      for(int j=0; j < 200;j++)
        feac[i][j] = 0;

    if(fifea){
      while(fscanf(fifea,"%d %d %f",&fcrate,&ffea,&valcal) == 3){
        feac[fcrate][ffea] = valcal;
      }
    }
*/

    TFile *f = new TFile("output.root");
    TTree *t = (TTree *) f->Get("tree");

    TH1F *hCoinc[4][4];
    TH2F *hCoinc2D[4][4];

    TH1F *hCoinc1[4][4][10];
    TH1F *hCoinc2[4][4][10];

    float calib1[4][10];
    float calib2[4][10];


    int itopstart = 12;
    int ibottomstart = 56;

    TH1F *hAll = new TH1F("hAll","",200,-5E3,5E3);
    TH2F *hTot1 = new TH2F("hTot1","",50,0,2,50,-4000,4000);
    TH2F *hTot2 = new TH2F("hTot2","",50,0,2,50,-4000,4000);

    for(int i=0; i < 4; i++){
      for(int j=0; j < 4; j++){
        hCoinc[i][j] = new TH1F(Form("hCoinc_%d_%d",i+itopstart,j+ibottomstart),Form("hCoinc_%d_%d;Deltat (ps)",i+itopstart,j+ibottomstart),2000,-200E3,200E3);
        hCoinc2D[i][j] = new TH2F(Form("hCoinc2D_%d_%d",i+itopstart,j+ibottomstart),Form("hCoinc_%d_%d;L (m);Deltat (ps)",i+itopstart,j+ibottomstart),16,6,10,2000,-200E3,200E3);

        for(int itrm=3;itrm<13;itrm++){
            hCoinc1[i][j][itrm-3] = new TH1F(Form("hCoinc1_%d_%d_%d",i+itopstart,j+ibottomstart,itrm),Form("hCoinc_%d_%d trm1=%d;Deltat (ps)",i+itopstart,j+ibottomstart,itrm),4000,-500E3,500E3);
            hCoinc2[i][j][itrm-3] = new TH1F(Form("hCoinc2_%d_%d_%d",i+itopstart,j+ibottomstart,itrm),Form("hCoinc_%d_%d trm2=%d;Deltat (ps)",i+itopstart,j+ibottomstart,itrm),4000,-500E3,500E3);

            calib1[i][itrm-3] = 0;
            calib2[i][itrm-3] = 0;
        } 
      }
    }

    // read TRM calibrations if available 
    FILE *fin = fopen("calib.txt","r");
    if(fin){
      int ia,ib,ic;
      float fd;
      while(fscanf(fin,"%d %d %d %f",&ia,&ib,&ic,&fd) == 4){
        if(ia==0) calib1[ib][ic] = fd;
        else calib2[ib][ic] = fd;

//        if(ia==0) printf("%d %d %f\n",ib+itopstart,ic,fd);
//        else  printf("%d %d %f\n",ib+ibottomstart,ic,fd);
      }
    }

    int ch1,ch2,cr1,cr2,fea1,fea2,trm1,trm2;
    float pos1[3],pos2[3],tot1,tot2;
    double dtime;

    t->SetBranchAddress("ch1",&ch1);
    t->SetBranchAddress("ch2",&ch2);
    t->SetBranchAddress("pos1",pos1);
    t->SetBranchAddress("pos2",pos2);
    t->SetBranchAddress("cr1",&cr1);
    t->SetBranchAddress("cr2",&cr2);
    t->SetBranchAddress("fea1",&fea1);
    t->SetBranchAddress("fea2",&fea2);
    t->SetBranchAddress("tot1",&tot1);
    t->SetBranchAddress("tot2",&tot2);

    TFile *fo = new TFile("calib.root","RECREATE");
    TTree *to = new TTree("tree","tree");
    to->Branch("ch1",&ch1,"ch1/I");
    to->Branch("ch2",&ch2,"ch2/I");
    to->Branch("pos1",pos1,"pos1[3]/F");
    to->Branch("pos2",pos2,"pos2[3]/F");
    to->Branch("dtime",&dtime,"dtime/D");
    to->Branch("cr1",&cr1,"cr1/I");
    to->Branch("cr2",&cr2,"cr2/I");
    to->Branch("fea1",&fea1,"fea1/I");
    to->Branch("fea2",&fea2,"fea2/I");
    to->Branch("tot1",&tot1,"tot1/F");
    to->Branch("tot2",&tot2,"tot2/F");

    for(int i=0; i < t->GetEntries(); i++){
      t->GetEvent(i);

      trm1 = t->GetLeaf("trm1")->GetValue() - 3;
      trm2 = t->GetLeaf("trm2")->GetValue() - 3;

      int cr1t = t->GetLeaf("cr1")->GetValue() - itopstart;
      if(cr1t < 0 || cr1t > 3) continue;
      int cr2t = t->GetLeaf("cr2")->GetValue() - ibottomstart;
      if(cr2t < 0 || cr2t > 3) continue;

      dtime = t->GetLeaf("dtime")->GetValue() + t->GetLeaf("l")->GetValue()*33.356409 - calib1[cr1t][trm1] + calib2[cr2t][trm2];
  
      dtime -= ob->evalTimeSlewing(t->GetLeaf("ch1")->GetValue(),t->GetLeaf("tot1")->GetValue()*1E-3);// - ob->evalTimeSlewing(t->GetLeaf("ch1")->GetValue(),0);
      dtime += ob->evalTimeSlewing(t->GetLeaf("ch2")->GetValue(),t->GetLeaf("tot2")->GetValue()*1E-3);// - ob->evalTimeSlewing(t->GetLeaf("ch2")->GetValue(),0);

//      dtime -= feac[cr1][fea1];
//      dtime += feac[cr2][fea2];

      hCoinc[cr1t][cr2t]->Fill(dtime);
      hCoinc2D[cr1t][cr2t]->Fill(t->GetLeaf("l")->GetValue()*0.01,dtime);
      hCoinc1[cr1t][cr2t][trm1]->Fill(dtime);
      hCoinc2[cr1t][cr2t][trm2]->Fill(dtime);

      hAll->Fill(dtime);
      hTot1->Fill(TMath::Log10(t->GetLeaf("tot1")->GetValue()*1E-3 + 1),dtime);
      hTot2->Fill(TMath::Log10(t->GetLeaf("tot2")->GetValue()*1E-3 + 1),-dtime);
      if(abs(dtime) < 10000) to->Fill();
    }

    TCanvas *c = new TCanvas();
    c->Divide(4,4);
    for(int i=0; i < 4; i++){
      for(int j=0; j < 4; j++){
        c->cd(i*4+j+1);
        hCoinc2D[i][j]->Draw("col");
      }
    }

    TCanvas *c2 = new TCanvas();
    c2->Divide(4,4);
    for(int i=0; i < 4; i++){
      for(int j=0; j < 4; j++){
        c2->cd(i*4+j+1);
        hCoinc[i][j]->Draw();
      }
    }

    TF1 *ff = new TF1("ff","gaus",-500E3,500E3);
    float peak;
    fo->cd();
    to->Write();
    hAll->Write();
    hTot1->Write();
    hTot2->Write();
    FILE *fcal = fopen("newcal.txt","w");
    for(int i=0; i < 4; i++){
      for(int j=0; j < 4; j++){
        for(int trm=0; trm < 10; trm++){
          ff->SetParameter(0,100);
          ff->SetParameter(1,0);
          ff->SetParameter(2,1000);
          ff->SetParLimits(2,200,10000);

          peak = hCoinc1[i][j][trm]->GetBinCenter(hCoinc1[i][j][trm]->GetMaximumBin());
          hCoinc1[i][j][trm]->Fit(ff,"WW","",peak - 3000, peak + 3000);
          if(hCoinc1[i][j][trm]->GetBinContent(hCoinc1[i][j][trm]->GetMaximumBin()) > 5) fprintf(fcal,"%d %d %d %d %f\n",0,i,j,trm,ff->GetParameter(1));
          hCoinc1[i][j][trm]->Write();
          peak = hCoinc2[i][j][trm]->GetBinCenter(hCoinc2[i][j][trm]->GetMaximumBin());
          hCoinc2[i][j][trm]->Fit(ff,"WW","",peak - 3000,peak + 3000);
          if(hCoinc2[i][j][trm]->GetBinContent(hCoinc2[i][j][trm]->GetMaximumBin()) > 5) fprintf(fcal,"%d %d %d %d %f\n",1,i,j,trm,-ff->GetParameter(1));
          hCoinc2[i][j][trm]->Write();
        }
      }
    }
    fclose(fcal);
    fo->Write();
}
