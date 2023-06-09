#!/usr/bin/env python3


from ROOT import o2, TFile, TF1, gROOT, gInterpreter, TPaveText, TColor, gStyle
import numpy as np


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
if 1:
    from ROOT import DebugTrack


if 1:
    NRGBs = 5
    NCont = 256
    stops = np.array([0.00, 0.30, 0.61, 0.84, 1.00])
    red = np.array([0.00, 0.00, 0.57, 0.90, 0.51])
    green = np.array([0.00, 0.65, 0.95, 0.20, 0.00])
    blue = np.array([0.51, 0.55, 0.15, 0.00, 0.10])
    TColor.CreateGradientColorTable(NRGBs,
                                    stops, red, green, blue, NCont)
    gStyle.SetNumberContours(NCont)
    gStyle.SetPalette(55)

gInterpreter.Declare("""
    static constexpr float mMassZ = MassPionCharged;
    static constexpr float mMassZSqared = mMassZ*mMassZ;
    float parameters[5] = {0, 0, 0, 0, 0};
    float GetExpectedSigma(const float mom, const float tofSignal, const float collisionTimeRes){
        if (mom <= 0) {
            return -999.f;
        }
        const float dpp = parameters[0] + parameters[1] * mom + parameters[2] * mMassZ / mom; // mean relative pt resolution;
        const float sigma = dpp * tofSignal / (1. + mom * mom / (mMassZSqared));
        return std::sqrt(sigma * sigma + parameters[3] * parameters[3] / mom / mom + parameters[4] * parameters[4] + collisionTimeRes * collisionTimeRes);
    }
  float ComputeExpectedTimePi(const float tofExpMom, const float length) { return length * sqrt((mMassZSqared) + (tofExpMom * tofExpMom)) / (kCSPEED * tofExpMom); }
"""
                     )

gInterpreter.Declare("""
enum PIDFlags : uint8_t {
  EvTimeUndef = 0x0,  // Event collision not set, corresponding to the LHC Fill event time
  EvTimeTOF = 0x1,    // Event collision time from TOF
  EvTimeT0AC = 0x2,   // Event collision time from the FT0AC
  EvTimeTOFT0AC = 0x4 // Event collision time from the TOF and FT0AC
};
"""
                     )
