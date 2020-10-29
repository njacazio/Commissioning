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


def get_ccdb_obj(path, timestamp=-1, dest="/tmp/", show=True, verbose=False):
    """
    Gets the ccdb object from 'path' and 'timestamp' and downloads it into 'dest'
    """
    if verbose:
        print("Getting obj", path, "with timestamp",
              timestamp, convert_timestamp(timestamp))
    cmd = f"o2-ccdb-downloadccdbfile --path {path} --dest {dest} --timestamp {timestamp}"
    subprocess.run(cmd.split())
    if verbose:
        f = TFile(os.path.join(dest, path, "snapshot.root"), "READ")
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
          obj.Print("ALL")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch data from CCDB"
        "Basic example: `./fetch_output.py qc/TOF/TOFTaskCompressed/hDiagnostic`")
    parser.add_argument('path', metavar='path_to_object', type=str,
                        help='Path of the object in the CCDB repository')
    parser.add_argument('--timestamp', metavar='object_timestamp', type=int,
                        default=-1,
                        help='Timestamp of the object to fetch')
    parser.add_argument('--verbose', '-v', action='store_true', default=0)

    args = parser.parse_args()
    get_ccdb_obj(path=args.path,
                 timestamp=args.timestamp,
                 verbose=args.verbose)
