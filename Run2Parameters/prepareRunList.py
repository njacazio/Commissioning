#!/usr/bin/env python3

# alien.py find /alice/data/ AO2D.root|awk '{print "alien://"$1}' >/tmp/lista.txt

def main(runlist="/tmp/lista.txt"):

    class Run:
        period = ""
        passname = ""
        year = 0
        run = 0

        def __init__(self, line):
            line = line.strip()
            r = line.replace("alien:///alice/data/", "").replace("ESDs/", "").replace("AODs/", "").split("/")
            # print(r)
            year = int(r[0])
            period = r[1]
            run = int(r[2])
            passname = r[3]
            passname = passname.split("_")[0]
            self.period = period
            self.passname = passname
            self.year = year
            self.run = run

        def __eq__(self, other):
            return self.period == other.period and self.passname == other.passname and self.year == other.year and self.run == other.run

        def __str__(self):
            return f"Year {self.year} period {self.period} run {self.run} pass {self.passname}"

        def __repr__(self):
            return "\n" + self.__str__()

        def __hash__(self):
            return hash((self.period, self.passname, self.year, self.run))

        def save(self):
            return f"{self.year}/{self.period}/{self.run}/{self.passname}" + "\n"
    runs = []
    dicthash = {}
    with open(runlist) as f:
        lines = f.readlines()
        n = 0
        ntot = len(lines)
        print(f"Reading {runlist} of {ntot} lines")
        for line in lines:
            # print(line)
            r = Run(line)
            n += 1
            if r.passname == "offlineclusters":
                continue
            if r in dicthash:
                continue
            if r in runs:
                continue
            dicthash[r] = r
            runs.append(r)
            print(n, "/", ntot, r)

    with open("/tmp/runlist.txt", "w") as f:
        for i in runs:
            f.write(i.save())

    per_year = {}
    per_periods = {}
    per_pass = {}
    per_run = {}
    for i in runs:
        per_year.setdefault(i.year, []).append(i)
        per_periods.setdefault(i.period, []).append(i)
        per_pass.setdefault(i.passname, []).append(i)
        per_run.setdefault(i.run, []).append(i)
    print("Years", per_year.keys())
    print("Periods", per_periods.keys())
    print("Passes", per_pass.keys())
    print("Runs", per_run.keys())
    for i in per_run:
        if len(per_run[i]) == 1:
            continue
        passnames = ""
        for j in per_run[i]:
            passnames += j.passname + "-"
        passnames = passnames.strip("-")
        print(i, per_run[i])
        per_run[i][0].passname = passnames
        per_run[i] = [per_run[i][0]]

    with open("/tmp/perrun.txt", "w") as f:
        for i in per_run.values():
            if len(i) > 1:
                raise ValueError("More than one run")
            f.write(i[0].save())


# main()
main("/tmp/runlist.txt")
