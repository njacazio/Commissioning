#include "TOFWorkflowUtils/CompressedAnalysis.h"
#include <iostream>

//#define FILLHITTIME
#define FILLDIAGNOSTIC
#define LOGTOFIFO

class NoiseAnalysis : public o2::tof::CompressedAnalysis
{
public:
  NoiseAnalysis() = default;
  ~NoiseAnalysis() = default;

  bool initialize() final;
  bool finalize() final;

  void setTimeMin(int val) { mTimeMin = val; };
  void setTimeMax(int val) { mTimeMax = val; };

  void setFileName(std::string val) { mFileName = val; };
  
private:

  void rdhHandler(const o2::header::RAWDataHeaderV6* rdh) final {};
  
  void headerHandler(const CrateHeader_t* crateHeader,
		     const CrateOrbit_t* crateOrbit) final;
  
  void frameHandler(const CrateHeader_t* crateHeader,
		    const CrateOrbit_t* crateOrbit,
                    const FrameHeader_t* frameHeader,
		    const PackedHit_t* packedHits) final;
  
  void trailerHandler(const CrateHeader_t* crateHeader,
		      const CrateOrbit_t* crateOrbit,
                      const CrateTrailer_t* crateTrailer,
		      const Diagnostic_t* diagnostics,
                      const Error_t* errors) final;  

  int mTimeMin = 4096;
  int mTimeMax = 36864;

  int mCrateCounter[72] = {0};
  int mIndexCounter[172800] = {0};
#ifdef FILLDIAGNOSTIC
  int mDiagnostics[72][12][32] = {0}; // [crate][slot][bit]
#endif
  
  std::string mFileName = "noise_analysis.root";

#ifdef FILLHITTIME
  TH2 *hTRMTime = nullptr;
#endif
  
};

bool
NoiseAnalysis::initialize()
{
  std::cout << "--- initialize NoiseAnalysis" << std::endl;
#ifdef FILLHITTIME
  hTRMTime = new TH2F("hTRMTime", ";TRM id;hit time", 720, 0., 720., 16384, 0., 2097152.);
#endif
  return true;
}


bool
NoiseAnalysis::finalize()
{
  std::cout << "--- finalize NoiseAnalysis" << std::endl;
  TFile fout(mFileName.c_str(), "RECREATE");

  TH1F hRuns("hRuns", "", 1, 0., 1.);
  hRuns.SetBinContent(1, 1.);
  hRuns.Write();
  
  TH1F hTimeWin("hTimeWin", "", 1, 0., 1.);
  hTimeWin.SetBinContent(1, mTimeMax - mTimeMin);
  hTimeWin.Write();

  TH1F hCrateCounter("hCrateCounter", "", 72, 0., 72.);
  for (int i = 0; i < 72; ++i)
    hCrateCounter.SetBinContent(i + 1, mCrateCounter[i]);
  hCrateCounter.Write();
  
  TH1F hIndexCounter("hIndexCounter", "", 172800, 0., 172800.);
  for (int i = 0; i < 172800; ++i)
    hIndexCounter.SetBinContent(i + 1, mIndexCounter[i]);
  hIndexCounter.Write();
  
#ifdef FILLDIAGNOSTIC
  for (int icrate = 0; icrate < 72; ++icrate) {
    if (mDiagnostics[icrate][0][0] == 0) continue;
    TH2F hDiagnostic(Form("hDiagnostic_%02d", icrate), ";bit;slot", 32, 0., 32., 12, 1., 13.);
    for (int islot = 0; islot < 32; ++islot) {
      for (int ibit = 0; ibit < 32; ++ibit) {
	hDiagnostic.SetBinContent(ibit + 1, islot + 1, mDiagnostics[icrate][islot][ibit]);
      }
    }
    hDiagnostic.Write();
  }
#endif
  
  
#ifdef FILLHITTIME
  hTRMTime->Write();
#endif
  
  fout.Close();

  return true;
}
  
void NoiseAnalysis::headerHandler(const CrateHeader_t* crateHeader,
				  const CrateOrbit_t* crateOrbit)
{
  auto drmID = crateHeader->drmID;   // [0-71]
  mCrateCounter[drmID]++;

#ifdef FILLDIAGNOSTIC
  mDiagnostics[drmID][0][0]++;
  auto slotPartMask = crateHeader->slotPartMask;
  for (int ibit = 0; ibit < 11; ++ibit)
    if (slotPartMask & (1 << ibit))
      mDiagnostics[drmID][ibit + 1][0]++;
#endif
}
  

void NoiseAnalysis::frameHandler(const CrateHeader_t* crateHeader,
				 const CrateOrbit_t* crateOrbit,
				 const FrameHeader_t* frameHeader,
				 const PackedHit_t* packedHits)
{
 

  for (int i = 0; i < frameHeader->numberOfHits; ++i) {
    auto packedHit = packedHits + i;

    int time = packedHit->time + (frameHeader->frameID << 13); // [24.4 ps]
    
    auto drmID = crateHeader->drmID;   // [0-71]
    auto trmID = frameHeader->trmID;   // [3-12]
    auto chain = packedHit->chain;     // [0-1]
    auto tdcID = packedHit->tdcID;     // [0-14]
    auto channel = packedHit->channel; // [0-7]
    auto index = channel + 8 * tdcID + 120 * chain + 240 * (trmID - 3) + 2400 * drmID; // [0-172799]

#ifdef FILLHITTIME
    hTRMTime->Fill((trmID - 3) + (10 * drmID) , time);
#endif
    
    if (time < mTimeMin) continue;
    if (time >= mTimeMax) continue;
    mIndexCounter[index]++;

  }
}

void NoiseAnalysis::trailerHandler(const CrateHeader_t* crateHeader,
				   const CrateOrbit_t* crateOrbit,
				   const CrateTrailer_t* crateTrailer,
				   const Diagnostic_t* diagnostics,
				   const Error_t* errors)
{
#ifdef FILLDIAGNOSTIC
  auto drmID = crateHeader->drmID;
  for (int i = 0; i < crateTrailer->numberOfDiagnostics; ++i) {
    auto diagnostic = diagnostics + i;
    auto slotID = diagnostic->slotID;
    auto faultBits = diagnostic->faultBits;
    for (int ibit = 0; ibit < 28; ++ibit)
      if (faultBits & (1 << ibit))
	mDiagnostics[drmID][slotID - 1][ibit + 4]++;
  }
#endif
}

o2::tof::CompressedAnalysis*
noise_analysis(int timeMin = 4096, int timeMax = 36864, std::string fileName = "noise_analysis.root")
{
  auto analysis = new NoiseAnalysis;
  analysis->setTimeMin(timeMin);
  analysis->setTimeMax(timeMax);
  analysis->setFileName(fileName);
  analysis->setDecoderVerbose(false);
  return analysis;
}

