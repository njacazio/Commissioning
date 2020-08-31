#if !defined(__CLING__) || defined(__ROOTCLING__)
#include "FairGenerator.h"
#include "FairPrimaryGenerator.h"
#include "TRandom3.h"
#include <iostream>
#endif

class GeneratorCosmic : public FairGenerator
{
 public:
  GeneratorCosmic() : FairGenerator("GeneratorCosmic") {};
  Bool_t ReadEvent(FairPrimaryGenerator* primGen) override;

 private:
  TRandom3 random;
  int pdg = 13;
  double mass = 0.10565800;
  double momentum = 100.;
};

Bool_t
GeneratorCosmic::ReadEvent(FairPrimaryGenerator* primGen)
{

  double s1 = random.Uniform(-800., 800.);
  double s2 = 800.;
  double s3 = random.Uniform(-800., 800.);
  
  double theta = std::acos(std::sqrt(random.Uniform(0., 1.)));
  double phi = random.Uniform(0., 2. * M_PI);

  double n1 = std::sin(theta) * std::cos(phi);
  double n2 = -std::cos(theta);
  double n3 = std::sin(theta) * std::sin(phi);

  
  double vx = s1;
  double vy = s2;
  double vz = s3;
  double vt = random.Uniform(-25., 25.);
    
  double px = momentum * n1;
  double py = momentum * n2;
  double pz = momentum * n3;
  double e = sqrt(mass * mass + momentum * momentum);
    
  int parent = -1;
  bool wanttracking = true;
  double weight = 1.;
  TMCProcess proc = kPPrimary;
    
  primGen->AddTrack(pdg, px, py, pz, vx, vy, vz, parent, wanttracking, e, vt, weight, proc);

  return kTRUE;
};

			   
FairGenerator*
cosmicGenerator()
{
  return new GeneratorCosmic();
}
