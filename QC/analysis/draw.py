#!/usr/bin/env python3


from shutil import ExecError
from utilities.plotting import draw_nice_canvas, remove_canvas, save_all_canvases
from common import warning_msg, get_default_parser, set_verbose_mode, verbose_msg
from ROOT import TFile, TH1, TLatex
from os import path
import glob
import configparser


labels_drawn = []


def draw_label(label, x=0.55, y=0.96):
    while label.startswith(" ") or label.endswith(" "):
        label = label.strip()
    l = TLatex(x, y, label)
    l.SetNDC()
    l.Draw()
    l.SetTextAlign(21)
    l.SetTextFont(42)
    l.SetTextSize(0.035)
    labels_drawn.append(l)
    return l


object_drawn = {}


def draw(filename,
         out_path="/tmp/",
         extension="png",
         configuration=None,
         save=False):
    filename = path.normpath(filename)
    f_tag = filename.split("/")[-2]
    verbose_msg("Processing", filename, f"'{f_tag}'")
    can = draw_nice_canvas(f_tag)
    input_file = None
    h = None
    try:
        input_file = TFile(filename, "READ")
    except:
        pass
    h = input_file.Get("ccdb_object")
    h.SetDirectory(0)
    input_file.Close()
    h.SetName(f_tag)
    drawopt = ""
    show_title = False
    # if "TEfficiency" in h.ClassName():
    #     # h = h.GetTotalHistogram()
    #     h = h.GetPassedHistogram()
    h.SetBit(TH1.kNoTitle)
    postprocess = ""
    if configuration is not None:
        def get_option(opt, forcetype=None):
            src = "DEFAULT"
            if configuration.has_option(f_tag, opt):
                src = f_tag
            # verbose_msg("Getting option", src, opt)
            o = configuration.get(src, opt)
            if forcetype is not None:
                if forcetype == bool:
                    o = configuration.getboolean(src, opt)
                elif forcetype == float:
                    o = configuration.getfloat(src, opt)
                else:
                    o = forcetype(o)
            if type(o) is str:
                while o.startswith(" ") or o.endswith(" "):
                    o = o.strip()
            # print(f"'{o}'", type(o))
            return o
        can.SetLogx(get_option("logx", bool))
        can.SetLogy(get_option("logy", bool))
        can.SetLogz(get_option("logz", bool))
        drawopt = get_option("drawopt")
        show_title = get_option("showtitle", bool)
        if not get_option("showstats", bool):
            h.SetBit(TH1.kNoStats)

        def set_if_not_empty(opt, setter, forcetype=None):
            s = get_option(opt, forcetype=forcetype)
            if s == "":
                return
            if "SetTitle" in setter:
                s = f"h.{setter}(\"{s}\")"
            else:
                s = f"h.{setter}({s})"
            # print(s)
            eval(s, None, {"h": h})

        set_if_not_empty("xtitle", "GetXaxis().SetTitle")
        set_if_not_empty("ytitle", "GetYaxis().SetTitle")
        set_if_not_empty("xrange", "GetXaxis().SetRangeUser")
        set_if_not_empty("yrange", "GetYaxis().SetRangeUser")
        postprocess = get_option("postprocess")
    h.Draw(drawopt)
    if postprocess != "":
        postprocess = postprocess.replace(".py", "")
        p = f"from postprocessing import {postprocess}"
        exec(p)
        p = f"{postprocess}.main(h)"
        exec(p)
    if show_title:
        draw_label(h.GetTitle())
    if "TEfficiency" in h.ClassName():
        h.SetTitle("")
    can.Update()
    if save:
        saveas = path.join(out_path, f"{f_tag}.{extension}")
        can.SaveAs(saveas)
    if f_tag in object_drawn:
        warning_msg("Replacing", f_tag)
    object_drawn[f_tag] = h
    return can, h


def main(tag="qc",
         main_path="/tmp/",
         draw_only=["mDeltaXEtaCONSTR"],
         filename="snapshot.root",
         config_file="drawconfig.conf",
         wait=False,
         refresh=False):
    config_parser = configparser.RawConfigParser()
    config_parser.read(config_file)
    p = path.join(main_path, tag)
    if not path.isdir(p):
        raise ExecError("Cannot find directory", p)
    files = [f for f in glob.glob(
        path.join(p, f"**/{filename}"), recursive=True)]
    for fn in files:
        process = True
        if draw_only is not None:
            process = False
            for i in draw_only:
                if i not in fn:
                    continue
                process = True
        if not process:
            continue
        r = draw(fn, configuration=config_parser)
        if wait:
            input(
                f"'{r[1].GetName()}' {r[1].ClassName()} press enter to continue")
        if refresh:
            remove_canvas(r[0])
            del r
    save_all_canvases("/tmp/plots.pdf")
    return config_parser


if __name__ == "__main__":
    parser = get_default_parser("Fetch data from CCDB"
                                "Basic example: `./draw.py`")

    parser.add_argument('--only', "-O",
                        type=str,
                        default=None,
                        nargs="+",
                        help='Names of the objects to draw exclusively')
    parser.add_argument('--config', "-c",
                        type=str,
                        default="drawconfig.conf",
                        help='Name of the configuration file to use')
    parser.add_argument("-b",
                        action="store_true",
                        help='Background mode')
    parser.add_argument('--wait', "-w",
                        action="store_true",
                        help='Option to stop at each canvas')
    parser.add_argument('--refresh', "-r",
                        action="store_true",
                        help='Option to delete each canvas after drawing it')

    args = parser.parse_args()
    set_verbose_mode(args)

    r = main(draw_only=args.only,
             wait=args.wait,
             refresh=args.refresh)
    if 1:
        l = []
        for i in object_drawn:
            if i in r.sections():
                continue
            l.append(f"[{i}]")
        if len(l) > 0:
            print("Processed objects without config:")
            for i in l:
                print(i)
    if not args.b:
        input("Press enter to continue")
