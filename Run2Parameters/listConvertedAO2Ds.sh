#!/bin/bash

Years=(2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020)
Years=(2018 2019 2020)

# rm /tmp/lista.txt

for i in "${Years[@]}"; do
    echo Listing year $i
    alien.py find /alice/data/$i AO2D.root | awk '{print "alien://"$1}' >>/tmp/lista.txt
done
