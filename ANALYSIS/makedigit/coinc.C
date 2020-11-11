// Requirement: o2sim_geometry.root
// run macro in compiled mode: root -b -q -l coinc.C+

#include "TH1F.h"
#include "TH2F.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TTree.h"
#include "TOFBase/Digit.h"
#include "TOFBase/Geo.h"

int maxdiginrow = 10000000; 

bool isNoise(int ch){
  if(ch == 31443) return 1;
  if(ch == 34482) return 1;
  if(ch == 34483) return 1;
  if(ch == 125331) return 1;
  if(ch == 125518) return 1;
  if(ch == 125675) return 1;
  if(ch == 125808) return 1;
  if(ch == 128753) return 1;
  if(ch == 128800) return 1;

  if(ch == 123744) return 1;
  if(ch == 123745) return 1;
  if(ch == 124821) return 1;
  if(ch == 125089) return 1;
  if(ch == 125317) return 1;
  if(ch == 125318) return 1;
  if(ch == 125325) return 1;
  if(ch == 125326) return 1;
  if(ch == 125329) return 1;
  if(ch == 125332) return 1;
  if(ch == 125371) return 1;
  if(ch == 125372) return 1;
  if(ch == 125473) return 1;
  if(ch == 125517) return 1;
  if(ch == 125578) return 1;
  if(ch == 125673) return 1;
  if(ch == 125674) return 1;
  if(ch == 125727) return 1;
  if(ch == 125809) return 1;
  if(ch == 127510) return 1;
  if(ch == 128798) return 1;

  return 0;
}

