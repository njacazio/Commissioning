#!/usr/bin/env python3


from ROOT import o2, TFile, TF1, gROOT, gInterpreter, TPaveText


gInterpreter.Declare("""
constexpr float MassPhoton = 0.0;
constexpr float MassElectron = 0.000511;
constexpr float MassMuon = 0.105658;
constexpr float MassPionCharged = 0.139570;
constexpr float MassPionNeutral = 0.134976;
constexpr float MassKaonCharged = 0.493677;
constexpr float MassKaonNeutral = 0.497648;
constexpr float MassProton = 0.938272;
constexpr float MassLambda = 1.115683;
constexpr float MassDeuteron = 1.8756129;
constexpr float MassTriton = 2.8089211;
constexpr float MassHelium3 = 2.8083916;
constexpr float MassAlpha = 3.7273794;
constexpr float MassHyperTriton = 2.992;
constexpr float MassXiMinus = 1.32171;
constexpr float MassOmegaMinus = 1.67245;

static constexpr float kCSPEED = TMath::C() * 1.0e2f * 1.0e-12f; /// Speed of light in TOF units (cm/ps)
static constexpr float defaultReturnValue = -999.f;              /// Default return value in case TOF measurement is not available

struct DebugTrack { // Track that mimics the O2 data structure
  float mp = 0.1f;
  float p() const { return mp; }
  bool isEvTimeDefined() const { return true; }
  bool hasTOF() const { return true; }
  float tofEvTime() const { return 0.f; }
  float tofEvTimeErr() const { return 50.f; }
  float length() const { return 400.f; }
  float tofSignal() const { return length() * 1.01 / kCSPEED; }
  int trackType() const { return 0; };
  float tofExpMom() const
  {
    constexpr float mass = MassPionCharged; // default pid = pion
    const float expBeta = (length() / (tofSignal() * kCSPEED));
    return mass * expBeta / std::sqrt(1.f - expBeta * expBeta);
  }
};
""")
from ROOT import DebugTrack
