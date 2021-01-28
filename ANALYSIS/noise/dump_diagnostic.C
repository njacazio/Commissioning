#include "DataFormatsTOF/CompressedDataFormat.h"

void
dump_diagnostic(const char *fnamein)
{

  auto fin = TFile::Open(fnamein);
  std::ofstream fout;
  std::string fnameout = fnamein;
  size_t lastindex = fnameout.find_last_of("."); 
  fnameout = fnameout.substr(0, lastindex) + ".diagnostic"; 
  fout.open(fnameout.c_str(), std::ios::out);
  fout << std::fixed << std::setprecision(3);
  fout << "# drm \t slot \t frac. \t what" << std::endl;

  // loop over crates
  for (int icrate = 0; icrate < 72; ++icrate) {

    auto h = (TH2*)fin->Get(Form("hDiagnostic_%02d", icrate));
    if (!h) continue; // no diagnostic for this crate

    // loop over slots
    for (int islot = 1; islot <= 12; ++islot) {
      float ndata = h->GetBinContent(1, islot);
      if (ndata <= 0) continue; // no data from this slot

      // loop over bits
      for (int ibit = 4; ibit < 32; ++ibit) {

	float nbit = h->GetBinContent(ibit + 1, islot);
	if (nbit <= 0) continue; // no occurrence in this bit
	float freq = nbit / ndata;

	if (islot == 1)      fout << icrate <<  "\t" << islot << "\t" << freq << "\t" << o2::tof::diagnostic::DRMDiagnosticName[ibit] << std::endl;
	else if (islot == 2) fout << icrate <<  "\t" << islot << "\t" << freq << "\t" << o2::tof::diagnostic::LTMDiagnosticName[ibit] << std::endl;
	else           	     fout << icrate <<  "\t" << islot << "\t" << freq << "\t" << o2::tof::diagnostic::TRMDiagnosticName[ibit] << std::endl;
	
      }
    }
    
  }

  fin->Close();
  fout.close();
}
