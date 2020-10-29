/// @author Roberto Preghenella
/// @since  2020-04-01

#include "Framework/Task.h"
#include "Framework/WorkflowSpec.h"
#include "Framework/ConfigParamSpec.h"
#include "Framework/ConfigParamRegistry.h"
#include "Framework/ControlService.h"
#include "Framework/CallbackService.h"
#include "Framework/ConcreteDataMatcher.h"
#include <fairmq/FairMQDevice.h>

using namespace o2::framework;

class WriterProxyTask : public Task
{
 public:
  WriterProxyTask() = default;
  ~WriterProxyTask() override = default;

  void init(InitContext& ic) final;
  void run(ProcessingContext& pc) final;
  
 private:

  bool mStatus = false;
  std::ofstream mFile;

};

void
WriterProxyTask::init(InitContext& ic)
{
  auto filename = ic.options().get<std::string>("writer-proxy-filename");

  /** open output file **/
  std::cout << " --- Opening output file: " << filename << std::endl;
  mFile.open(filename, std::fstream::out | std::fstream::binary);
  if (!mFile.is_open()) {
    std::cout << " --- Cannot open output file: " << strerror(errno) << std::endl;
    mStatus = true;
  }

}

void
WriterProxyTask::run(ProcessingContext& pc)
{

  /** check status **/
  if (mStatus) {
    if (mFile.is_open())
      mFile.close();
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

      /** write **/
      mFile.write(payloadIn, payloadInSize);
      
    }
  }
}

// add workflow options, note that customization needs to be declared before
// including Framework/runDataProcessing
void customize(std::vector<ConfigParamSpec>& workflowOptions)
{
  auto inputSpec = ConfigParamSpec{"writer-proxy-input-spec", VariantType::String, "x:TOF/RAWDATA", {"Input spec string"}};
  workflowOptions.push_back(inputSpec);
}

#include "Framework/runDataProcessing.h" // the main driver

/// This function hooks up the the workflow specifications into the DPL driver.
WorkflowSpec defineDataProcessing(ConfigContext const& cfgc)
{
  auto inputSpec = cfgc.options().get<std::string>("input-spec");
  
  return WorkflowSpec {
    DataProcessorSpec {"writer-proxy",
	select(inputSpec.c_str()),
	Outputs{},
	AlgorithmSpec(adaptFromTask<WriterProxyTask>()),
	Options{
	  {"writer-proxy-filename", VariantType::String, "writer-proxy.dat", {"Output file name"}}}
    }
  };
}
