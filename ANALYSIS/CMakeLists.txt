add_executable(atc-compressed-analysis src/compressed-analysis.cc)
target_link_libraries(atc-compressed-analysis
  PUBLIC
  PRIVATE
  FairMQ::FairMQ
  AliceO2::Framework
  AliceO2::Headers
  AliceO2::TOFReconstruction
  ROOT::Core
  ROOT::Hist
  ms_gsl::ms_gsl
  arrow::arrow_shared
  arrow::gandiva_shared
  )
install(TARGETS atc-compressed-analysis RUNTIME DESTINATION bin)
