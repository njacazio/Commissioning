From RUBEN on the 26th of Sept 2024

In principle, you can simply run $O2_ROOT/prodtests/sim_challenge.sh (run with -h to see available options).
Or, you can indeed run the AODProducer over some debug data, e.g. any subdirectory from https://alimonitor.cern.ch/raw/raw_details.jsp?timesel=0&filter_jobtype=LHC23zzh+-+apass4_test3_debug+-+Pb-Pb+5.36+TeV%2C+tests+for+PbPb+apass4+%28async-v1-01-08%29%2C+EPN%2C+O2-4970

The command will be e.g.

```
GLOSET="--shm-segment-size 24000000000 --hbfutils-config o2_tfidinfo.root,upstream --timeframes-rate-limit 3 --timeframes-rate-limit-ipcid 1 "
export DPL_REPORT_PROCESSING=1
o2-reader-driver-workflow $GLOSET | o2-aod-producer-workflow $GLOSET -b --run
```
executed in the folder with data copied from the alien.

You can also try with accessing data directly from the alien as e.g.

```
EXTPATH="alien:///alice/data/2023/LHC23zzh/544122/apass4_test3_debug_epn/0430/o2_ctf_run00544122_orbit0146990816_tf0000343118_epn136
GLOSET="--hbfutils-config ${EXTPATH}/o2_tfidinfo.root,upstream --shm-segment-size 24000000000  --timeframes-rate-limit 2 --timeframes-rate-limit-ipcid 1"
o2-reader-driver-workflow $GLOSET | o2-aod-producer-workflow $GLOSET --input-dir ${EXTPATH} -b --run
```

But sometimes root fails to extract large files from alien zipfiles, so this is not guaranteed to converge.


Standard workflow:

1. ./get_debug_production.sh
2. ./run_tof_matcher.sh
3. ./run_aod_making.sh
