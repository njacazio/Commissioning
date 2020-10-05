#include "CompressedAnalysis.h"
#include <iostream>

using namespace o2::tof::compressed;

class DiagnosticsAnalysis : public o2::tof::CompressedAnalysis
{
public:
  DiagnosticsAnalysis() = default;
  ~DiagnosticsAnalysis() = default;

  bool initialize() final;
  bool finalize() final;

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

  std::string mFileName = "noise_analysis.root";
  int mDiagnostics[72][12][32]; // [crate][slot][bit]

};

bool
DiagnosticsAnalysis::initialize()
{
  std::cout << "--- initialize DiagnosticsAnalysis" << std::endl;
  for (int icrate = 0; icrate < 72; ++icrate)
    for (int islot = 0; islot < 12; ++islot)
      for (int ibit = 0; ibit < 32; ++ibit)
	mDiagnostics[icrate][islot][ibit] = 0;
  return true;
}
  
bool
DiagnosticsAnalysis::finalize()
{
  std::cout << "--- finalize DiagnosticsAnalysis" << std::endl;
  TFile fout(mFileName.c_str(), "RECREATE");
  for (int icrate = 0; icrate < 72; ++icrate) {
    TH2F h(Form("hDiagnostics_%02d", icrate), ";bit;slot", 32, 0., 32., 12, 1., 13.);
    for (int islot = 0; islot < 32; ++islot) {
      for (int ibit = 0; ibit < 32; ++ibit) {
	h.SetBinContent(ibit + 1, islot + 1, mDiagnostics[icrate][islot][ibit]);
      }
    }
    h.Write();
  }
  fout.Close();
  return true;
}
  
void DiagnosticsAnalysis::headerHandler(const CrateHeader_t* crateHeader,
					 const CrateOrbit_t* crateOrbit)
{
  auto drmID = crateHeader->drmID;
  auto slotPartMask = crateHeader->slotPartMask;
  mDiagnostics[drmID][0][0]++;
  for (int ibit = 0; ibit < 11; ++ibit)
    if (slotPartMask & (1 << ibit))
      mDiagnostics[drmID][ibit + 1][0]++;
}

void DiagnosticsAnalysis::frameHandler(const CrateHeader_t* crateHeader,
					const CrateOrbit_t* crateOrbit,
					const FrameHeader_t* frameHeader,
					const PackedHit_t* packedHits)
{}

void DiagnosticsAnalysis::trailerHandler(const CrateHeader_t* crateHeader,
					  const CrateOrbit_t* crateOrbit,
					  const CrateTrailer_t* crateTrailer,
					  const Diagnostic_t* diagnostics,
					  const Error_t* errors)
{
  auto drmID = crateHeader->drmID;
  for (int i = 0; i < crateTrailer->numberOfDiagnostics; ++i) {
    auto diagnostic = diagnostics + i;
    auto slotID = diagnostic->slotID;
    auto faultBits = diagnostic->faultBits;
    for (int ibit = 0; ibit < 28; ++ibit)
      if (faultBits & (1 << ibit))
	mDiagnostics[drmID][slotID - 1][ibit + 4]++;
  }
}

o2::tof::CompressedAnalysis*
diagnostic_analysis(std::string fileName = "diagnostic_analysis.root")
{
  auto analysis = new DiagnosticsAnalysis;
  analysis->setFileName(fileName);
  return analysis;
}

