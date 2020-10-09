#include "TOFWorkflowUtils/CompressedAnalysis.h"
#include <iostream>

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
                      const Error_t* errors) final {};  

  int mTimeMin = 4096;
  int mTimeMax = 36864;

  int mCrateCounter[72] = {0};
  int mIndexCounter[172800] = {0};

  std::string mFileName = "noise_analysis.root";
  
  TH1 *hRuns = nullptr;
  TH1 *hTimeWin = nullptr;
  TH1 *hCrateCounter = nullptr;
  TH1 *hIndexCounter = nullptr;
  TH2 *hTRMTime = nullptr;
  
  
};

bool
NoiseAnalysis::initialize()
{
  std::cout << "--- initialize NoiseAnalysis" << std::endl;
  hRuns = new TH1F("hRuns", "", 1, 0., 1.);
  hTimeWin = new TH1F("hTimeWin", "", 1, 0., 1.);
  hCrateCounter = new TH1F("hCrateCounter", "", 72, 0., 72.);
  hIndexCounter = new TH1F("hIndexCounter", "", 172800, 0., 172800.);
  hTRMTime = new TH2F("hTRMTime", ";TRM id;hit time", 720, 0., 720., 16384, 0., 2097152.);
  return true;
}


bool
NoiseAnalysis::finalize()
{
  std::cout << "--- finalize NoiseAnalysis" << std::endl;
  TFile fout(mFileName.c_str(), "RECREATE");

  hRuns->SetBinContent(1, 1.);
  hRuns->Write();
  
  hTimeWin->SetBinContent(1, mTimeMax - mTimeMin);
  hTimeWin->Write();

  for (int i = 0; i < 72; ++i) hCrateCounter->SetBinContent(i + 1, mCrateCounter[i]);
  hCrateCounter->Write();

  for (int i = 0; i < 172800; ++i) hIndexCounter->SetBinContent(i + 1, mIndexCounter[i]);
  hIndexCounter->Write();

  hTRMTime->Write();

  fout.Close();

  return true;
}
  
void NoiseAnalysis::headerHandler(const CrateHeader_t* crateHeader,
				  const CrateOrbit_t* crateOrbit)
{
  auto drmID = crateHeader->drmID;   // [0-71]
  mCrateCounter[drmID]++;
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

    hTRMTime->Fill((trmID - 3) + (10 * drmID) , time);

    if (time < mTimeMin) continue;
    if (time >= mTimeMax) continue;
    mIndexCounter[index]++;

  }
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

