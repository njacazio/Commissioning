#include "/home/alidock/TOFCommissioning/ANALYSIS/src/compressed-analysis.hh"
#include <iostream>

using namespace o2::tof::compressed;

class TimingAnalysis : public CompressedAnalysis
{
public:
  TimingAnalysis() = default;
  ~TimingAnalysis() = default;

  bool initialize() final;
  bool finalize() final;

private:

  void rdhHandler(const o2::header::RAWDataHeaderV6* rdh) final {};
  
  void headerHandler(const CrateHeader_t* crateHeader,
		     const CrateOrbit_t* crateOrbit) final {};
  
  void frameHandler(const CrateHeader_t* crateHeader,
		    const CrateOrbit_t* crateOrbit,
                    const FrameHeader_t* frameHeader,
		    const PackedHit_t* packedHits) final;
  
  void trailerHandler(const CrateHeader_t* crateHeader,
		      const CrateOrbit_t* crateOrbit,
                      const CrateTrailer_t* crateTrailer,
		      const Diagnostic_t* diagnostics,
                      const Error_t* errors) final {};  

  TH1 *mIndex = nullptr;
  TH2 *mTimeZ = nullptr;
  
};

bool
TimingAnalysis::initialize()
{
  std::cout << "--- initialize TimingAnalysis" << std::endl;
  mIndex = new TH1F("hIndex", "", 157248, 0., 157248.);
  mTimeZ = new TH2F("hTimeZ", ";z (cm);time % BC (ns)", 100, -500., 500., 2048, -24.9508, 24.9508);
  return true;
}
  
bool
TimingAnalysis::finalize()
{
  std::cout << "--- finalize TimingAnalysis" << std::endl;
  TFile fout("timing.root", "RECREATE");
  mIndex->Write();
  mTimeZ->Write();
  fout.Close();
  return true;
}
  
void TimingAnalysis::frameHandler(const CrateHeader_t* crateHeader,
					const CrateOrbit_t* crateOrbit,
					const FrameHeader_t* frameHeader,
					const PackedHit_t* packedHits)
{
  int det[5];
  float pos[3];
  for (int i = 0; i < frameHeader->numberOfHits; ++i) {
    auto packedHit = packedHits + i;
    auto drmID = crateHeader->drmID;
    auto trmID = frameHeader->trmID;
    auto chain = packedHit->chain;
    auto tdcID = packedHit->tdcID;
    auto channel = packedHit->channel;
    auto eindex = o2::tof::Geo::getECHFromIndexes(drmID, trmID, chain, tdcID, channel);
    auto index = o2::tof::Geo::getCHFromECH(eindex);
    o2::tof::Geo::getVolumeIndices(index, det);
    o2::tof::Geo::getPos(det, pos);
    int time = packedHit->time;
    int timebc = time % 1024;
    time += (frameHeader->frameID << 13);

    double timens = timebc * o2::tof::Geo::TDCBIN * 1.e-3;
    double Lc = sqrt(pos[0] * pos[0] + pos[1] * pos[1] + pos[2] * pos[2]) * 0.033356409;
    
    mIndex->Fill(index);
    mTimeZ->Fill(pos[2], timens - Lc);
  }
}

CompressedAnalysis*
timing()
{
  return new TimingAnalysis;
}

