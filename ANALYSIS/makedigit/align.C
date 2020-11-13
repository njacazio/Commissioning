void align(int cr=0){
   float calib[2][4][10],pcalib[2][4][10];
   int ncalib[2][4][10];

   TH1F *h = new TH1F("h","",1000,-10000,10000);

   for(int i=0;i < 2;i ++)
     for(int j=0;j < 4;j ++)
        for(int k=0;k < 10;k ++){
            pcalib[i][j][k] = 0;
            calib[i][j][k] = 0;
            ncalib[i][j][k] = 0;
        }

   FILE *fin = fopen("calib.txt","r");
   if(fin){
     int ia,ib,ic;
      float fd;
      while(fscanf(fin,"%d %d %d %f",&ia,&ib,&ic,&fd) == 4){
        pcalib[ia][ib][ic] = fd;
      }
     fclose(fin);
   }

   FILE *f = fopen("newcal.txt","r");

   int icr,cr1,cr2,trm;
   float cal;
   while(fscanf(f,"%d %d %d %d %f",&icr,&cr1,&cr2,&trm,&cal) == 5){
      h->Fill(cal);
      if(cr==icr && cr==0){
        calib[0][cr1][trm] += cal;
        ncalib[0][cr1][trm]++;
      }
      if(cr==icr && cr==1){ 
        calib[1][cr2][trm] += cal;
        ncalib[1][cr2][trm]++;
      }
   }

   FILE *fo = fopen("calib.txt","w");
   for(int i=0;i < 2;i ++)
     for(int j=0;j < 4;j ++)
        for(int k=0;k < 10;k ++){
            if(ncalib[i][j][k]) calib[i][j][k] /= ncalib[i][j][k];
            fprintf(fo,"%d %d %d %f\n",i,j,k,calib[i][j][k] + pcalib[i][j][k]);
        }
   fclose(fo);

   TFile *fout = new TFile("align.root","RECREATE");
   h->Write();
   fout->Close();
}
