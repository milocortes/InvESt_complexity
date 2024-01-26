#!/bin/bash
for i in {11..21}; do 
    anio=$((2000 + i))
    URL="https://www2.census.gov/programs-surveys/cbp/datasets/$anio/cbp"$i"msa.zip"
    wget $URL
    unzip *.zip
    rm *.zip
done
