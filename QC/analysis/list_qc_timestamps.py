#!/usr/bin/env python3

"""
Script to list the timestamps on objects on the CCDB
"""

from common import run_cmd, verbose_msg, set_verbose_mode, msg, get_default_parser, get_ccdb_api, warning_msg
from fetch_output import convert_timestamp, get_ccdb_obj
import os
from ROOT import TFile, TGraph, o2


timestamps = {}
listing_calls = {}


def print_timestamps():
    msg("Found", len(timestamps), "paths on CCDB")
    for i in timestamps:
        t = timestamps[i]
        msg("Found", len(t), i, "objects.",
            "First:", t[0], convert_timestamp(t[0][list(t[0].keys())[0]]), ".",
            "Last", t[-1], convert_timestamp(t[-1][list(t[0].keys())[0]]))


def save_fields(input_line,
                fields_to_save=["Created:"],
                fields_of_interest={}):
    for i in fields_to_save:
        if i in input_line:
            input_line = input_line.split(" ")
            fields_of_interest[input_line[0]] = int(input_line[1])
    return fields_of_interest


def useapi(ccdb_path, host):
    global timestamps
    objectlist = get_ccdb_api(host).list(ccdb_path,
                                         False,
                                         "text/plain")
    bunch_objects = []
    starting_sequence = "ID: "
    for i in objectlist.split("\n"):
        if starting_sequence in i:
            bunch_objects.append("")
        if len(bunch_objects) <= 0:
            warning_msg("Skipping", i, "because found no object there")
            continue
        bunch_objects[-1] += f"{i}\n"
    verbose_msg("Found", len(bunch_objects), "object in path", ccdb_path)
    for counter, i in enumerate(bunch_objects):
        if 0:
            print(f"Object #{counter}/{len(bunch_objects)-1}")
            print(i)
        t = {}
        for j in i.split("\n"):
            save_fields(j, fields_of_interest=t)
        # print(t)
        timestamps.setdefault(ccdb_path, []).append(t)


def list_ccdb_object(ccdb_path,
                     timestamp=1950004155840,
                     host="http://ccdb-test.cern.ch:8080",
                     tmp_file="out.txt",
                     #  fields_to_save=["Valid-Until:",
                     #                  "Valid-From:",
                     #                  "Created:"],
                     fields_to_save=["Valid-From:",
                                     "Created:"],
                     time_it=False):
    global timestamps
    listing_calls[ccdb_path] = listing_calls.setdefault(ccdb_path, 0) + 1
    verbose_msg("Listing MO", ccdb_path,
                "for timestamp", timestamp, convert_timestamp(timestamp),
                "in host", host,
                "iteration #", listing_calls[ccdb_path])
    run_cmd(f"curl -i -L {host}/{ccdb_path}/{timestamp} --output {tmp_file} 2> /dev/null && cat {tmp_file} | head -n 20 > {tmp_file}2",
            check_status=False,
            time_it=time_it)
    os.rename(f"{tmp_file}2", tmp_file)
    t = {}
    with open(tmp_file) as f:
        for i in f:
            # Checking that it was ok
            i = i.strip()
            if "HTTP" in i:
                if i == "HTTP/1.1 404":
                    verbose_msg("Did not find object")
                    return
            # print(i)
            for j in fields_to_save:
                if j in i:
                    i = i.split(" ")
                    t[i[0]] = int(i[1])
    single_line = " ---> "
    for i in fields_to_save:
        single_line += f"{i} {t[i]} {convert_timestamp(t[i])} +++ "
    verbose_msg(single_line)
    timestamps.setdefault(ccdb_path, []).append(t)
    return 0


