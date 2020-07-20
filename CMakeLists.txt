project(TOFCommissioning)
cmake_minimum_required(VERSION 3.13 FATAL_ERROR)

cmake_policy(SET CMP0074 NEW)
cmake_policy(SET CMP0065 NEW)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

find_package(fmt REQUIRED)
find_package(ms_gsl REQUIRED)
find_package(O2arrow REQUIRED)
find_package(Threads REQUIRED)
find_package(FairMQ 1.4 REQUIRED)
find_package(FairLogger ${FairMQ_FairLogger_VERSION} REQUIRED)
find_package(Boost ${FairMQ_Boost_VERSION} REQUIRED COMPONENTS ${FairMQ_Boost_COMPONENTS})

find_package(AliceO2 REQUIRED)
find_package(ROOT REQUIRED)

find_package(tofbuf)

include_directories(${CMAKE_CURRENT_SOURCE_DIR} ${Boost_INCLUDE_DIR})

add_subdirectory(RAW)
