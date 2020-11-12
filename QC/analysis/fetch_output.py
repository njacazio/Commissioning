#!/usr/bin/env python3

import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
import argparse
from ROOT import TFile, gPad
import os


def convert_timestamp(ts):
    """
    Converts the timestamp in milliseconds in human readable format
    """
    return datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')


def get_ccdb_obj(ccdb_path, timestamp, out_path, show, verbose):
    """
    Gets the ccdb object from 'ccdb_path' and 'timestamp' and downloads it into 'out_path'
    """
    if verbose:
        print("Getting obj", ccdb_path, "with timestamp",
              timestamp, convert_timestamp(timestamp))
    cmd = f"o2-ccdb-downloadccdbfile --path {ccdb_path} --dest {out_path} --timestamp {timestamp}"
    subprocess.run(cmd.split())
    if verbose:
        f = TFile(os.path.join(out_path, ccdb_path, "snapshot.root"), "READ")
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
            gPad.Update()
            input("Press enter to continue")
            # obj.Print("ALL")


def main(ccdb_path, timestamp, out_path, show, verbose):
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
                             verbose=verbose)
    else:
        get_ccdb_obj(ccdb_path=ccdb_path,
                     out_path=out_path,
                     timestamp=timestamp,
                     show=show,
                     verbose=verbose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch data from CCDB"
        "Basic example: `./fetch_output.py qc/TOF/TOFTaskCompressed/hDiagnostic`")
    parser.add_argument('ccdb_path',
                        metavar='path_to_object',
                        type=str,
                        help='Path of the object in the CCDB repository. If a file is passed the all the file input is downloaded')
    parser.add_argument('--timestamp', "-t",
                        metavar='object_timestamp',
                        type=int,
                        default=-1,
                        help='Timestamp of the object to fetch, by default -1 (latest)')
    parser.add_argument('--out_path', "-o",
                        default="/tmp/",
                        type=str,
                        help='Output path on your local machine')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--show', '-s', action='store_true')

    args = parser.parse_args()
    main(ccdb_path=args.ccdb_path,
         out_path=args.out_path,
         timestamp=args.timestamp,
         show=args.show,
         verbose=args.verbose)
