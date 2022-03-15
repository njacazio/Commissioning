#!/usr/bin/env python3

from shutil import ExecError
from jinja2 import Template, Environment, FileSystemLoader, StrictUndefined
import subprocess
import configparser
import os
from os import path
import argparse

jinjaEnv = Environment(loader=FileSystemLoader(searchpath="./templates/"),
                       undefined=StrictUndefined)

available_templates = []


def render_template_file(file_name,
                         template_data,
                         enable=True,
                         verbose=False):
    if file_name.endswith(".tex"):
        if file_name not in available_templates:
            raise ValueError(file_name, "not in", available_templates)
        available_templates.remove(file_name)
        for i in template_data:
            template_data[i] = template_data[i].replace(
                "_", "\\_").replace("\\\_", "\\_")
    if verbose:
        with open(path.join("./templates/", file_name), "r") as f:
            for i in f:
                i = i.strip()
                if len(i) == 0:
                    continue
                if i.startswith("%"):
                    continue
                j2_template = Template(i, undefined=StrictUndefined)
                l = j2_template.render(template_data)
                if verbose:
                    print(i)
                    print(l)
                lines.append(l)
    else:
        lines = jinjaEnv.get_template(file_name).render(template_data)
    out_file = ".".join(path.basename(file_name).split(".")[:-1])
    out_file = path.join("rendered",
                         out_file + "."+path.basename(file_name).split(".")[-1])
    with open(out_file, "w") as f:
        if not enable:
            f.write(f"% Disabled file from {file_name}\n")
        for i in lines.split("\n"):
            i = i.strip()
            f.write(f"{i}\n")


def main(configuration,
         periodname,
         passname,
         cfg_authors="configurations/authors.conf",
         main_path=None):
    global available_templates
    available_templates = []
    for i in os.listdir("templates/"):
        if not i.endswith(".tex"):
            continue
        available_templates.append(i)
    config_parser = configparser.RawConfigParser()
    # First set basic information
    if not path.isfile(cfg_authors):
        raise FileNotFoundError(cfg_authors)
    config_parser.read(cfg_authors)

    def make_name(n, c):
        if "." not in n:
            n = n[0]
        else:
            n = n.strip(".")
        return f"{n}.~{c}"
    presenter = make_name(config_parser.get("presenter", "name"),
                          config_parser.get("presenter", "cname"))
    presenterinstitute = ""
    config_parser.remove_section("presenter")
    authors = []
    institutes = []
    institutes_no_number = []
    for i in config_parser.sections():
        n = config_parser.get(i, "name")
        inst = config_parser.get(i, "institute")
        if inst not in institutes_no_number:
            institutes_no_number.append(inst)
        inst_index = institutes_no_number.index(inst) + 1
        a = f"{make_name(n, i)}$^{{({inst_index})}}$"
        if presenter in a:
            presenterinstitute = inst
            a = f"\\textcolor{{Black}}{{{a}}}"
        inst = f"({inst_index}) {inst}"
        if inst not in institutes:
            institutes.append(inst)
        authors.append(a)

    titletag = f"{periodname} {passname}".strip()
    data = {
        "passname": passname,
        "periodname": periodname,
        "authors": " ".join(authors).strip(),
        "presenter": presenter,
        "presenterinstitute": presenterinstitute,
        "institutes": " ".join(institutes).strip(),
        "titletag": titletag
    }
    render_template_file("title.tex", template_data=data)
    data = {"titletag": titletag}
    if main_path is not None:
        data["imagepath"] = path.join(main_path, periodname, passname)
    # Read running configuration
    config_parser.clear()
    config_parser.read(configuration)

    for i in config_parser.sections():
        print("Scanning section", i)
        sub_data = {}
        for j in config_parser[i]:
            o = config_parser.get(i, j)
            sub_data[j] = o
            # print("Getting", j, "for", i, ":", o)
            if j == "imagepath":
                sub_data[j] = path.join(sub_data[j], periodname, passname)
        for j in data:
            if j in sub_data:
                print("Overwriting", j, "for", i, ":", data[j])
            sub_data[j] = data[j]
        # print(sub_data)
        render_template_file(f"{i}.tex", template_data=sub_data)
    for i in available_templates:
        i = path.join("rendered", i)
        os.popen(f"rm {i}").read()
        os.popen(f"touch {i}").read()
    process = subprocess.Popen(
        "timeout 5 pdflatex tofqa.tex".split(" "), stdout=subprocess.PIPE)
    out, err = process.communicate()
    if err is not None or "LaTeX Error" in str(out):
        raise ExecError("Issue when running 'pdflatex tofqa.tex'"
                        "check tofqa.log")
    titletag.replace(" ", "_")
    os.rename("tofqa.pdf", f"final/TOF-QC_{titletag}.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configuration", "-c",
                        type=str, default="configurations/configuration.conf")
    parser.add_argument("--passname",
                        type=str, default="pass5_lowIR",
                        help="Pass to analyse")
    parser.add_argument("--periodname",
                        type=str, default="LHC15o",
                        help="Period to analyse")
    parser.add_argument("--mainpath", "-M",
                        type=str, default=None,
                        help="Path where to fetch the data")
    args = parser.parse_args()

    main(configuration=args.configuration,
         passname=args.passname,
         periodname=args.periodname,
         main_path=args.mainpath)
