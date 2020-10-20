/// @author Roberto Preghenella
/// @since  2020-03-31

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

#include "Headers/RAWDataHeader.h"
#include "DataFormatsTOF/RawDataFormat.h"

extern "C" {
#include "tofbuf.h"
};

//#define STAGING_RAM_BYTES MAXEVSIZE_B   
//#define STAGING_RAM_WORDS (STAGING_RAM_BYTES/4)

using namespace o2::framework;

class SclProxyTask : public Task
{
 public:
  SclProxyTask() { mBuffer = new char[mBufferSize]; };
  ~SclProxyTask() override { delete[] mBuffer; };

  void init(InitContext& ic) final;
  void run(ProcessingContext& pc) final;
  
 private:

  bool mStatus = false;
  bool mDumpData = false;
  bool mBlocking = false;
  bool mQuitEOT = false;
  char* mBuffer = nullptr;
  const int mBufferSize = 33554432;
  int mLinkRunning = 0;
};

void
SclProxyTask::init(InitContext& ic)
{

  mDumpData = ic.options().get<bool>("dump-data");
  mBlocking = ic.options().get<bool>("blocking");
  mQuitEOT = ic.options().get<bool>("eot-quit");

  auto rule = mBlocking ? TOFBUF_BLOCKING : TOFBUF_NOWAIT;
  std::cout << " --- tofbufRule " << (mBlocking ? "TOFBUF_BLOCKING" : "TOFBUF_NOWAIT") << std::endl; 
  tofbufRule(rule);
  if (tofbufMap() != EXIT_SUCCESS) {
    std::cout << " --- tofbufMap failure " << std::endl;
    mStatus = true;
  }
  else {
    std::cout << " --- tofbufMap success " << std::endl;
  }

};

void
SclProxyTask::run(ProcessingContext& pc)
{

  /** check status **/
  if (mStatus) {
    pc.services().get<ControlService>().endOfStream();
    pc.services().get<ControlService>().readyToQuit(QuitRequest::Me);
    return;
  }

  /** read data **/
  int bufferPayload = 0;
  int link = tofbufPop(&bufferPayload, reinterpret_cast<unsigned int *>(mBuffer));
  if (link < 0) {
    std::cout << " --- tofbufPop did not receive data: sleep 1 second and retry " << std::endl;
    sleep(1);
    return;
  }
  std::cout << " --- tofbufPop got data buffer from link #" << link << ": " << bufferPayload << " bytes" << std::endl;

  /** no payload **/
  if (bufferPayload == 0) {
    mStatus = true;
    return;
  }

  /** check tofbuf header **/
  uint32_t *word = reinterpret_cast<uint32_t *>(mBuffer);
  printf(" --- tofbufPop header: %08x (%d words, %d bytes) \n", *word, *word, *word * 4);
  if ((*word * 4) + 4 != bufferPayload) {
    std::cout << " --- tofbufPop header inconsistency " << std::endl;
    return;
  }
  char *pointer = mBuffer + 4;
  auto payload = (*word * 4);

  /** start of transmission **/
  if (tofbufCheckSOTEOT(reinterpret_cast<unsigned int *>(mBuffer)) == TOFBUF_SOT) {
    std::cout << " --- start of transmission detected from link #" << link << ": let's rock" << std::endl;
    mLinkRunning++;
    return;
  }

  /** end of transmission **/
  if (tofbufCheckSOTEOT(reinterpret_cast<unsigned int *>(mBuffer)) == TOFBUF_EOT) {
    std::cout << " --- end of transmission detected from link #" << link << std::endl;
    mLinkRunning--;
    if (mLinkRunning == 0 && mQuitEOT) {
      std::cout << " --- end of transmission detected from all links: so long, and thanks for all the bytes" << std::endl;
      mStatus = true;
    }
    return;
  }

  /** dump the data to screen **/
  if (mDumpData) {
    std::cout << " --- dump data: " << payload << " bytes" << std::endl;
    for (int i = 0; i < payload / 4; ++i) {
      word = reinterpret_cast<uint32_t *>(pointer);
      printf("     0x%08x \n", *(word + i));
    }
    std::cout << " --- end of dump data " << std::endl;
  }

  /** output **/
  auto device = pc.services().get<o2::framework::RawDeviceService>().device();
  auto outputRoutes = pc.services().get<o2::framework::RawDeviceService>().spec().outputs;
  auto fairMQChannel = outputRoutes.at(0).channel;  
  auto payloadMessage = device->NewMessage(payload);
  std::memcpy(payloadMessage->GetData(), pointer, payload);
  o2::header::DataHeader header("RAWDATA", "TOF", 0);
  header.payloadSize = payload;
  o2::framework::DataProcessingHeader dataProcessingHeader{0};
  o2::header::Stack headerStack{header, dataProcessingHeader};
  auto headerMessage = device->NewMessage(headerStack.size());
  std::memcpy(headerMessage->GetData(), headerStack.data(), headerStack.size());
  
  /** send **/
  FairMQParts parts;
  parts.AddPart(std::move(headerMessage));
  parts.AddPart(std::move(payloadMessage));
  device->Send(parts, fairMQChannel);
  
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
    DataProcessorSpec {"scl-proxy",
	Inputs{},
	Outputs{OutputSpec(ConcreteDataTypeMatcher{"TOF", "RAWDATA"})},
	AlgorithmSpec(adaptFromTask<SclProxyTask>()),
	Options{
	  {"blocking", VariantType::Bool, false, {"Blocking mode"}},
	  {"eot-quit", VariantType::Bool, false, {"Quit at EOT"}},
	  {"dump-data", VariantType::Bool, false, {"Dump data"}}}
    }
  };
}
