## ASYNCH QC: RETRIEVE OBJECTS FROM CCDB

1. Have a file called jiraticket.txt with the content of the Jira 
exmple for LHC22s pass4: 

"529397 - 1670222350246 - 05 Dec 2022 06:39 UTC - 05 Dec 2022 07:39 CET
529399 - 1670222684103 - 05 Dec 2022 06:44 UTC - 05 Dec 2022 07:44 CET
529403 - 1670222410643 - 05 Dec 2022 06:40 UTC - 05 Dec 2022 07:40 CET
529414 - 1670224443524 - 05 Dec 2022 07:14 UTC - 05 Dec 2022 08:14 CET
529418 - 1670223324479 - 05 Dec 2022 06:55 UTC - 05 Dec 2022 07:55 CET"

2. run the script runQCasynch.sh as follows:
>> . runQCasynch.sh LHC22s apass4

3. The script will create a folder for each run number with the rootfiles