#!/usr/bin/env python3

import subprocess
from ROOT import TFile, gPad, TPaveText, o2, std
from common import verbose_msg, set_verbose_mode, get_default_parser, msg, get_ccdb_api, warning_msg, convert_timestamp, fatal_msg
import os


def get_ccdb_obj(ccdb_path,
                 timestamp,
                 out_path,
                 host,
                 show,
                 tag=False,
                 overwrite_preexisting=True,
                 download_mode="api",
                 check_metadata=True,
                 musthave_in_metadata=None,
                 interesting_metadata=["ObjectType",
                                       "PassName",
                                       "PeriodName",
                                       "RunNumber",
                                       "Valid-From",
                                       "Valid-Until",
                                       ""]):
    """
    Gets the ccdb object from 'ccdb_path' and 'timestamp' and downloads it into 'out_path'.
    If `out_path` is a file name and not a path, then the output file will be renamed to the requested name.
    If 'tag' is True then the filename will be renamed after the timestamp.
    """
    if musthave_in_metadata is not None and download_mode == "wget":
        timestamp = 1700000000000
    if type(timestamp) is not int:
        raise ValueError("timestamp must be an integer", type(timestamp))

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

    out_name = "snapshot.root"
    out_path = os.path.normpath(out_path)
    fullname = os.path.join(out_path, ccdb_path, out_name)
    if "." in os.path.split(out_path)[-1]:
        fullname = out_path
        out_name = os.path.split(out_path)[-1]
        out_path = os.path.split(out_path)[0]
    if tag:
        out_name = os.path.splitext(out_name)
        out_name = f"{out_name[0]}_{timestamp}{out_name[1]}"
        fullname = os.path.join(out_path, ccdb_path, out_name)
    verbose_msg("Getting obj", ccdb_path, "with timestamp",
                timestamp, convert_timestamp(timestamp), "from host", host, "to", fullname)
    if os.path.isfile(fullname) and not overwrite_preexisting:
        if check_rootfile(fullname):
            msg("File", fullname, "already existing, not overwriting")
            return
    full_out_path = os.path.dirname(fullname)
    if download_mode == "wget" and not os.path.isdir(full_out_path):
        print("Making dir", full_out_path)
        os.makedirs(full_out_path, exist_ok=True)
    if download_mode == "api":
        api = get_ccdb_api(host)
        if timestamp == -1:
            verbose_msg("Getting current timestamp")
            timestamp = o2.ccdb.getCurrentTimestamp()
        metadata = std.map('string,string')()
        api.retrieveBlob(ccdb_path,
                         out_path,
                         metadata,
                         timestamp)
        if tag:
            os.rename(os.path.join(out_path, ccdb_path,
                                   "snapshot.root"), fullname)
    elif download_mode == "wget":
        cmd = f"wget -O {fullname} {host}/{ccdb_path}/{timestamp}"
        if "PeriodName" in musthave_in_metadata:
            cmd += "/PeriodName={}".format(musthave_in_metadata["PeriodName"])
        if "RunNumber" in musthave_in_metadata:
            cmd += "/RunNumber={}".format(musthave_in_metadata["RunNumber"])
        if "PassName" in musthave_in_metadata:
            cmd += "/PassName={}".format(musthave_in_metadata["PassName"])
        verbose_msg("Using o2 executable", cmd)
        subprocess.run(cmd.split())
    else:
        cmd = f"o2-ccdb-downloadccdbfile --host {host} --path {ccdb_path} --dest {out_path} --timestamp {timestamp}"
        cmd += f" -o {out_name}"
        verbose_msg("Using o2 executable", cmd)
        subprocess.run(cmd.split())
    if not os.path.isfile(fullname):
        raise ValueError("Download target file", fullname, "not found")
    if not check_rootfile(fullname):
        raise ValueError("Download target file", fullname, "is not Ok")
    if check_metadata and (download_mode != "wget"):
        f = TFile(os.path.join(fullname), "READ")
        meta = f.Get("ccdb_meta")
        verbose_msg("Metadata")
        m_d = {"Valid-From": None, "Valid-Until": None}
        for i in meta:
            if i[0] in m_d:
                m_d[i[0]] = int(i[1])
            if musthave_in_metadata is not None:
                for metatohave in musthave_in_metadata:
                    if metatohave != i[0]:
                        continue
                    mvalue = musthave_in_metadata[metatohave]
                    if mvalue != i[1]:
                        for m in meta:
                            continue
                            print(m)
                        warning_msg(musthave_in_metadata, "metadata",
                                    i[1], "not matching required metadata", mvalue, "!")
                        os.remove(os.path.join(fullname))
                        return
            if interesting_metadata[0] != "" and i[0] not in interesting_metadata:
                continue
            if i[0] in m_d:
                verbose_msg(i, convert_timestamp(int(i[1])),
                            "delta =", int(i[1]) - timestamp)
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
         download_mode="api",
         musthave_in_metadata=None,
         retry_policy=0,
         retry_delta=30,
         show=False,
         tag=None):
    if retry_policy < 0:
        fatal_msg("Can't have a negative retry policy")
    timestamp = convert_timestamp(timestamp, make_timestamp=True)
    downloaded = []
    # The input file is a list of objects
    if os.path.isfile(ccdb_path):
        with open(ccdb_path) as f:
            for i in f:
                i = i.strip()
                if i == "":
                    continue
                if "#" in i:
                    continue
                if "%" in i:
                    break
                for j in range(retry_policy+1):
                    obj = get_ccdb_obj(ccdb_path=i,
                                       out_path=out_path,
                                       timestamp=timestamp + j * retry_delta,
                                       tag=tag,
                                       show=show,
                                       download_mode=download_mode,
                                       musthave_in_metadata=musthave_in_metadata,
                                       host=host)
                    if obj is not None:
                        downloaded.append(obj)
                        if j > 0:
                            warning_msg("Managed after", j, "tries")
                        break
                    warning_msg("Retrying retrieval", j, "out of", retry_policy,
                                "adding to timestamp", j * retry_delta, "ms")
    else:
        for j in range(retry_policy+1):
            obj = get_ccdb_obj(ccdb_path=ccdb_path,
                               out_path=out_path,
                               timestamp=timestamp + j * retry_delta,
                               tag=tag,
                               show=show,
                               download_mode=download_mode,
                               musthave_in_metadata=musthave_in_metadata,
                               host=host)
            if obj is not None:
                downloaded.append(obj)
                if j > 0:
                    warning_msg("Managed after", j, "tries")
                break
            warning_msg("Retrying retrieval", j, "out of", retry_policy,
                        "adding to timestamp", j * retry_delta, "ms")