void coinc(const char *namef = "tofdigits.root"){
   TFile *f = new TFile(namef);
   TTree *t = (TTree *) f->Get("o2sim");
   
   o2::tof::DigitHeader header,*Pheader=&header;
   std::vector<o2::tof::Digit> digit, *Pdigit=&digit;
   std::vector<o2::tof::ReadoutWindowData> row, *Prow = &row;
   t->SetBranchAddress("TOFHeader",&Pheader);
   t->SetBranchAddress("TOFDigit",&Pdigit);
   t->SetBranchAddress("TOFReadoutWindow",&Prow);

   TH1F *hcratein = new TH1F("hcratein",";crate;",72,0,72);
   TH1F *hncrate = new TH1F("hncrate",";n crate;",73,0,73);

   TH1F *hDeltaT = new TH1F("hDeltaT",";Deltat -L/c (ps)",1000,-100E3,100E3);
   TH2F *hDeltaT2 = new TH2F("hDeltaT2",";L (cm);Deltat -L/c (ps)",100,0,1000,1000,-100E3,100E3);

   TH1F *hNoise = new TH1F("hNoise",";channel;counts",160000,0,160000);

   int64_t bcdelta;
   uint64_t bc1,bc2;
   int tdc1,tdc2,ch1,ch2,det1[5],det2[5],ech1,ech2,cr1,cr2,itemp;
   double dtime;
   float pos1[3],pos2[3],v,dist,delay1,delay2,ftemp;

   TFile *fo = new TFile("output.root","RECREATE");
   TTree *to = new TTree("tree","tree");
   to->Branch("ch1",&ch1,"ch1/I");
   to->Branch("ch2",&ch2,"ch2/I");
   to->Branch("pos1",pos1,"pos1[3]/F");
   to->Branch("pos2",pos2,"pos2[3]/F");
   to->Branch("dtime",&dtime,"dtime/D");
   to->Branch("l",&dist,"l/F");
   to->Branch("cr1",&cr1,"cr1/I");
   to->Branch("cr2",&cr2,"cr2/I");

   for(int i=0; i < t->GetEntries(); i++){
     t->GetEvent(i);
    
     for(int icrate=0; icrate < 72; icrate++){
       hcratein->AddBinContent(icrate,header.getCrateCounts(icrate));
       hncrate->AddBinContent(icrate+1, header.numCratesCounts(icrate+1));
     }

     // loop over row
     for(uint64_t j=0; j < row.size(); j++){
        o2::tof::ReadoutWindowData& rowc = row[j];
        auto digRow = rowc.getBunchChannelData(digit);

       if(digRow.size() < 2 || digRow.size() > maxdiginrow) continue;
 
       // loop over digits
       for(int k1=0; k1 < digRow.size(); k1++){
         auto dig1c = digRow[k1];
         bc1 = dig1c.getBC();
         tdc1 = dig1c.getTDC();
         ch1 = dig1c.getChannel();

         if(isNoise(ch1)) continue;

         hNoise->Fill(ch1);

         // Det IDs (sector, module, strip, padx, padz)
         o2::tof::Geo::getVolumeIndices(ch1, det1);

         // channel pos (o2sim_geometry.root needed!)
         o2::tof::Geo::getPos(det1, pos1);

         // channel ID from electronic
         ech1 = o2::tof::Geo::getECHFromCH(ch1);

         // delay due to cable length
         delay1 = o2::tof::Geo::getCableTimeShift(o2::tof::Geo::getCrateFromECH(ech1), o2::tof::Geo::getTRMFromECH(ech1), o2::tof::Geo::getChainFromECH(ech1), o2::tof::Geo::getTDCFromECH(ech1));

         cr1 = o2::tof::Geo::getCrateFromECH(ech1);

         // loop over digits to look for coincs
         for(int k2=k1+1; k2 < digRow.size(); k2++){
            auto dig2c = digRow[k2];
            bc2 = dig2c.getBC();
            tdc2 = dig2c.getTDC();
            ch2 = dig2c.getChannel(); 
            o2::tof::Geo::getVolumeIndices(ch2, det2);
            o2::tof::Geo::getPos(det2, pos2);
            ech2 = o2::tof::Geo::getECHFromCH(ch2);
            delay2 = o2::tof::Geo::getCableTimeShift(o2::tof::Geo::getCrateFromECH(ech2), o2::tof::Geo::getTRMFromECH(ech2), o2::tof::Geo::getChainFromECH(ech2), o2::tof::Geo::getTDCFromECH(ech2));

            if(isNoise(ch2)) continue;

            cr2 = o2::tof::Geo::getCrateFromECH(ech2);

            if(pos1[1] < pos2[1]) v = 2.9979246e-2;
            else v = -2.9979246e-2;

            bcdelta = bc1;
            bcdelta -= bc2;
            dtime = bcdelta*1024;
            dtime += int(tdc1) - tdc2;
            dtime *= o2::tof::Geo::TDCBIN;

            dist = (pos1[0]-pos2[0])*(pos1[0]-pos2[0]);
            dist += (pos1[1]-pos2[1])*(pos1[1]-pos2[1]);
            dist += (pos1[2]-pos2[2])*(pos1[2]-pos2[2]);
            dist = sqrt(dist);

            dtime -= delay1 - delay2;

            if(TMath::Abs(dtime) < 20000E3) {

              if(cr2 < cr1){ // invert
                 ftemp = pos1[0];
                 pos1[0] = pos2[0];
                 pos2[0] = ftemp;

                 ftemp = pos1[1];
                 pos1[1] = pos2[1];
                 pos2[1] = ftemp;

                 ftemp = pos1[2];
                 pos1[2] = pos2[2];
                 pos2[2] = ftemp;
  
                 dtime = -dtime;

                 itemp = ch1;
                 ch1 = ch2;
                 ch2 = itemp;

                 itemp = cr1;
                 cr1 = cr2;
                 cr2 = itemp;
              }

              hDeltaT->Fill(dtime);
              hDeltaT2->Fill(dist,dtime);
              to->Fill();
            }
         }
       }
     }
   }

   TCanvas *c1 = new TCanvas();
   c1->Divide(2,1);
   c1->cd(1);
   hcratein->Draw();
   c1->cd(2);
   hncrate->Draw();

   TCanvas *c2 = new TCanvas();
   c2->Divide(2,1);
   c2->cd(1);
   hDeltaT->Draw();
   c2->cd(2);
   hDeltaT2->Draw("colz");

   for(int i=1; i < 1600000;i++){
      if(hNoise->GetBinContent(i) > 100) printf("  if(ch == %d) return 1;\n",i-1);
   }

   fo->cd();
   to->Write();
   hNoise->Write();
   fo->Close();
}
