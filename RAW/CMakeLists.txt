add_executable(atc-file-proxy src/file-proxy.cc)
target_link_libraries(atc-file-proxy
  PUBLIC
  PRIVATE
  FairMQ::FairMQ
  AliceO2::Framework
  ROOT::Core
  ms_gsl::ms_gsl
  arrow::arrow_shared
  arrow::gandiva_shared
  )
install(TARGETS atc-file-proxy RUNTIME DESTINATION bin)

add_executable(atc-writer-proxy src/writer-proxy.cc)
target_link_libraries(atc-writer-proxy
  PUBLIC
  PRIVATE
  FairMQ::FairMQ
  AliceO2::Framework
  AliceO2::Headers
  ROOT::Core
  ms_gsl::ms_gsl
  arrow::arrow_shared
  arrow::gandiva_shared
  )
install(TARGETS atc-writer-proxy RUNTIME DESTINATION bin)

if(TOFBUF_FOUND)

set(CMAKE_VERBOSE_MAKEFILE ON)

add_executable(atc-scl-proxy src/scl-proxy.cc ${TOFBUF_SOURCES})
target_include_directories(atc-scl-proxy PRIVATE ${TOFBUF_INCLUDE_DIRS})
target_link_libraries(atc-scl-proxy
  PUBLIC
  PRIVATE
  FairMQ::FairMQ
  AliceO2::Framework
  ROOT::Core
  ms_gsl::ms_gsl
  arrow::arrow_shared
  arrow::gandiva_shared
  )
install(TARGETS atc-scl-proxy RUNTIME DESTINATION bin)
endif()