def fetchfromfile(filename, ccdb_path, args):
    with open(filename) as f:
        for i in f:
            i = i.strip()
            while "  " in i:
                i = i.replace("  ", " ")
            if i == "":
                continue
            if i.startswith("#"):
                continue
            if i.startswith("%"):
                break
            i = i.replace(":", "")
            i = i.split()
            # print(i)
            run_number = i[0]
            timestamp = i[1]
            out_path = f"{args.out_path}/Run{run_number}"

            main(ccdb_path=ccdb_path,
                 out_path=out_path,
                 timestamp=timestamp,
                 show=args.show,
                 tag=args.tag,
                 retry_policy=10,
                 retry_delta=1000,
                 musthave_in_metadata={"RunNumber": run_number},
                 host=ccdb_host)


if __name__ == "__main__":
    parser = get_default_parser("Fetch data from CCDB. "
                                "Basic example: `./fetch_output.py qc/TOF/MO/TaskRaw/hDiagnostic`")
    parser.add_argument('ccdb_path',
                        metavar='path_to_object',
                        type=str,
                        help="Path of the object in the CCDB repository. If a `.txt` file is passed the all the file input is downloaded."
                             "Can also be an address e.g. if http://qcdb.cern.ch:8083/browse/qc/TOF/MO/TaskDigits/TOFRawsMulti the host is taken from there")
    parser.add_argument('--timestamp', "-t",
                        metavar='object_timestamp',
                        type=str,
                        default=["-1"],
                        nargs="+",
                        help='Timestamp of the object to fetch, by default -1 (latest). Can accept more then one timestamp.')
    parser.add_argument('--out_path', "-o",
                        default="/tmp/QCMOs/",
                        type=str,
                        help='[/tmp/] Output path on your local machine')
    parser.add_argument('--downloadmode', "-d",
                        default="api",
                        type=str,
                        choices=["api", "wget", "other"],
                        help='Mode to download the object. Default is api')
    parser.add_argument('--ccdb_host', "-H",
                        default="http://ali-qcdb-gpn.cern.ch:8083",
                        type=str,
                        help='Host to use for the CCDB fetch e.g. qcdb.cern.ch:8083 or http://ccdb-test.cern.ch:8080')
    parser.add_argument('--tag', '-T', action='store_true',
                        help='Flag to tag the output files with the timestamp')
    parser.add_argument('--show', '-s', action='store_true',
                        help='Flag to draw the output.')
    parser.add_argument('--runnumber', '-R',
                        default=None,
                        help='Run number to ask in the metadata. Can be used to download if in `wget` mode')
    parser.add_argument('--passname', '--pass', '-P',
                        default=None,
                        help='Pass to ask in the metadata. Can be used to download if in `wget` mode')
    parser.add_argument('--periodname', "--period", '-p',
                        default=None,
                        help='Period to ask in the metadata. Can be used to download if in `wget` mode')
    parser.add_argument('--useinputfile', "-I",
                        default=None,
                        type=str,
                        help='Input file name')

    args = parser.parse_args()
    set_verbose_mode(args)
    ccdb_path = args.ccdb_path
    ccdb_host = args.ccdb_host
    if "http://" in ccdb_path:
        ccdb_path = ccdb_path.split("/browse/")
        if len(ccdb_path) != 2:
            raise ValueError("cannot deduce host and path from",
                             args.ccdb_path, "does it have the '/browse/' string?")
        ccdb_host = ccdb_path[0]
        ccdb_path = ccdb_path[1]
        msg("Overriding host to", ccdb_host)

    meta_dict = None

    def do_meta_dict(var, name):
        global meta_dict
        if var is not None:
            if meta_dict is None:
                meta_dict = {}
            meta_dict[name] = var
    do_meta_dict(args.runnumber, "RunNumber")
    do_meta_dict(args.passname, "PeriodName")
    do_meta_dict(args.periodname, "PeriodName")
    if args.useinputfile is not None:
        fetchfromfile(args.useinputfile, ccdb_path, args)
    else:
        for i in args.timestamp:
            main(ccdb_path=ccdb_path,
                 out_path=args.out_path,
                 timestamp=i,
                 show=args.show,
                 tag=args.tag,
                 musthave_in_metadata=meta_dict,
                 download_mode=args.downloadmode,
                 host=ccdb_host)
