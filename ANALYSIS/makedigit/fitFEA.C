void fitFEA(){

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

  TF1 *ff = new TF1("ff","gaus",-2000,2000);

  TFile *f = TFile::Open("calib.root");
  TTree *tree = (TTree *) f->Get("tree");
  tree->Draw("dtime:fea1 >>p1(200,0,200,40,-1500,1500)","(cr1==12) && abs(dtime)< 1500","colz");
  TH2D *h1 = (TH2D *) gDirectory->FindObject("p1");
  tree->Draw("dtime:fea1 >>p2(200,0,200,40,-1500,1500)","(cr1==13) && abs(dtime)< 1500","colz");
  TH2D *h2 = (TH2D *) gDirectory->FindObject("p2");
  tree->Draw("dtime:fea1 >>p3(200,0,200,40,-1500,1500)","(cr1==14) && abs(dtime)< 1500","colz");
  TH2D *h3 = (TH2D *) gDirectory->FindObject("p3");
  tree->Draw("dtime:fea1 >>p4(200,0,200,40,-1500,1500)","(cr1==15) && abs(dtime)< 1500","colz");
  TH2D *h4 = (TH2D *) gDirectory->FindObject("p4");
  tree->Draw("-dtime:fea2 >>p5(200,0,200,40,-1500,1500)","(cr2==56) && abs(dtime)< 1500","colz");
  TH2D *h5 = (TH2D *) gDirectory->FindObject("p5");
  tree->Draw("-dtime:fea2 >>p6(200,0,200,40,-1500,1500)","(cr2==57) && abs(dtime)< 1500","colz");
  TH2D *h6 = (TH2D *) gDirectory->FindObject("p6");
  tree->Draw("-dtime:fea2 >>p7(200,0,200,40,-1500,1500)","(cr2==58) && abs(dtime)< 1500","colz");
  TH2D *h7 = (TH2D *) gDirectory->FindObject("p7");
  tree->Draw("-dtime:fea2 >>p8(200,0,200,40,-1500,1500)","(cr2==59) && abs(dtime)< 1500","colz");
  TH2D *h8 = (TH2D *) gDirectory->FindObject("p8");

  TCanvas *c = new TCanvas();
  c->Divide(4,2);
  c->cd(1);
  h1->Draw("colz");
  TProfile *h1_1 = (TProfile *) gDirectory->FindObject("p1_1");
  c->cd(2);
  h2->Draw("colz");
  TProfile *h2_1 = (TProfile *) gDirectory->FindObject("p2_1");
  c->cd(3);
  h3->Draw("colz");
  TProfile *h3_1 = (TProfile *) gDirectory->FindObject("p3_1");
  c->cd(4);
  h4->Draw("colz");
  TProfile *h4_1 = (TProfile *) gDirectory->FindObject("p4_1");
  c->cd(5);
  h5->Draw("colz");
  TProfile *h5_1 = (TProfile *) gDirectory->FindObject("p5_1");
  c->cd(6);
  h6->Draw("colz");
  TProfile *h6_1 = (TProfile *) gDirectory->FindObject("p6_1");
  c->cd(7);
  h7->Draw("colz");
  TProfile *h7_1 = (TProfile *) gDirectory->FindObject("p7_1");
  c->cd(8);
  h8->Draw("colz");
  TProfile *h8_1 = (TProfile *) gDirectory->FindObject("p8_1");

  int ic[8] = {12,13,14,15,56,57,58,59};
  TH2D *ph[8];
  ph[0]=h1;
  ph[1]=h2;
  ph[2]=h3;
  ph[3]=h4;
  ph[4]=h5;
  ph[5]=h6;
  ph[6]=h7;
  ph[7]=h8;

  FILE *fo = fopen("fea.cal","w");

  new TCanvas;

  for(int i=0;i < 8;i++){
    ph[i]->SetMarkerStyle(20);
    for(int j=0; j < 200;j++){
      TH1D *htemp = ph[i]->ProjectionY("htemp",j+1,j+1);
      if(htemp->Integral() > 20){
         htemp->Fit(ff,"WW");
         fprintf(fo,"%d %d %f\n",ic[i],j,ff->GetParameter(1)*0.5+feac[ic[i]][j]);
         printf("%d %d %f\n",ic[i],j,ff->GetParameter(1));
      }
      else
         fprintf(fo,"%d %d %f\n",ic[i],j,feac[ic[i]][j]);
    }
  }

  fclose(fo);
}
