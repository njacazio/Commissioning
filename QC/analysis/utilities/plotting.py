#!/usr/bin/env python3

from ROOT import TCanvas, gPad, TLegend, TLatex, TPaveText

nice_canvases = {}


def draw_nice_canvas(name, x=800, y=800, logx=False, logy=False, logz=True, title=None, replace=True):
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
    c.Draw()
    nice_canvases[name] = c
    return c


labels_drawn = []


def draw_label(label, x=0.55, y=0.96, size=0.035, align=21):
    global labels_drawn
    while label.startswith(" ") or label.endswith(" "):
        label = label.strip()
    l = TLatex(x, y, label)
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


def set_nice_frame(h):
    if "TEff" in h.ClassName():
        gPad.GetListOfPrimitives().ls()
        # h = gPad.GetListOfPrimitives().At(0)
        set_nice_frame(h.GetTotalHistogram())
        set_nice_frame(h.GetPassedHistogram())
        return
    h.GetYaxis().SetTitleSize(0.04)
    h.GetXaxis().SetTitleSize(0.04)
    h.GetXaxis().SetTitleOffset(1.25)


nice_frames = {}


def draw_nice_frame(c, x, y, xt, yt):
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
