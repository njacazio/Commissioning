#!/bin/bash

ALIEN_PATH=/alice/data/2023/LHC23zzh/544122/apass4_test3_debug_epn/0430/o2_ctf_run00544122_orbit0146990816_tf0000343118_epn136

mkdir /tmp/debug_production
alien_cp $ALIEN_PATH/root_archive.zip file:/tmp/debug_production/

alien_cp $ALIEN_PATH/tofclusters.root file:/tmp/debug_production/

alien_cp $ALIEN_PATH/tpctracks.root file:/tmp/debug_production/
