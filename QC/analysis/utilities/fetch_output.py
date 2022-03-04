#!/usr/bin/env python3

import subprocess
from datetime import datetime
from ROOT import TFile, gPad, TPaveText, o2, std
from common import verbose_msg, set_verbose_mode, get_default_parser, msg, get_ccdb_api, warning_msg
import os


def convert_timestamp(ts):
    """
    Converts the timestamp in milliseconds in human readable format or vice versa if passing a string
    """
    if type(ts) is str:
        return int(datetime.strptime(ts, "%d/%m/%Y, %H:%M:%S").timestamp()*1000)
    return datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')


def get_ccdb_obj(ccdb_path,
                 timestamp,
                 out_path,
                 host,
                 show,
                 tag=False,
                 overwrite_preexisting=True,
                 use_o2_api=True,
                 check_metadata=True,
                 interesting_metadata=["ObjectType",
                                       "PassName",
                                       "PeriodName",
                                       "RunNumber",
                                       "Valid-From",
                                       "Valid-Until",
                                       ""]):
    """
    Gets the ccdb object from 'ccdb_path' and 'timestamp' and downloads it into 'out_path'
    If 'tag' is True then the filename will be renamed after the timestamp.
    """
    def check_rootfile(fname):
        try:
            f = TFile(fname, "READ")
            if f.TestBit(TFile.kRecovered):
                warning_msg("File", fname, "was recovered")
                return False
            elif not f.IsOpen():
                warning_msg("File", fname, "is not open")
                return False
        except OSError:
            warning_msg("Issue when checking file", fname)
            return False
        return True

    verbose_msg("Getting obj", host, ccdb_path, "with timestamp",
                timestamp, convert_timestamp(timestamp))
    out_name = "snapshot.root"
    if tag:
        out_name = f"snapshot_{timestamp}.root"
    out_path = os.path.normpath(out_path)
    fullname = os.path.join(out_path, ccdb_path, out_name)
    if os.path.isfile(fullname) and not overwrite_preexisting:
        if check_rootfile(fullname):
            msg("File", fullname, "already existing, not overwriting")
            return
    if use_o2_api:
        api = get_ccdb_api(host)
        if timestamp == -1:
            timestamp = o2.ccdb.getCurrentTimestamp()
        metadata = std.map('string,string')()
        api.retrieveBlob(ccdb_path,
                         out_path,
                         metadata,
                         timestamp)
        if tag:
            os.rename(os.path.join(out_path, ccdb_path,
                                   "snapshot.root"), fullname)
    else:
        cmd = f"o2-ccdb-downloadccdbfile --host {host} --path {ccdb_path} --dest {out_path} --timestamp {timestamp}"
        cmd += f" -o {out_name}"
        print(cmd)
        subprocess.run(cmd.split())
    if not os.path.isfile(fullname):
        raise ValueError("File", fullname, "not found")
    if not check_rootfile(fullname):
        raise ValueError("File", fullname, "is not Ok")
    if check_metadata:
        f = TFile(os.path.join(fullname), "READ")
        meta = f.Get("ccdb_meta")
        verbose_msg("Metadata")
        m_d = {"Valid-From": None, "Valid-Until": None}
        for i in meta:
            if i[0] in m_d:
                m_d[i[0]] = int(i[1])
            if interesting_metadata[0] != "" and i[0] not in interesting_metadata:
                continue
            if i[0] in m_d:
                verbose_msg(i, convert_timestamp(int(i[1])))
            else:
                verbose_msg(i)
        if timestamp < m_d["Valid-From"] or timestamp > m_d["Valid-Until"]:
            warning_msg("Timestamp asked is outside of window", timestamp, m_d)

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
    return fullname


def main(ccdb_path,
         timestamp=-1,
         out_path="/tmp/",
         host="qcdb.cern.ch:8083",
         show=False,
         preserve_ccdb_structure=True,
         tag=None):
    if type(timestamp) is not int:
        timestamp = convert_timestamp(timestamp)

    downloaded = []
    # The input file is a list of objects
    if os.path.isfile(ccdb_path):
        with open(ccdb_path) as f:
            for i in f:
                i = i.strip()
                if i == "":
                    continue
                obj = get_ccdb_obj(ccdb_path=i,
                                   out_path=out_path,
                                   timestamp=timestamp,
                                   tag=tag,
                                   show=show,
                                   host=host)
                downloaded.append(obj)
    else:
        obj = get_ccdb_obj(ccdb_path=ccdb_path,
                           out_path=out_path,
                           timestamp=timestamp,
                           tag=tag,
                           show=show,
                           host=host)
        downloaded.append(obj)
    if not preserve_ccdb_structure:
        print("Printing")
        for i in downloaded:
            j = i.split("/")[-2]
            j = os.path.join(out_path, f"{j}.root")
            print(i,"->", j)
            os.rename(i, j)


if __name__ == "__main__":
    parser = get_default_parser("Fetch data from CCDB"
                                "Basic example: `./fetch_output.py qc/TOF/MO/TaskRaw/hDiagnostic`")
    parser.add_argument('ccdb_path',
                        metavar='path_to_object',
                        type=str,
                        help='Path of the object in the CCDB repository. If a `.txt` file is passed the all the file input is downloaded')
    parser.add_argument('--timestamp', "-t",
                        metavar='object_timestamp',
                        type=str,
                        default=["-1"],
                        nargs="+",
                        help='Timestamp of the object to fetch, by default -1 (latest)')
    parser.add_argument('--out_path', "-o",
                        default="/tmp/",
                        type=str,
                        help='Output path on your local machine')
    parser.add_argument('--ccdb_host', "-H",
                        default="qcdb.cern.ch:8083",
                        type=str,
                        help='Host to use for the CCDB fetch e.g. qcdb.cern.ch:8083')
    parser.add_argument('--tag', '-T', action='store_true')
    parser.add_argument('--show', '-s', action='store_true')

    args = parser.parse_args()
    set_verbose_mode(args)

    for i in args.timestamp:
        if i.isdecimal():
            i = int(i)
        main(ccdb_path=args.ccdb_path,
             out_path=args.out_path,
             timestamp=i,
             show=args.show,
             tag=args.tag,
             host=args.ccdb_host)
