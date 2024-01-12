
#include "TFile.h"
#include "DataFormatsTOF/CalibTimeSlewingParamTOF.h"
#include "DataFormatsTOF/CalibInfoTOFshort.h"
#include "TOFBase/Utils.h"

bool useOnlyOldOffsets=true;  // enable it not to use old TS corrections, but only offsets
int firstSect;              // run starting from this sector (def=0), defined in doTS
int lastSect;               // run till this sector, defined in doTS

std::vector<o2::dataformats::CalibInfoTOFshort> mVectC, *mPvectC = &mVectC;
TChain *mTreeFit;
int mNfits = 0;
const int NCHPERBUNCH = o2::tof::Geo::NCHANNELS / o2::tof::Geo::NSECTORS / 16;
static const int NMINTOFIT = 250;

o2::dataformats::CalibTimeSlewingParamTOF *ts, *tsNew;

int extractNewTimeSlewing(const o2::dataformats::CalibTimeSlewingParamTOF* oldTS, o2::dataformats::CalibTimeSlewingParamTOF* newTS);
void fitTimeSlewing(int sector, const o2::dataformats::CalibTimeSlewingParamTOF* oldTS, o2::dataformats::CalibTimeSlewingParamTOF* newTS);
void fitChannelsTS(int chStart, const o2::dataformats::CalibTimeSlewingParamTOF* oldTS, o2::dataformats::CalibTimeSlewingParamTOF* newTS);
int fitSingleChannel(int ch, TH2F* h, const o2::dataformats::CalibTimeSlewingParamTOF* oldTS, o2::dataformats::CalibTimeSlewingParamTOF* newTS);

void doTS(int fsec=0, int lsec=17){
  firstSect = fsec;
  lastSect  = lsec;

  TFile *fCal = new TFile("./TOF/Calib/ChannelCalib/snapshot.root");
  ts = (o2::dataformats::CalibTimeSlewingParamTOF *) fCal->Get("ccdb_object");
  tsNew = new o2::dataformats::CalibTimeSlewingParamTOF;

  extractNewTimeSlewing(ts, tsNew);

  TFile *fsl = new TFile("newtsNew.root","RECREATE");
  fsl->WriteObjectAny(tsNew, tsNew->Class(), "ccdb_object");
  fsl->Close();
}


int extractNewTimeSlewing(const o2::dataformats::CalibTimeSlewingParamTOF* oldTS, o2::dataformats::CalibTimeSlewingParamTOF* newTS)
{
  if (!oldTS || !newTS) { // objects were not defined -> to nothing
    return 1;
  }
  newTS->bind();

  static auto fitFunc = new TF1("fTOFfit", "gaus", -5000, 5000);

  fitFunc->SetParameter(0, 100);
  fitFunc->SetParameter(1, 0);
  fitFunc->SetParameter(2, 200);

  if (mTreeFit) { // remove previous tree
    delete mTreeFit;
  }

  mTreeFit = new TChain("treeCollectedCalibInfo", "treeCollectedCalibInfo");

  auto retval = system("ls accumulated/*.root >listaCalTS"); // create list of calibInfo accumulated
  //  system("sleep 15");
  FILE* f = fopen("listaCalTS", "r");

  if (!f) { // no inputs -> return
    return 2;
  }

  char namefile[50];
  while (fscanf(f, "%s", namefile) == 1) {
    mTreeFit->AddFile(namefile);
  }

  if (!mTreeFit->GetEntries()) { // return if no entry available
    return 3;
  }

  mTreeFit->SetBranchAddress("TOFCollectedCalibInfo", &mPvectC);

  for (int isec = firstSect; isec < lastSect+1; isec++) {
    fitTimeSlewing(isec, oldTS, newTS);

    TFile *fsl = new TFile(Form("newtsNew_%d.root",isec),"RECREATE");
    fsl->WriteObjectAny(tsNew, tsNew->Class(), "ccdb_object");
    fsl->Close();
  }

  return 0;
}