def iterative_search(maximum_found_objects=2000,
                     max_search_iterations=-20,
                     minimum_timestamp=1615197295100,
                     delta_timestamp=1*1000):
    """
    delta_timestamp is in milliseconds
    """
    for i in timestamps:
        verbose_msg("Iteratively searching for", i, "with",
                    max_search_iterations, "iterations")
        delta = delta_timestamp
        iterations = 0
        while True:
            iterations += 1
            if max_search_iterations > 0 and iterations > max_search_iterations:
                msg("Max search iterations for", i,
                    f"({iterations} < {max_search_iterations})")
                break
            last_timestamp = timestamps[i][-1]["Valid-From:"]
            if last_timestamp - delta < minimum_timestamp:
                msg("Found old enough", i,
                    f"({last_timestamp} < {minimum_timestamp})")
                break
            listing_status = list_ccdb_object(i,
                                              timestamp=last_timestamp - delta)
            if listing_status == 0:
                verbose_msg("++ Found an object",
                            (last_timestamp -
                             timestamps[i][-1]["Valid-From:"])*0.001,
                            "seconds younger with delta", delta, "ms")
                delta = delta_timestamp
            else:
                delta += delta_timestamp
            if maximum_found_objects > 0 and len(timestamps[i]) >= maximum_found_objects:
                msg("Found enough", i, f"({maximum_found_objects})")
                break
    print_timestamps()


def write_timestamps(out_file="t.root",
                     entry_name="Valid-From:"):
    f = TFile(out_file, "UPDATE")
    f.cd()
    for i in timestamps:
        g = TGraph()
        g.SetName(i.replace("/", "--"))
        for j in timestamps[i]:
            g.SetPoint(g.GetN(),
                       float(g.GetN()),
                       float(j[entry_name]))
        g.Write()
    f.Close()


def download_objects(input_file="t.root",
                     out_path="/tmp/ccdbtest2/",
                     host="http://ccdb-test.cern.ch:8080",
                     overwrite=False):
    msg("Downloading CCDB objects from input file", input_file)
    out_path = os.path.normpath(out_path)
    f = TFile(input_file, "READ")
    lk = f.GetListOfKeys()
    obj_done = []
    for i in lk:
        name = i.GetName()
        cycle = i.GetCycle()
        if name in obj_done:
            continue
        obj_done.append(name)
        obj = f.Get(f"{name};{cycle}")
        name = name.replace("--", "/")
        limits = [int(obj.GetPointY(j)) for j in range(obj.GetN())]
        verbose_msg(name, len(limits),
                    "First", limits[0], convert_timestamp(limits[0]),
                    "Last", limits[-1], convert_timestamp(limits[-1]))
        for j in limits:
            get_ccdb_obj(name, j, out_path=out_path,
                         host=host, show=False,
                         verbose=True,
                         tag=True,
                         overwrite_preexisting=overwrite)
    f.Close()


def main(paths_to_check,
         host):
    if 0:  # Iterative search
        # Initializing timestamp objects
        for i in paths_to_check:
            list_ccdb_object(i)

        # Performing iterative search
        iterative_search()
    else:  # Use the CCDB API
        for i in paths_to_check:
            i = i.strip()
            if i == "":
                continue
            if "." in i:  # It's a file!
                verbose_msg("Using", i, "as input file")
                with open(i, "r") as f:
                    for j in f:
                        j = j.strip()
                        if i == "":
                            continue
                        useapi(ccdb_path=j,
                               host=host)
            else:
                useapi(ccdb_path=i,
                       host=host)
        print_timestamps()

    # Saving to disk
    write_timestamps(entry_name="Created:")


if __name__ == "__main__":
    parser = get_default_parser(__doc__)
    parser.add_argument("--input", "-i", type=str,
                        nargs="+",
                        # default="",
                        default=["qc/TOF/MO/TaskCosmics/CosmicRate/",
                                 "qc/TOF/MO/TaskCosmics/Crate1/"],
                        help="Input paths to check e.g. `qc/TOF/MO/TaskCosmics/CosmicRate/`. Multiple arguments are accepted, files with paths per line in input are also accepted")
    parser.add_argument("--host", type=str,
                        default="http://ccdb-test.cern.ch:8080",
                        help="Address of the ccdb host e.g. http://ccdb-test.cern.ch:8080 or http://qcdb.cern.ch:8083")
    parser.add_argument("--output", "-o", type=str,
                        default="/tmp/",
                        help="Path where to store the CCDB objects to download")
    parser.add_argument("--download", "-d",
                        action="store_true", help="Download mode.")

    args = parser.parse_args()
    set_verbose_mode(args)

    if args.download:
        download_objects(out_path=args.output)
    else:
        main(args.input,
             host=args.host)
