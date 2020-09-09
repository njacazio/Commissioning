// build me with
// g++ -o epn2raw epn2raw.cc

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

int
main(int argc, char **argv)
{
  if (argc != 3) {
    std::cerr << "usage: ./epn2raw [filename.tf] [shift]" << std::endl;
    return 1;
  }
  int shift = atoi(argv[2]);

  // input file
  std::ifstream infile;
  std::string infilename = std::string(argv[1]);
  infile.open(infilename.c_str(), std::ios_base::binary);
  if (!infile.is_open()) {
    std::cerr << "cannot open input file: " << infilename << std::endl;
    return 1;
  }

  // output file
  std::ofstream outfile;
  std::string outfilename = std::string(argv[1]) + ".raw";
  outfile.open(outfilename.c_str(), std::ios_base::binary);
  if (!outfile.is_open()) {
    std::cerr << "cannot open output file: " << outfilename << std::endl;
    return 1;
  }

  // info file
  std::ifstream infofile;
  std::string infofilename = std::string(argv[1]) + ".info";
  infofile.open(infofilename.c_str());
  if (!infofile.is_open()) {
    std::cerr << "cannot open info file: " << infofilename << std::endl;
    return 1;
  }

  // process
  char buffer[1048576];
  std::string line, cell;
  long offset, memory;
  std::getline(infofile, line); // first line is a header
  while (std::getline(infofile, line)) {
    std::stringstream linestream;
    linestream << line;
    for (int i = 0; i < 9; ++i) linestream >> cell;
    linestream >> offset >> memory;

    infile.seekg(offset - shift);
    infile.read(buffer, memory);

    /** check for consistency **/
    uint32_t *RDHs = reinterpret_cast<uint32_t *>(buffer);
    if (*RDHs != 0x00044004) {
      printf(" --- wrong RDH signature at offset %ld : %08x \n ", offset, *RDHs);
      break;
    }

    outfile.write(buffer, memory);
  }

  infile.close();
  outfile.close();
  infofile.close();
}
