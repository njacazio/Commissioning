#!/usr/bin/env python3

import os
import subprocess
mainpath = "aliceml:/tmp/pbpb/AnalysisResults/"
mainpath = "aliceml:tmp/pbpb/AnalysisResults/"
mainpath = "aliceml:tmp/900/TOFCALIB/"
mainfile = "AnalysisResults_trees_TOFCALIB.root"
tmpfile= "/tmp/downloadlist.sh"

os.makedirs("/tmp/toftrees/", exist_ok=True)
with open(tmpfile, "w") as f:
    for i in range(0, 100):
        cmd = "env -i scp " + mainpath + str(i) + "/" + mainfile + " /tmp/toftrees/{}".format(mainfile.replace(".root", "_{}.root".format(i)))
        cmd = "env -i rsync -u --progress " + mainpath + str(i) + "/" + mainfile + " /tmp/toftrees/{}".format(mainfile.replace(".root", "_{}.root".format(i)))
        f.write("{}\n".format(cmd))
        # print(cmd)
        # process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        # output, error = process.communicate()

print("Now run the following command:")
print("bash {}".format(tmpfile))