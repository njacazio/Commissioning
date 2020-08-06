/// @author Roberto Preghenella
/// @since  2020-07-26

#include "Framework/Task.h"
#include "Framework/WorkflowSpec.h"
#include "Framework/ConfigParamSpec.h"
#include "Framework/ConfigParamRegistry.h"
#include "Framework/ControlService.h"
#include "Framework/CallbackService.h"
#include "Framework/ConcreteDataMatcher.h"
#include "Framework/RawDeviceService.h"
#include "Framework/DeviceSpec.h"
#include <fairmq/FairMQDevice.h>

#include "ConfigurationMacroHelper.h"
#include "compressed-analysis.hh"

using namespace o2::framework;

class CompressedAnalysisTask : public Task
{
public:
  CompressedAnalysisTask() = default;
  ~CompressedAnalysisTask() = default;

  void init(InitContext& ic) final;
  void run(ProcessingContext& pc) final;
  
 private:

  CompressedAnalysis* mAnalysis = nullptr;
  bool mStatus = false;
};

void
CompressedAnalysisTask::init(InitContext& ic)
{
  LOG(INFO) << "CompressedBaseTask init";

  auto conetmode = ic.options().get<bool>("atc-compressed-analysis-conet-mode");
  auto filename = ic.options().get<std::string>("atc-compressed-analysis-filename");
  auto function = ic.options().get<std::string>("atc-compressed-analysis-function");

  if (filename.empty()) {
    LOG(ERROR) << "No analysis filename defined";
    mStatus = true;
    return;
  }
  
  if (function.empty()) {
    LOG(ERROR) << "No analysis function defined";
    mStatus = true;
    return;
  }
  
  mAnalysis = GetFromMacro<CompressedAnalysis*>(filename, function, "CompressedAnalysis*", "compressed_analysis");
  if (!mAnalysis) {
    LOG(ERROR) << "Could not retrieve analysis from file: " << filename;
    mStatus = true;
    return;
  }
  
  mAnalysis->setDecoderCONET(conetmode);
  mAnalysis->initialize();

  auto finishFunction = [this]() {
    LOG(INFO) << "CompressedBaseTask finish";
    mAnalysis->finalize();
  };
  ic.services().get<CallbackService>().set(CallbackService::Id::Stop, finishFunction);

};

void
CompressedAnalysisTask::run(ProcessingContext& pc)
{
  
  /** check status **/
  if (mStatus) {
    pc.services().get<ControlService>().readyToQuit(QuitRequest::Me);
    return;
  }

  /** loop over inputs routes **/
  for (auto iit = pc.inputs().begin(), iend = pc.inputs().end(); iit != iend; ++iit) {
    if (!iit.isValid())
      continue;

    /** loop over input parts **/
    for (auto const& ref : iit) {

      const auto* headerIn = DataRefUtils::getHeader<o2::header::DataHeader*>(ref);
      auto payloadIn = ref.payload;
      auto payloadInSize = headerIn->payloadSize;

      mAnalysis->setDecoderBuffer(payloadIn);
      mAnalysis->setDecoderBufferSize(payloadInSize);
      mAnalysis->run();
    }
  }
};

// add workflow options, note that customization needs to be declared before
// including Framework/runDataProcessing
void customize(std::vector<ConfigParamSpec>& workflowOptions)
{}

#include "Framework/runDataProcessing.h" // the main driver

/// This function hooks up the the workflow specifications into the DPL driver.
WorkflowSpec defineDataProcessing(ConfigContext const& cfgc)
{
  return WorkflowSpec {
    DataProcessorSpec {"compressed-analysis",
	select("x:TOF/CRAWDATA"),
	Outputs{},
	AlgorithmSpec(adaptFromTask<CompressedAnalysisTask>()),
	Options{
	  {"atc-compressed-analysis-conet-mode", VariantType::Bool, false, {"CONET mode"}},
	  {"atc-compressed-analysis-filename", VariantType::String, "", {"Analysis file name"}},
	  {"atc-compressed-analysis-function", VariantType::String, "", {"Analysis function call"}}
	}
    }
  };
}

