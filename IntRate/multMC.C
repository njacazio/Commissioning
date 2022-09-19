float orbit_lenght = 90E-6;
float thrS = 0.1;
float thrB = 0.05;

TH1D *hback = nullptr;
TF1 *fitfunc;

float fractionTF = 1E-6;

double myfunc(double *x, double *par){
  double val = 0;
  if(hback){
    int ibin = hback->FindBin(x[0]);
    val += par[0] * hback->GetBinContent(ibin);
  }
  float xx = int(x[0]);
  val += TMath::Landau(xx, par[2], par[3])*par[1];

  return val;
}

void doplot(TH2F *h, TProfile *hp, int nactivechannels, float res[3], std::vector<int>& bcInt, std::vector<float>& bcRate, std::vector<float>& bcPileup);

void multMC(){
  fitfunc = new TF1("fitfunc",myfunc,0,10,4);
  fitfunc->SetParameter(0,1);
  fitfunc->SetParLimits(0,0,100);
  fitfunc->SetParameter(1,1);
  fitfunc->SetParLimits(1,0,1E8);
  fitfunc->SetParameter(2,1);
  //  fitfunc->SetParLimits(2,0,100);
  fitfunc->SetParameter(3,1);
  //  fitfunc->SetParLimits(3,0,100);
  fitfunc->SetLineColor(4);
  float res[3] = {};
  int nactivechannels = o2::tof::Geo::NCHANNELS;

  TFile *f = new TFile("tofDigitsQC.root");
  auto mon = f->Get("TaskDigits");
  o2::quality_control::core::MonitorObject *obj = (o2::quality_control::core::MonitorObject *) mon->FindObject("Multiplicity/VsBC");
  TH2F *h = (TH2F *) obj->getObject();

  obj = (o2::quality_control::core::MonitorObject *) mon->FindObject("OrbitVsCrate");
  TH2F *hOrbit = (TH2F *) obj->getObject();
  printf("%d %d\n",hOrbit->GetYaxis()->GetNbins(),hOrbit->GetXaxis()->GetNbins());
  //  return;
  for(int i=1; i <= hOrbit->GetYaxis()->GetNbins(); i++){
    float maxv = 0;
    for(int j=1; j <= hOrbit->GetXaxis()->GetNbins(); j++){
      if(hOrbit->GetBinContent(j,i) > maxv){
	maxv = hOrbit->GetBinContent(j,i);
      }
    }
    fractionTF += maxv;
  }
  fractionTF /= 128*3;

  obj = (o2::quality_control::core::MonitorObject *) mon->FindObject("Multiplicity/VsBCpro");
  TProfile *hp = (TProfile *) obj->getObject();

  obj = (o2::quality_control::core::MonitorObject *) mon->FindObject("HitMap");
  TH2F *hmap = (TH2F *) obj->getObject();
  hmap->Divide(hmap);
  hmap->Draw("colz");

  nactivechannels = hmap->Integral()*24;
  printf("N channels = %d\n",nactivechannels);

  std::vector<int> bcInt;
  std::vector<float> bcRate;
  std::vector<float> bcPileup;

  doplot(h, hp, nactivechannels, res, bcInt, bcRate, bcPileup);
  printf("\n\nnoise rate per channel= %f Hz - collision rate = %f Hz - mu-pilup = %f \n", res[0], res[1], res[2]);

  for(int i=0; i < bcInt.size(); i++){
    printf("bc = %d) rate = %f, pilup = %f\n",bcInt[i]*18 -9, bcRate[i], bcPileup[i]);
  }

}

void doplot(TH2F *h, TProfile *hp, int nactivechannels, float res[3], std::vector<int>& bcInt, std::vector<float>& bcRate, std::vector<float>& bcPileup){
  int nb = 0;
  for(int i=1; i <= 198; i++){
    if(hp->GetBinContent(i) < thrB){

      if(! hback){
	hback = h->ProjectionY("back",i,i);
      } else {
	hback->Add(h->ProjectionY("tmp",i,i));
      }

      nb++;
    }
  }

  int ns = 0;
  std::vector<int> signals;

  new TCanvas;
  h->Draw("colz");

  new TCanvas;
  hp->Draw();

  float sumw = 0.;
  float pilup = 0.;
  float ratetot = 0.;

  if(nb){
    for(int i=1; i <= 198; i++){
      if(hp->GetBinContent(i) > thrS){
	signals.push_back(i);
	ns++;
      }
    }

    TCanvas *c = new TCanvas;
    c->Divide(signals.size(),1);
    hback->SetLineColor(2);

    for(int i=0; i < signals.size(); i++){
      c->cd(i+1)->SetLogy();
      c->cd(i+1)->SetLogx();
      TLegend *leg = new TLegend(0.6,0.5,0.85,0.7);
      TH1D *hb = new TH1D(*hback);
      hb->SetName(Form("hback_%d",i));
      int ibc = signals[i];
      int bcmin = (ibc-1)*18;
      int bcmax = ibc*18;
      TH1D *hs = h->ProjectionY(Form("sign_%d_%d",bcmin,bcmax),ibc,ibc);
      hs->SetTitle(Form("%d < BC < %d",bcmin,bcmax));
      hs->Draw();
      hb->Scale(hs->GetBinContent(1) / hb->GetBinContent(1));
      hback->Scale(hs->GetBinContent(1) / hback->GetBinContent(1));
      float overall = hs->Integral();
      hs->Fit(fitfunc,"+","",0,7);
      float background = hb->Integral();
      float background2 = hback->Integral()*fitfunc->GetParameter(0);
      hb->Draw("SAME");
      hb->SetLineWidth(3);
      float prob = (overall - background) / overall / fractionTF;
      float prob2 = (overall - background2) / overall / fractionTF;
      float mu = TMath::Log(1./(1-prob));
      float mu2 = TMath::Log(1./(1-prob2));
      float rate = mu / orbit_lenght;
      float rate2 = mu2 / orbit_lenght;
      leg->AddEntry(hs,"mult","L");
      leg->AddEntry(hb,"noise","L");
      leg->SetHeader(Form("rate=%.0f Hz",rate));
      bcInt.push_back(ibc);
      bcRate.push_back(rate);
      bcPileup.push_back(mu/prob);
      leg->Draw("SAME");
      sumw += rate2;
      pilup += mu/prob * rate2;
      ratetot += rate2;
      printf("interaction prob = %f, rate=%f Hz, mu=%f (fractionTF = %f, scaling = %f)\n",mu, rate, mu/prob, fractionTF, fitfunc->GetParameter(0));
    }

    if(sumw>0){
      res[0] = (hback->GetMean() - 0.5) / orbit_lenght * h->GetNbinsX() / nactivechannels;
      res[1] = ratetot;
      res[2] = pilup/sumw;
    }
  }
}
