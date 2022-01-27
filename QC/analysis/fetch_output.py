#!/usr/bin/env python3

import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
from ROOT import TFile, gPad, TPaveText, o2, std
from common import verbose_msg, set_verbose_mode, get_default_parser, msg, get_ccdb_api
import os


def convert_timestamp(ts):
    """
    Converts the timestamp in milliseconds in human readable format
    """
    return datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')


def get_ccdb_obj(ccdb_path, timestamp, out_path, host, show, verbose,
                 tag=False,
                 overwrite_preexisting=True,
                 use_o2_api=True):
    """
    Gets the ccdb object from 'ccdb_path' and 'timestamp' and downloads it into 'out_path'
    If 'tag' is True then the filename will be renamed after the timestamp.
    """
    verbose_msg("Getting obj", ccdb_path, "with timestamp",
                timestamp, convert_timestamp(timestamp))
    out_name = "snapshot.root"
    if tag:
        out_name = f"snapshot_{timestamp}.root"
    out_path = os.path.normpath(out_path)
    fullname = os.path.join(out_path, ccdb_path, out_name)
    if os.path.isfile(fullname) and not overwrite_preexisting:
        msg("File", fullname, "already existing, not overwriting")
    if use_o2_api:
        api = get_ccdb_api(host)
        if timestamp == -1:
            timestamp = o2.ccdb.getCurrentTimestamp()
        metadata = std.map('string,string')()
        api.retrieveBlob(ccdb_path,
                         out_path,
                         metadata,
                         timestamp,
                         True,
                         out_name)

    else:
        cmd = f"o2-ccdb-downloadccdbfile --host {host} --path {ccdb_path} --dest {out_path} --timestamp {timestamp}"
        cmd += f" -o {out_name}"
        subprocess.run(cmd.split())
    if not os.path.isfile(fullname):
        raise ValueError("File", fullname, "not found")
    if verbose:
        f = TFile(os.path.join(fullname), "READ")
        meta = f.Get("ccdb_meta")
        if False:
            print("Metadata")
            for i in meta:
                print(i)

        def print_info(entry):
            print("Object", entry, meta[entry])
        print_info("Last-Modified")
        if show:
            obj = f.Get("ccdb_object")
            obj.Draw()
            time_box = TPaveText(.01, .9, 0.3, 0.99, "NDC")
            time_box.AddText(ccdb_path)
            time_box.AddText(f"timestamp {timestamp}")
            time_box.AddText(f"{convert_timestamp(timestamp)}")
            time_box.Draw()
            gPad.Update()
            input("Press enter to continue")
            # obj.Print("ALL")


def main(ccdb_path, timestamp, out_path, host, show, verbose):
    if os.path.isfile(ccdb_path):
        with open(ccdb_path) as f:
            for i in f:
                i = i.strip()
                if i == "":
                    continue
                get_ccdb_obj(ccdb_path=i,
                             out_path=out_path,
                             timestamp=timestamp,
                             show=show,
                             host=host,
                             verbose=verbose)
    else:
        get_ccdb_obj(ccdb_path=ccdb_path,
                     out_path=out_path,
                     timestamp=timestamp,
                     show=show,
                     host=host,
                     verbose=verbose)


if __name__ == "__main__":
    parser = get_default_parser("Fetch data from CCDB"
                                "Basic example: `./fetch_output.py qc/TOF/MO/TaskRaw/hDiagnostic`")
    parser.add_argument('ccdb_path',
                        metavar='path_to_object',
                        type=str,
                        help='Path of the object in the CCDB repository. If a `.txt` file is passed the all the file input is downloaded')
    parser.add_argument('--timestamp', "-t",
                        metavar='object_timestamp',
                        type=int,
                        default=-1,
                        help='Timestamp of the object to fetch, by default -1 (latest)')
    parser.add_argument('--out_path', "-o",
                        default="/tmp/",
                        type=str,
                        help='Output path on your local machine')
    parser.add_argument('--ccdb_host', "-H",
                        default="qcdb.cern.ch:8083",
                        type=str,
                        help='Host to use for the CCDB fetch')
    parser.add_argument('--show', '-s', action='store_true')

    args = parser.parse_args()
    set_verbose_mode(args)

    main(ccdb_path=args.ccdb_path,
         out_path=args.out_path,
         timestamp=args.timestamp,
         show=args.show,
         host=args.ccdb_host,
         verbose=args.verbose)