void fitTimeSlewing(int sector, const o2::dataformats::CalibTimeSlewingParamTOF* oldTS, o2::dataformats::CalibTimeSlewingParamTOF* newTS)
{
  const int nchPerSect = o2::tof::Geo::NCHANNELS / o2::tof::Geo::NSECTORS;
  for (int i = sector * nchPerSect; i < (sector + 1) * nchPerSect; i += NCHPERBUNCH) {
    fitChannelsTS(i, oldTS, newTS);
  }
}

void fitChannelsTS(int chStart, const o2::dataformats::CalibTimeSlewingParamTOF* oldTS, o2::dataformats::CalibTimeSlewingParamTOF* newTS)
{
  // fiting NCHPERBUNCH at the same time to optimze reading from tree
  TH2F* h[NCHPERBUNCH];
  float time, tot;
  int mask;
  int bcSel[NCHPERBUNCH];

  for (int ii = 0; ii < NCHPERBUNCH; ii++) {
    h[ii] = new TH2F(Form("h%d", chStart + ii), "", 10000, 0, 100, 100, -5000, 5000);
    bcSel[ii] = -9999;
  }

  int counts = 0;
  for (long i = chStart; i + NCHPERBUNCH < mTreeFit->GetEntries(); i += 157248) {
    if(!(counts % 20)){
      printf("%ld / %lld\n",i,mTreeFit->GetEntries());
    }
    counts++;
    for (int ii = 0; ii < NCHPERBUNCH; ii++) {
      int ch = chStart + ii;
      mTreeFit->GetEvent(i + ii);
      int k = 0;
      bool skip = false;
      for (auto& obj : mVectC) {
        // if (obj.getTOFChIndex() != ch || skip) {
        //   printf("skip %d != %d\n",obj.getTOFChIndex(),ch);
        //   continue;
        // }

        time = obj.getDeltaTimePi();
        tot = obj.getTot();
        mask = 256;//obj.getMask();
        time -= o2::tof::Utils::addMaskBC(mask, ch) * o2::tof::Geo::BC_TIME_INPS;

        float tscorr;
        if(!useOnlyOldOffsets){
          tscorr = oldTS->evalTimeSlewing(ch, tot);
        } else {
          tscorr = oldTS->getChannelOffset(ch);
        }
        if (tscorr < -1000000 || tscorr > 1000000) {
          skip = true;
          continue;
        }
        time -= tscorr;

        if (bcSel[ii] > -9000) {
          time += bcSel[ii] * o2::tof::Geo::BC_TIME_INPS;
        } else {
          bcSel[ii] = 0;
        }
        while (time < -5000) {
          time += o2::tof::Geo::BC_TIME_INPS;
          bcSel[ii] += 1;
        }
        while (time > 20000) {
          time -= o2::tof::Geo::BC_TIME_INPS;
          bcSel[ii] -= 1;
        }

        // adjust to avoid borders effect
        if (time > 12500) {
          time -= o2::tof::Geo::BC_TIME_INPS;
        } else if (time < -12500) {
          time += o2::tof::Geo::BC_TIME_INPS;
        }

        h[ii]->Fill(tot, time);
      }
    }
  }

  printf("Fit\n");
  for (int ii = 0; ii < NCHPERBUNCH; ii++) {
    if(!(ii%500) || 1){
      printf("Fitting %d\n",chStart + ii);
    }
    mNfits += fitSingleChannel(chStart + ii, h[ii], oldTS, newTS);
    delete h[ii]; // clean histo once fitted
  }
}

