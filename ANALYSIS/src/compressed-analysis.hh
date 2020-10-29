/// @author Roberto Preghenella
/// @since  2020-07-26

#include "Headers/RAWDataHeader.h"
#include "DataFormatsTOF/CompressedDataFormat.h"
#include "TOFReconstruction/DecoderBase.h"

using namespace o2::tof::compressed;

class CompressedAnalysis : public DecoderBaseT<o2::header::RAWDataHeaderV6>
{

public:
  CompressedAnalysis() = default;
  ~CompressedAnalysis() = default;

  virtual bool initialize() = 0;
  virtual bool finalize() = 0;

private:

};
