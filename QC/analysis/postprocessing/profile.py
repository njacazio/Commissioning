#!/usr/bin/env python3

from ROOT import gPad


def main(h):
    p = h.ProfileX()
    p.SetDirectory(0)
    p.GetYaxis().SetTitle(f"#LT{h.GetYaxis().GetTitle()}#GT")
    p.Draw("same")
    gPad.SetGridy()
    gPad.SetGridx()
