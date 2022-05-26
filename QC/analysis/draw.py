#!/usr/bin/env python3


"""
Script to draw monitoring objects taken from the CCDB
"""

from shutil import ExecError
from utilities.plotting import draw_nice_canvas, draw_nice_frame, remove_canvas, save_all_canvases, reset_canvases, set_nice_frame
from common import warning_msg, get_default_parser, set_verbose_mode, verbose_msg, convert_timestamp
from ROOT import TFile, TH1, TLatex
from os import path
import glob
import configparser


object_drawn = {}


def draw(filename,
         out_path="/tmp/",
         extensions=["png", "root"],
         configuration=None,
         save=False,
         save_tag="",
         metadata_of_interest=None):
    reset_canvases()
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
    if metadata_of_interest is not None:
        metadata = input_file.Get("ccdb_meta")
        m = {}
        for i in metadata:
            if type(metadata_of_interest) is list:
                if i[0] in metadata_of_interest:
                    print(i[0], "->", i[1])
                    if i[0] in ["Valid-From", "Valid-Until"]:
                        m[i[0]] = f"{i[1]} {convert_timestamp(i[1])}"
                    else:
                        m[i[0]] = i[1]
            else:
                print(i[0], "->", i[1])
        if len(m) > 0:
            metadata_of_interest = m
        else:
            metadata_of_interest = None
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
        if type(configuration) is str:
            c = configparser.RawConfigParser()
            c.read(configuration)
            configuration = c

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
            verbose_msg(f"Got for option {opt} from {src} '{o}'", type(o))
            return o
        if get_option("skip", forcetype=bool):
            verbose_msg("Skipping", filename)
            remove_canvas(can)
            del can
            return
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
    if "TEfficiency" in h.ClassName():
        x = h.GetTotalHistogram().GetXaxis()
        x = [x.GetBinLowEdge(1), x.GetBinUpEdge(x.GetNbins())]
        y = [0, 1.2]
        if h.GetDimension() == 2:
            y = h.GetTotalHistogram().GetYaxis()
            y = [y.GetBinLowEdge(1), y.GetBinUpEdge(y.GetNbins())]
        draw_nice_frame(can, x, y, h, h)
        h.Draw(drawopt+"same")
    else:
        set_nice_frame(h)
        h.Draw(drawopt)
    if postprocess != "":
        postprocess = postprocess.replace(".py", "")
        try:
            p = f"from postprocessing import {postprocess}"
            exec(p)
            p = f"{postprocess}.main(h)"
            exec(p)
        except:
            warning_msg("Could not run", postprocess, "for", f_tag)
    if show_title:
        draw_label(h.GetTitle())
    if "TEfficiency" in h.ClassName():
        h.SetTitle("")
    if metadata_of_interest is not None:
        yl = 0.4
        for i in metadata_of_interest:
            draw_label(f"{i} = {metadata_of_interest[i]}",
                       x=0.9, y=yl, size=0.025, align=31)
            yl -= 0.03
    can.Update()
    if save:
        for i in extensions:
            saveas = path.join(out_path, f"{f_tag}{save_tag}.{i}")
            can.SaveAs(saveas)
    if f_tag in object_drawn:
        warning_msg("Replacing", f_tag)
    object_drawn[f_tag] = h
    return can, h


def main(main_path="/tmp/qc/",
         draw_only=["mDeltaXEtaCONSTR"],
         filename="snapshot.root",
         timestamp=None,
         config_file="drawconfig.conf",
         wait=False,
         refresh=False,
         save=False):
    if timestamp is not None:
        filename = path.splitext(filename)
        filename = f"{filename[0]}_{timestamp}{filename[1]}"

    config_parser = configparser.RawConfigParser()
    config_parser.read(config_file)
    if not path.isdir(main_path):
        raise ExecError("Cannot find directory", main_path)
    files = [f for f in glob.glob(
        path.join(main_path, f"**/{filename}"), recursive=True)]
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
        save_tag = ""
        if timestamp is not None:
            save_tag = f"_{timestamp}"
        r = draw(fn, configuration=config_parser,
                 save=save,
                 save_tag=save_tag,
                 out_path=main_path)
        if wait:
            input(
                f"'{r[1].GetName()}' {r[1].ClassName()} press enter to continue")
        if refresh:
            remove_canvas(r[0])
            del r
    if save:
        save_all_canvases("/tmp/plots.pdf")
    return config_parser


if __name__ == "__main__":
    parser = get_default_parser("Script to draw the monitoring object fetched from CCDB "
                                "It usally work with a configuration file that specifies the input files and options. "
                                "Basic example: `./draw.py`")

    parser.add_argument('--inputfile', "-i",
                        type=str,
                        default=None,
                        nargs="+",
                        help='Draw a single file. Optional argument that bypasses the configuration file.')
    parser.add_argument('--only', "-O",
                        type=str,
                        default=None,
                        nargs="+",
                        help='Names of the objects to draw exclusively')
    parser.add_argument('--mainpath', "-M",
                        type=str,
                        default="/tmp/qc/",
                        help='Main path where to take input and post output')
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
    parser.add_argument('--save', "-S",
                        action="store_true",
                        help='Option save images')
    parser.add_argument('--timestamp', "-t",
                        metavar='object_timestamp',
                        type=str,
                        default=[None],
                        nargs="+",
                        help='Timestamp of the object to fetch, by default -1 (latest). Can accept more then one timestamp.')

    args = parser.parse_args()
    set_verbose_mode(args)

    if args.inputfile is not None:
        for i in args.inputfile:
            intersting = ["RunNumber", "Valid-From", "Valid-Until"]
            r = draw(i, metadata_of_interest=intersting)
    else:
        for i in args.timestamp:
            r = main(draw_only=args.only,
                     main_path=args.mainpath,
                     wait=args.wait,
                     refresh=args.refresh,
                     timestamp=i,
                     save=args.save)
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