int fitSingleChannel(int ch, TH2F* h, const o2::dataformats::CalibTimeSlewingParamTOF* oldTS, o2::dataformats::CalibTimeSlewingParamTOF* newTS)
{
  const int nchPerSect = o2::tof::Geo::NCHANNELS / o2::tof::Geo::NSECTORS;

  int fitted = 0;
  float offset = oldTS->getChannelOffset(ch);
  int sec = ch / nchPerSect;
  int chInSec = ch % nchPerSect;
  int istart = oldTS->getStartIndexForChannel(sec, chInSec);
  int istop = oldTS->getStopIndexForChannel(sec, chInSec);
  int nbinPrev = istop - istart;
  int np = 0;

  unsigned short oldtot[10000];
  short oldcorr[10000];
  unsigned short newtot[10000];
  short newcorr[10000];
  float newcorrF[10000];

  int count = 0;

  const std::vector<std::pair<unsigned short, short>>& vect = oldTS->getVector(sec);
  for (int i = istart; i < istop; i++) {
    oldtot[count] = vect[i].first;
    oldcorr[count] = vect[i].second;
    count++;
  }

  TH1D* hpro = h->ProjectionX("hpro");

  int ibin = 1;
  int nbin = h->GetXaxis()->GetNbins();
  float integralToEnd = h->Integral();

  if (nbinPrev == 0) {
    nbinPrev = 1;
    oldtot[0] = 0;
    oldcorr[0] = 0;
  }

  if(useOnlyOldOffsets){
    // not using TS from old
    nbinPrev = 1;
    oldtot[0] = 0;
    oldcorr[0] = 0;
  }

  // propagate problematic from old TS
  newTS->setFractionUnderPeak(sec, chInSec, oldTS->getFractionUnderPeak(ch));
  newTS->setSigmaPeak(sec, chInSec, oldTS->getSigmaPeak(ch));
  bool isProb = oldTS->getFractionUnderPeak(ch) < 0.5 || oldTS->getSigmaPeak(ch) > 1000;

  /*
  if (isProb) { // if problematic
    // skip fit procedure
    integralToEnd = 0;
  }
  */
  
  if (integralToEnd < NMINTOFIT) { // no update to be done
    np = 1;
    newtot[0] = 0;
    newcorr[0] = 0;
    newTS->setTimeSlewingInfo(ch, offset, nbinPrev, oldtot, oldcorr, np, newtot, newcorr);
    if (hpro) {
      delete hpro;
    }
    return fitted;
  }

  float totHalfWidth = h->GetXaxis()->GetBinWidth(1) * 0.5;

  static TF1* fitFunc = new TF1("fTOFfit", "gaus", -5000, 5000);

  int integral = 0;
  float x[10000], y[10000];
  float minV = 100000;
  float maxV = -100000;
  for (int i = 1; i <= nbin; i++) {
    integral += hpro->GetBinContent(i);
    integralToEnd -= hpro->GetBinContent(i);

    if (integral < NMINTOFIT || (integralToEnd < NMINTOFIT && i < nbin)) {
      continue;
    }

    // get a point
    float xmin = h->GetXaxis()->GetBinCenter(ibin) - totHalfWidth;
    float xmax = h->GetXaxis()->GetBinCenter(i) + totHalfWidth;
    TH1D* hfit = h->ProjectionY(Form("mypro"), ibin, i);
    float xref = hfit->GetBinCenter(hfit->GetMaximumBin());

    hfit->Fit(fitFunc, "QN0", "", xref - 500, xref + 500);
    fitted++;

    x[np] = xmin;//(xmin + xmax) * 0.5;
    y[np] = fitFunc->GetParameter(1);
    if (x[np] > 65.534) {
      continue; // max tot acceptable in ushort representation / 1000.
    }
    
    if(y[np] > maxV){
      maxV = y[np];
    }		   
    if(y[np] < minV){
      minV = y[np];
    }		          
    
    newtot[np] = x[np] * 1000;
    newcorrF[np] = y[np];
    np++;
    ibin = i + 1;
    integral = 0;
    delete hfit;
  }

  float recentering = (minV + maxV)*0.5;
  for (int i = 0; i < np; i++) {
    newcorr[i] = short(newcorrF[i] - recentering);
  }
  offset += recentering;
    
  newTS->setTimeSlewingInfo(ch, offset, nbinPrev, oldtot, oldcorr, np, newtot, newcorr);

  if (hpro) {
    delete hpro;
  }
  return fitted;
}
