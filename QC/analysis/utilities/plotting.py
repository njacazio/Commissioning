#!/usr/bin/env python3

from ROOT import TColor, gStyle, gROOT, TCanvas, gPad, TLegend, TLatex, TPaveText, TGraph, TH1
import numpy as np


def definenicepalette():
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
    gStyle.SetOptStat(0)
    gStyle.SetOptTitle(0)
    gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")


def make_color_range(ncolors, simple=False):
    if ncolors <= 0:
        raise ValueError("ncolors must be > 0")
    if ncolors == 1:
        simple = True
    if simple:
        if ncolors <= 2:
            colors = ['#e41a1c', '#377eb8']
        elif ncolors <= 3:
            colors = ['#e41a1c', '#377eb8', '#4daf4a']
        elif ncolors <= 4:
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
        elif ncolors < 5:
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
        else:
            colors = ['#00000', '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#a65628', '#f781bf']
        # print("Using colors", colors)
        if len(colors) < ncolors:
            print("Not enough colors for simple", ncolors, "using, continous scale")
            return make_color_range(ncolors=ncolors, simple=False)
        return [TColor.GetColor(i) for i in colors]
    NRGBs = 5
    NCont = 256
    NCont = ncolors
    stops = np.array([0.00, 0.30, 0.61, 0.84, 1.00])
    red = np.array([0.00, 0.00, 0.57, 0.90, 0.51])
    green = np.array([0.00, 0.65, 0.95, 0.20, 0.00])
    blue = np.array([0.51, 0.55, 0.15, 0.00, 0.10])
    FI = TColor.CreateGradientColorTable(NRGBs,
                                         stops, red, green, blue, NCont)
    colors = []
    for i in range(NCont):
        colors.append(FI + i)
    colors = np.array(colors, dtype=np.int32)
    gStyle.SetPalette(NCont, colors)
    return [int(i) for i in colors]


nice_canvases = {}


def draw_nice_canvas(name, x=800, y=800, logx=False, logy=False, logz=True, title=None, replace=True, gridx=False, gridy=False):
    if 1:
        try:
            from screeninfo import get_monitors
            factor = get_monitors()[0].width / 1920
            x *= factor
            y *= factor
            x = int(x)
            y = int(y)
        except ImportError:
            print("screeninfo not installed, using default screen size. To optimize install screeninfo `pip install --user screeninfo`")

    global nice_canvases
    if not replace and name in nice_canvases:
        c = nice_canvases[name]
        c.cd()
        if title is not None:
            c.SetTitle(title)
        return c
    if title is None:
        title = name
    c = TCanvas(name, title, x, y)
    c.SetLogx(logx)
    c.SetLogy(logy)
    c.SetLogz(logz)
    c.SetTicky()
    c.SetTickx()
    c.SetLeftMargin(0.15)
    c.SetBottomMargin(0.15)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetGridx(gridx)
    c.SetGridy(gridy)
    c.Draw()
    nice_canvases[name] = c
    return c


labels_drawn = []


def draw_label(label, x=0.55, y=0.96, size=0.035, align=21, ndc=True):
    global labels_drawn
    while label.startswith(" ") or label.endswith(" "):
        label = label.strip()
    l = TLatex(x, y, label)
    if ndc:
        l.SetNDC()
    l.Draw()
    l.SetTextAlign(align)
    l.SetTextFont(42)
    l.SetTextSize(size)
    labels_drawn.append(l)
    return l


paves_drawn = []


def draw_pave(lines, x=[.68, .91], y=[.63, .72], opt="brNDC"):
    global paves_drawn
    pave = TPaveText(x[0], y[0], x[1], y[1], opt)
    pave.SetFillColor(0)
    for i in lines:
        pave.AddText(i)
    pave.Draw()
    paves_drawn.append(pave)


def update_all_canvases():
    for i in nice_canvases:
        if not nice_canvases[i]:
            continue
        nice_canvases[i].Update()
    return nice_canvases


def remove_canvas(n):
    if type(n) is not str:
        n = n.GetName()
    nice_canvases[n] = None


def reset_canvases():
    for i in nice_canvases:
        remove_canvas(i)


def save_all_canvases(n):
    dn = list(nice_canvases.keys())
    dn = [dn[0], dn[-1]]
    for i in nice_canvases:
        c = nice_canvases[i]
        if c is None:
            continue
        if i == dn[0]:
            c.SaveAs(f"{n}[")
        c.SaveAs(f"{n}")
        if i == dn[1]:
            c.SaveAs(f"{n}]")


def set_nice_frame(h, notitle=False):
    if "TEff" in h.ClassName():
        gPad.GetListOfPrimitives().ls()
        # h = gPad.GetListOfPrimitives().At(0)
        set_nice_frame(h.GetTotalHistogram())
        set_nice_frame(h.GetPassedHistogram())
        return
    if notitle:
        h.SetBit(TH1.kNoTitle)
        h.SetBit(TH1.kNoStats)
    h.GetYaxis().SetTitleSize(0.04)
    h.GetYaxis().SetTitleOffset(1.6)
    h.GetXaxis().SetTitleSize(0.04)
    h.GetXaxis().SetLabelOffset(0.01)
    h.GetXaxis().SetTitleOffset(1.25)


nice_frames = {}


def draw_nice_frame(c, x, y, xt, yt):
    if c is None:
        c = gPad
    c.cd()
    global nice_frames
    if not type(x) is list:
        if "TEff" in x.ClassName():
            x = x.GetTotalHistogram()
        x = [x.GetXaxis().GetBinLowEdge(1),
             x.GetXaxis().GetBinUpEdge(x.GetNbinsX())]
    if not type(y) is list:
        iseff = True
        if "TEff" in y.ClassName():
            y = y.GetTotalHistogram()
            iseff = True
        if "TH2" in y.ClassName():
            y = [y.GetYaxis().GetBinLowEdge(1),
                 y.GetYaxis().GetBinUpEdge(y.GetNbinsX())]
        elif iseff:
            y = [0, 1]
        else:
            y = [y.GetMinimum(), y.GetMaximum()]
    if not type(xt) is str:
        if "TEff" in xt.ClassName():
            xt = xt.GetTotalHistogram()
        xt = xt.GetXaxis().GetTitle()
    if not type(yt) is str:
        if "TEff" in yt.ClassName():
            yt = yt.GetTotalHistogram()
        yt = yt.GetYaxis().GetTitle()
    frame = c.DrawFrame(x[0], y[0], x[1], y[1], f";{xt};{yt}")
    set_nice_frame(frame)
    frame.SetDirectory(0)
    nice_frames[c.GetName()] = frame
    return frame


nice_legends = []


def draw_nice_legend(x=[0.7, 0.92], y=[0.7, 0.92], tit="", columns=1):
    global nice_legends
    leg = TLegend(x[0], y[0], x[1], y[1], tit)
    leg.SetLineColor(0)
    leg.SetNColumns(columns)
    nice_legends.append(leg)
    leg.Draw()
    return leg


graphs = []


def draw_diagonal(h):
    g = TGraph()
    g.SetName(h.GetName()+"_diagonal")
    g.SetPoint(0, h.GetXaxis().GetBinLowEdge(1), h.GetYaxis().GetBinLowEdge(1))
    g.SetPoint(1, h.GetXaxis().GetBinUpEdge(h.GetXaxis().GetNbins()), h.GetYaxis().GetBinUpEdge(h.GetYaxis().GetNbins()))
    g.SetLineStyle(7)
    g.Draw("sameL")
    graphs.append(g)
    return g
