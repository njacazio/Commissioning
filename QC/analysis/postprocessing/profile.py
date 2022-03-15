#!/usr/bin/env python3


def main(h):
    p = h.ProfileX()
    p.SetDirectory(0)
    p.Draw("same")