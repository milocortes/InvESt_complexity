#!/bin/bash
wget https://www.census.gov/naics/concordances/ISIC_4_to_2017_NAICS.xlsx
wget https://www.census.gov/naics/concordances/ISIC_Rev_4_to_2022_NAICS.xlsx
wget https://www.census.gov/naics/concordances/2012%20NAICS_to_ISIC_4.xlsx
wget https://www.census.gov/naics/concordances/2017_to_2012_NAICS_Changes_Only.xlsx

mv *.xlsx datos/
